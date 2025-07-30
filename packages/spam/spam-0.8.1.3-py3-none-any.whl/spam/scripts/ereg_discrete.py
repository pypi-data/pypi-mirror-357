# This python facilitates eye-alignment with a graphical QT interface
# for Discrete Digital Image Correlation using SPAM functions
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

import argparse
import os

import numpy
import spam.helpers
import spam.label
import spam.visual.visualClass as visual
import tifffile
from PyQt5.QtWidgets import QApplication, QGridLayout, QPushButton, QWidget

numpy.seterr(all="ignore")


def eregDiscreteParser(parser):
    parser.add_argument(
        "im1",
        metavar="im1",
        type=argparse.FileType("r"),
        help="Greyscale image of reference state for correlation",
    )

    parser.add_argument(
        "lab1",
        metavar="lab1",
        type=argparse.FileType("r"),
        help="Labelled image of reference state for correlation",
    )

    parser.add_argument(
        "im2",
        metavar="im2",
        type=argparse.FileType("r"),
        help="Greyscale image of deformed state for correlation",
    )

    parser.add_argument(
        "-mar",
        "--margin",
        type=int,
        default=5,
        dest="margin",
        help="Margin in pixels. Default = 5",
    )

    parser.add_argument(
        "-rst",
        "--return-status-threshold",
        type=int,
        default=2,
        dest="RETURN_STATUS_THRESHOLD",
        help="Skip labels already correlated with at least this return status (requires -pf obviously). Default = 2",
    )

    parser.add_argument(
        "-ld",
        "--label-dilate",
        type=int,
        default=1,
        dest="LABEL_DILATE",
        help="Number of times to dilate labels. Default = 1",
    )

    parser.add_argument(
        "-pf",
        "-phiFile",
        dest="PHIFILE",
        default=None,
        type=argparse.FileType("r"),
        help="Path to TSV file containing initial Phi guess for each label. Default = None",
    )

    parser.add_argument(
        "-nomask",
        "--no-mask",
        action="store_false",
        dest="MASK",
        help="Don't mask each label's image",
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
        "-pre",
        "--prefix",
        type=str,
        default=None,
        dest="PREFIX",
        help="Prefix for output files (without extension). Default is basename of input file",
    )

    parser.add_argument(
        "-maskconv",
        "--mask-converged",
        action="store_true",
        dest="MASK_CONV",
        help="Mask the converge labels from the deformed greyscale",
    )

    args = parser.parse_args()

    # If we have no out dir specified, deliver on our default promise -- this can't be done inline before since parser.parse_args() has not been run at that stage.
    if args.OUT_DIR is None:
        args.OUT_DIR = os.path.dirname(args.im1.name)
        # However if we have no dir, notice this and make it the current directory.
        if args.OUT_DIR == "":
            args.OUT_DIR = "./"
    else:
        # Check existence of output directory
        try:
            if args.OUT_DIR:
                os.makedirs(args.OUT_DIR)
            else:
                args.DIR_out = os.path.dirname(args.im1.name)
        except OSError:
            if not os.path.isdir(args.OUT_DIR):
                raise

    # Output file name prefix
    if args.PREFIX is None:
        args.PREFIX = os.path.splitext(os.path.basename(args.im1.name))[0] + "-" + os.path.splitext(os.path.basename(args.im2.name))[0]

    return args


def script():
    # Define argument parser object
    parser = argparse.ArgumentParser(
        description="spam-ereg-discrete "
        + spam.helpers.optionsParser.GLPv3descriptionHeader
        + "This script facilitates eye-alignment for Discrete Digital Image Correlation two 3D greyscale images"
        + " (reference and deformed configurations) and requires the input of a labelled image for the reference configuration",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    # Parse arguments with external helper function
    args = eregDiscreteParser(parser)

    spam.helpers.displaySettings(args, "spam-ereg-discrete")

    print("spam-ereg-discrete: Current Settings:")
    
    outFile = args.OUT_DIR + "/" + args.PREFIX + "-ereg-discrete.tsv"

    REFlab = tifffile.imread(args.lab1.name)
    REFlabBB = spam.label.boundingBoxes(REFlab)
    REFlabCOM = spam.label.centresOfMass(REFlab)

    REFgrey = tifffile.imread(args.im1.name)
    DEFgrey = tifffile.imread(args.im2.name)

    # Some variable for nice filenames
    REFstr = os.path.basename(args.im1.name)
    DEFstr = os.path.basename(args.im2.name)

    if args.PHIFILE is not None:
        DDIC = spam.helpers.readCorrelationTSV(args.PHIFILE.name, readConvergence=True)
        DDIC["error"] = numpy.genfromtxt(args.PHIFILE.name, delimiter="\t", names=True)["error"]
        try:
            DDIC["LabelDilate"] = numpy.genfromtxt(args.PHIFILE.name, delimiter="\t", names=True)["LabelDilate"]
        except:
            DDIC["LabelDilate"] = numpy.zeros(DDIC["error"].shape[0])
        try:
            DDIC["PSCC"] = numpy.genfromtxt(args.PHIFILE.name, delimiter="\t", names=True)["PSCC"]
        except:
            DDIC["PSCC"] = numpy.zeros(DDIC["error"].shape[0])

        # 09-12-21 GP: Adding the mask for converge particles
        if args.MASK_CONV:
            print("Moving image")
            REFlabMoved = spam.label.moveLabels(REFlab, DDIC["PhiField"], returnStatus=DDIC["returnStatus"])
            DEFgrey = numpy.where(REFlabMoved > 0, 0, DEFgrey)

    else:
        labMax = REFlab.max()
        DDIC = {}
        DDIC["fieldCoords"] = REFlabCOM
        DDIC["PhiField"] = numpy.zeros([labMax, 4, 4])
        for label in range(labMax):
            DDIC["PhiField"][label] = numpy.eye(4)
        DDIC["returnStatus"] = numpy.zeros(labMax, dtype=int)
        DDIC["deltaPhiNorm"] = numpy.zeros(labMax, dtype=int)
        DDIC["iterations"] = numpy.zeros(labMax, dtype=int)
        DDIC["error"] = numpy.zeros(labMax, dtype=int)
        DDIC["LabelDilate"] = numpy.zeros(labMax, dtype=int)
        DDIC["PSCC"] = numpy.zeros(labMax, dtype=int)

    class MainWindow(QWidget):
        def __init__(self):
            QWidget.__init__(self)
            self.Phi = numpy.eye(4)
            self.mainWindowGrid = QGridLayout(self)

            # Issue #192 will be fixed here, by making sure the loew return stat list also has real boundin boxes
            #   (i.e., grains are really defined)
            nonConvergedGrains = DDIC["returnStatus"][0 : REFlabBB.shape[0]] < args.RETURN_STATUS_THRESHOLD
            presentGrains = REFlabBB[:, 1] > REFlabBB[:, 0]
            # In the very unlucky case that there is a nax numbered nonConverged grain that is not present at all:
            if REFlabBB.shape[0] < len(nonConvergedGrains):
                print("Warning: there are higher-numbered labels in your TSV file that are not in the labelled image, discarding them")

            print(numpy.where(nonConvergedGrains), presentGrains)
            self.nonConvergedGrains = numpy.where(numpy.logical_and(nonConvergedGrains, presentGrains))[0][0:]

            self.N = 0  # Number of the current nonConvergedGrain that's being studied
            print("Going to work on these labels:\n", self.nonConvergedGrains, "(p.s. I removed non-existent labels:", numpy.where(~presentGrains)[0][1:], " )")
            if len(self.nonConvergedGrains) > 0:
                self.labAndPhi = []
                self.labelExists = False
                self.alignOneLabel()
            else:
                print("No labels to work on")
                exit()

        def alignOneLabel(self):
            nonConvergedGrain = self.nonConvergedGrains[self.N]

            print("\tGrain {}".format(nonConvergedGrain))
            print("\t\tPosition in reference image: {}".format(REFlabCOM[nonConvergedGrain]))

            Phi = DDIC["PhiField"][nonConvergedGrain]

            displacement = Phi[0:3, -1]
            displacementInt = displacement.astype(int)
            self.diplacementInt = displacementInt
            # Remove the int part of displacement
            Phi[0:3, -1] -= displacementInt
            print("\t\tSubtracted this displacement:", displacementInt)

            REFgl = spam.label.getLabel(REFlab, nonConvergedGrain, boundingBoxes=REFlabBB, centresOfMass=REFlabCOM, labelDilate=args.LABEL_DILATE, margin=args.margin, maskOtherLabels=args.MASK)

            if REFgl is not None:
                self.labelExists = True
                # 2020-10-23: EA on Issue #186: using spam.helpers.slicePadded
                REFsubvol = spam.helpers.slicePadded(REFgrey, REFgl["boundingBox"] + numpy.array([0, 1, 0, 1, 0, 1]))

                if args.MASK:
                    # If mask asked, also flatten greylevels
                    REFsubvol[REFgl["subvol"] == 0] = 0

                # 2020-10-23: EA on Issue #186: using spam.helpers.slicePadded
                DEFsubvol = spam.helpers.slicePadded(
                    DEFgrey,
                    REFgl["boundingBox"]
                    + numpy.array([0, 1, 0, 1, 0, 1])
                    + numpy.array([displacementInt[0], displacementInt[0], displacementInt[1], displacementInt[1], displacementInt[2], displacementInt[2]]),
                )

                self.eregWidget = visual.ereg([REFsubvol, DEFsubvol], Phi, [f"{REFstr} - label {nonConvergedGrain}", f"{DEFstr} - label {nonConvergedGrain}"], binning=1, imUpdate=0)
                self.mainWindowGrid.addWidget(self.eregWidget, 1, 1)
                self.nextLabelButton = QPushButton("Accept and move on to next grain", self)
                self.nextLabelButton.clicked.connect(self.nextLabel)
                self.mainWindowGrid.addWidget(self.nextLabelButton, 2, 1)
            else:
                # print('alignOneGrain(): warning refgl is none')
                self.labelExists = False
                self.nextLabel()

        def nextLabel(self):
            # print("Entering nextLabel(): self.labelExists = ", self.labelExists)
            if self.labelExists:
                self.eregWidget.close()

                # Get Phi output from graphical
                PhiTmp = self.eregWidget.output()
                # Add back in int displacement
                PhiTmp[0:3, -1] += self.diplacementInt
                #                       nonConvergedGrain label number, eye-Phi
                self.labAndPhi.append([self.nonConvergedGrains[self.N], PhiTmp])
                print("nextLabel: I accepted a Phi for label {}".format([self.nonConvergedGrains[self.N]]))
            else:
                print("nextLabel: I skipped label {}".format([self.nonConvergedGrains[self.N]]))
                # This grain was skipped, let's add nothing in its place
                self.labAndPhi.append([self.nonConvergedGrains[self.N], numpy.eye(4)])

            # Move onto next grain, otherwise write and quit
            self.N += 1
            if self.N < len(self.nonConvergedGrains):
                self.alignOneLabel()
            else:
                self.nextLabelButton.close()
                self.eregWidget.close()
                # print(self.labAndPhi)

                print("Updating output...")
                for nonConvergedGrain, Phi in self.labAndPhi:
                    DDIC["PhiField"][nonConvergedGrain] = Phi

                print("Writing output to {}...".format(outFile), end="")
                outMatrix = numpy.array(
                    [
                        numpy.array(range(DDIC["numberOfLabels"])),
                        DDIC["fieldCoords"][:, 0],
                        DDIC["fieldCoords"][:, 1],
                        DDIC["fieldCoords"][:, 2],
                        DDIC["PhiField"][:, 0, 3],
                        DDIC["PhiField"][:, 1, 3],
                        DDIC["PhiField"][:, 2, 3],
                        DDIC["PhiField"][:, 0, 0],
                        DDIC["PhiField"][:, 0, 1],
                        DDIC["PhiField"][:, 0, 2],
                        DDIC["PhiField"][:, 1, 0],
                        DDIC["PhiField"][:, 1, 1],
                        DDIC["PhiField"][:, 1, 2],
                        DDIC["PhiField"][:, 2, 0],
                        DDIC["PhiField"][:, 2, 1],
                        DDIC["PhiField"][:, 2, 2],
                        DDIC["error"],
                        DDIC["iterations"],
                        DDIC["returnStatus"],
                        DDIC["deltaPhiNorm"],
                        DDIC["LabelDilate"],
                        DDIC["PSCC"],
                    ]
                ).T

                numpy.savetxt(
                    outFile,
                    outMatrix,
                    fmt="%.7f",
                    delimiter="\t",
                    newline="\n",
                    comments="",
                    header="Label\tZpos\tYpos\tXpos\t"
                    + "Zdisp\tYdisp\tXdisp\t"
                    + "Fzz\tFzy\tFzx\t"
                    + "Fyz\tFyy\tFyx\t"
                    + "Fxz\tFxy\tFxx\t"
                    + "error\titerations\treturnStatus\tdeltaPhiNorm\tLabelDilate\tPSCC",
                )
                print("...done")
                self.close()
                # self.mainWindowGrid.close()

    app = QApplication(["Label Registration"])
    window = MainWindow()
    window.show()
    app.exec_()
