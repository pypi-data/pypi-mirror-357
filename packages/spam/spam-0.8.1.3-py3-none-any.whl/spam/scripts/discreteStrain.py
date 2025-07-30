# This python computes strains from particle displacements using SPAM functions
# Copyright (C) 2020 SPAM Contributors
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.


"""
This script calculates strains in a granular assembly using Bagi's strain tesselation technique.
This means that at the fundamental level, strains are calculated on space-filling tetrahedra that
  connect four grain centres.
Tesselations can either be provided or calculated within the script.

The strains defined on tetrahedra can either be output as-are, or processed further,
either projected back to grains (whereby the value at each grain is a weighted local average
  and NOT the strain of the grain itself).
...or projected onto a regular grid.
"""

import os

import spam.deformation
import spam.DIC
import spam.helpers
import spam.label
import spam.mesh

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"

import argparse  # noqa: E402

import numpy  # noqa: E402

numpy.seterr(all="ignore")

import multiprocessing  # noqa: E402

try:
    multiprocessing.set_start_method("fork")
except RuntimeError:
    pass


def discreteStrainsCalcParser(parser):
    parser.add_argument(
        "inFile",
        metavar="inFile",
        type=argparse.FileType("r"),
        help="Path to TSV file containing the result of the correlation",
    )

    parser.add_argument(
        "-comp",
        "--strain-components",
        nargs="*",
        type=str,
        default=["vol", "dev"],
        dest="COMPONENTS",
        help="Selection of which strain components to save, options are: vol (volumetric strain), dev (deviatoric strain),\
              volss (volumetric strain in small strains), devss (deviatoric strain in small strains),\
              r (rotation vector), z (zoom vector), U (right-hand stretch tensor), e (strain tensor in small strains)",
    )

    parser.add_argument(
        "-np",
        "--number-of-processes",
        default=None,
        type=int,
        dest="PROCESSES",
        help="Number of parallel processes to use. Default = multiprocessing.cpu_count()",
    )

    parser.add_argument(
        "-od",
        "--out-dir",
        type=str,
        default=None,
        dest="OUT_DIR",
        help="Output directory, default is the dirname of input file",
    )

    parser.add_argument(
        "-tri",
        "--perform-triangulation",
        action="store_true",
        dest="TRI",
        help="Perform triangulation of grain centres?",
    )

    parser.add_argument(
        "-a",
        "-triangulation-alpha-value",
        type=float,
        default=0.0,
        dest="TRI_ALPHA",
        help="CGAL Alpha value for triangulation cleanup (negative = auto, zero = no cleanup, positive = userval). Default = 0",
    )

    parser.add_argument(
        "-tf",
        "--triangulation-file",
        type=str,
        default=None,
        dest="TRI_FILE",
        help="Load a triangulation from file? This should be a TSV with just lines with three numbers corresponding to the connectivity matrix\
             (e.g., output from numpy.savetxt())",
    )

    parser.add_argument(
        "-rf",
        "--radius-file",
        type=str,
        default=None,
        dest="RADII_TSV_FILE",
        help="Load a series of particle radii from file? Only necessary if -tri is activated",
    )

    parser.add_argument(
        "-rl",
        "--radii-from-labelled",
        type=str,
        default=None,
        dest="RADII_LABELLED_FILE",
        help="Load a labelled image and compute radii? Only necessary if -tri is activated",
    )

    parser.add_argument(
        "-rst",
        "--return-status-threshold",
        type=int,
        default=None,
        dest="RETURN_STATUS_THRESHOLD",
        help="Lowest return status value to preserve in the triangulation. Default = 2",
    )

    parser.add_argument(
        "-pre",
        "--prefix",
        type=str,
        default=None,
        dest="PREFIX",
        help="Prefix for output files (without extension). Default is basename of input file",
    )

    # parser.add_argument('-nos',
    # '--not-only-strain',
    # action="store_true",
    # dest='NOT_ONLY_STRAIN',
    # help='Return all the output matrices. Default = True')

    parser.add_argument(
        "-pg",
        "--project-to-grains",
        action="store_true",
        dest="PROJECT_TO_GRAINS",
        help="Also project strain components to grains? This gives a neighbourhood average expressed at the grain (and not the deformation of the grain itself)",
    )

    parser.add_argument(
        "-kz",
        "--keep-zero",
        action="store_true",
        dest="KEEP_ZERO",
        help="Consider grain number zero? Only affects TSV files. Default = False",
    )

    # parser.add_argument('-vtk',
    # '--VTKout',
    # action="store_false",
    # dest='VTK',
    # help='Activate VTK output format. Default = True')

    parser.add_argument(
        "-vtkln",
        "--VTKleaveNANs",
        action="store_false",
        dest="VTKmaskNAN",
        help="Leave NaNs in VTK output? If this option is not set they are replaced with 0.0",
    )

    args = parser.parse_args()

    # If we have no out dir specified, deliver on our default promise -- this can't be done inline before since parser.parse_args() has not been run at that stage.
    if args.OUT_DIR is None:
        args.OUT_DIR = os.path.dirname(args.inFile.name)
        # However if we have no dir, notice this and make it the current directory.
        if args.OUT_DIR == "":
            args.OUT_DIR = "./"
    else:
        # Check existence of output directory
        try:
            if args.OUT_DIR:
                os.makedirs(args.OUT_DIR)
            else:
                args.DIR_out = os.path.dirname(args.lab1.name)
        except OSError:
            if not os.path.isdir(args.OUT_DIR):
                raise
    # Output file name prefix
    if args.PREFIX is None:
        args.PREFIX = os.path.splitext(os.path.basename(args.inFile.name))[0] + "-strains"

    return args


def script():
    # Define argument parser object
    parser = argparse.ArgumentParser(
        description="spam-discreteStrain "
        + spam.helpers.optionsParser.GLPv3descriptionHeader
        + "This script computes different components of strain, given an irregularly-spaced displacement"
        + " field for a granular system, such as the output from spam-ddic."
        + " The Zhang (2015) framework, which extends Bagi (1996) is used for the computation",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    # Parse arguments with external helper function
    args = discreteStrainsCalcParser(parser)

    # This option skips the kinematics of particle zero in the kinematics file that will be read,
    #   since when working with labelled images particle zero is the background and `spam-ddic` does
    #   not correlate it (and in its output files there is a "blank" particle zero to be ignored).
    if args.KEEP_ZERO:
        start = 0
    else:
        start = 1

    # Check the strain mode, set as default large strains
    # largeStrains = True
    # if args.SMALL_STRAINS:
    # largeStrains = False

    # Figure out processes if not passed
    if args.PROCESSES is None:
        args.PROCESSES = multiprocessing.cpu_count()

    spam.helpers.displaySettings(args, "spam-discreteStrain")

    # Something needs to set this to true
    triangulationAvailable = False

    print("\nspam-discreteStrain: Loading kinematics...")
    if args.inFile.name[-3::] == "tsv":
        if args.RETURN_STATUS_THRESHOLD is not None:
            TSV = spam.helpers.readCorrelationTSV(args.inFile.name, readOnlyDisplacements=True, readConvergence=True)
            returnStat = TSV["returnStatus"][start:]
        else:
            # We don't care about return status (this is normally a home-made TSV)
            TSV = spam.helpers.readCorrelationTSV(args.inFile.name, readOnlyDisplacements=True, readConvergence=False)
        # dims = TSV["numberOfLabels"]-start
        points = TSV["fieldCoords"][start:]
        displacements = TSV["displacements"][start:]
        # print(points.shape, displacements.shape)
        try:
            radii = TSV["radius"][start::]
        except BaseException:
            radii = None
        del TSV

    elif args.inFile.name[-3::] == "vtk":
        VTK = spam.helpers.readUnstructuredVTK(args.inFile.name)
        if args.RETURN_STATUS_THRESHOLD is not None:
            returnStat = VTK["returnStatus"]
        # dims = VTK[0].shape[0]
        points = VTK[0].copy()
        displacements = VTK[2]["displacements"]
        connectivity = VTK[1].copy()
        # This is an untested guess
        triangulationAvailable = True
        try:
            radii = VTK[2]["radius"]
        except BaseException:
            radii = None
        del VTK
    else:
        print("\nspam-discreteStrain: Don't recognise this input kinematics file -- it should be a file from spam-ddic")

    # ### 2019-10-14 EA: Attempt to catch undesirable return statuses.
    # HACK: Set the failing particles positions to NaN
    if args.RETURN_STATUS_THRESHOLD is not None:
        points[returnStat < args.RETURN_STATUS_THRESHOLD] = numpy.nan

    # ### 2020-03-23 EA and OS, nan mask for safety
    # mask = numpy.sum(numpy.isnan(points), axis=1) > 0

    # Apparently we cannot read the VTK files we write with spam-ddic
    # If someone saves a proper VTK with a triangulation it should have bene loaded above,
    #   but just in case different files are used...
    if args.TRI_FILE is not None:
        if args.TRI_FILE[-3::] == "vtk":
            # print("\nspam-discreteStrain: I've read this file already I think")
            VTK = spam.helpers.readUnstructuredVTK(args.TRI_FILE)
            connectivity = VTK[1].copy().astype(numpy.uint)
            triangulationAvailable = True
            del VTK

        elif args.TRI_FILE[-3::] == "tsv":
            connectivity = numpy.genfromtxt(args.TRI_FILE).astype(numpy.uint)
            triangulationAvailable = True
        else:
            print("\nspam-discreteStrain: Don't recognise this input triangulation file -- it should be a file from spam-ddic")

    # Should we compute a triangulation?
    if args.TRI and not triangulationAvailable:
        # Look for some weights to pass to triangulate
        if args.RADII_TSV_FILE is not None:
            radii = numpy.loadtxt(args.RADII_TSV_FILE)[start::]

        if args.RADII_LABELLED_FILE is not None:
            import tifffile

            radii = spam.label.equivalentRadii(tifffile.imread(args.RADII_LABELLED_FILE))[start::]

        # Run the triangulation whether we have radii or not
        weights = radii**2.0 if radii is not None else None
        connectivity = spam.mesh.triangulate(points, weights=weights, alpha=args.TRI_ALPHA)
        print("\nspam-discreteStrain: {} tetrahedra created".format(connectivity.shape[0]))
        print("spam-discreteStrain: {} nodes considered".format(len(numpy.unique(connectivity.ravel()))))
        triangulationAvailable = True

    # else:
    # print("spam-discreteStrain: Input file extension not recognised, please give me VTK or TSV from spam-ddic")
    # exit()

    # If nobody set this to true, we're in big trouble
    if not triangulationAvailable:
        print("\nspam-discreteStrain: No triangulation available, either set -tri to compute it or pass a triangulation file with -tf")
        exit()

    # nans in COM?
    # nanmask = numpy.isfinite(points[:,0])

    # Compute bagi strains with initial and deformed centres of mass.
    # print("\nStart strain calculation...")
    # We'll do this with "onlyStrains=False" in case we need to project F (and R?) to grains

    # ### 2019-10-06 EA: Remove bad lines from connectivity, to make valid VTK
    # goodTets = numpy.ones(connectivity.shape[0], dtype=bool)
    # for n, tet in enumerate(connectivity):
    # ### If a bad tet:
    # if numpy.any(tet >= points.shape[0]):
    # goodTets[n] = 0
    # else:
    # if numpy.isfinite(points[tet]).sum() != 12 or numpy.isfinite(displacements[tet]).sum() != 12:
    # goodTets[n] = 0
    # connectivity = connectivity[goodTets]

    print("spam-discreteStrain: Computing F=I+du/dx for all tetrahedra")
    Ffield = spam.deformation.FfieldBagi(points, connectivity, displacements, verbose=True, nProcesses=args.PROCESSES)
    # strainMatrix, F, R, volStrain, devStrain = spam.deformation.FfieldBagi(points, connectivity, displacements, onlyStrain=False)

    # Compute bagi strains with initial and deformed centres of mass.
    if args.PROJECT_TO_GRAINS:
        print("\nspam-discreteStrain: Projecting strain field onto the grains...")

        # We need to project F, since it is in ZYX, U is in the eigendirections and cannot be summed.
        Fgrains = spam.mesh.projectTetFieldToGrains(points + displacements, connectivity, Ffield)

        decomposedFfield = spam.deformation.decomposeFfield(Fgrains, args.COMPONENTS, twoD=False, verbose=True, nProcesses=args.PROCESSES)

        spam.helpers.writeStrainTSV(
            args.OUT_DIR + "/" + args.PREFIX + "-grainProjection.tsv",
            points,
            decomposedFfield,
            firstColumn="Label",
            startRow=start,
        )
        # The VTK information will be added to the VTK at the end of the function.

    print("\nspam-discreteStrain: Decomposing F into ", args.COMPONENTS, "for all tetrahedra")
    decomposedFfield = spam.deformation.decomposeFfield(Ffield, args.COMPONENTS, twoD=False, verbose=True, nProcesses=args.PROCESSES)

    # if args.VTK:
    print("\nspam-discreteStrain: Saving VTK strain fields...", end="")
    cellData = {}
    for component in args.COMPONENTS:
        tmp = decomposedFfield[component]
        if args.VTKmaskNAN:
            tmp[numpy.isnan(tmp)] = 0.0
        # As of 2020-03-11 meshio only supports 2D fields with unstructured grids
        if component == "e" or component == "U":
            tmp = tmp.reshape(tmp.shape[0], 9)
        cellData[component] = tmp
    spam.helpers.writeUnstructuredVTK(
        points,
        connectivity,
        cellData=cellData,
        pointData={"displacements": displacements},
        fileName=args.OUT_DIR + "/" + args.PREFIX + ".vtk",
    )
    print("done.")

    # print("\nspam-discreteStrain: Saving TSV strain fields...", end='')
    # spam.helpers.writeStrainTSV(args.OUT_DIR+"/"+args.PREFIX+".tsv",
    # points, decomposedFfield, firstColumn="TetNumber", startRow=0)
    # print("done.")
