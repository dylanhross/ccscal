

from CcsCal import globals


from os.path import splitext, exists
from numpy import genfromtxt, zeros, abs
from subprocess import run


class RawData:

    def __init__ (self, data_filename, specified_mass, mass_window, pp=True):
        """
RawData.__init__

Initializes a new RawData object

Input(s):
    data_filename       - file name of the raw data file (string)
    specified_mass      - mass to extract data for (float)
    mass_window         - window of masses to bin data together for (float)
    [pp                 - whether to pre-process the text file (bool), optional default=True]
"""
        if pp:
            # create the pre-processed data file
            self.callPreProcessTxt(data_filename, specified_mass, mass_window)
            # store the file name of the pre-processed file
            self.ppFileName = splitext(data_filename)[0] + ".pp-" + str(specified_mass) + ".txt"
            # check if pre-processing was successful
            if not exists(self.ppFileName):
                raise RuntimeError("pre-processing for file " + data_filename + " failed!")
            # generate an array with the mass, dtbin, and intensity values from the pre-processed
            # data file
            self.data = genfromtxt(self.ppFileName, unpack=True)
        else:
            self.data = genfromtxt(data_filename, unpack=True)
        # this is set by fineFilterForMass
        self.dtBinAndIntensity = None
        # fine filter extracted data for mass and mass window
        self.fineFilterForMass(specified_mass, mass_window)
        # store the specified mass
        self.specifiedMass = specified_mass


    def callPreProcessTxt(self, data_filename, specified_mass, mass_window):
        """
RawData.callPreProcessTxt

Calls PreProcessTxt.o (or PreProcessTxt.exe on Windows) using the specified mass and mass window
provided as parameters. The mass window it actually uses is a rough mass window (i.e. double the
mass window provided)

*** This function is not very portable, needs some major improvements ***

Input(s):
    data_filename       - file name of the raw data file (string)
    specified_mass      - mass to extract data for (float)
    mass_window         - window of masses to bin data together for (float)
"""
        # pre-process data with rough mass_window (i.e. double the original mass window)
        useWindow = globals.PP_MASS_WIN_SCALE * mass_window
        # generate this string for logging purposes, but it isn't used for the actual
        # function call
        functionCallLine = globals.PP_EXE_PATH + " " +\
                            data_filename + " " +\
                            str(specified_mass) + " " + \
                            str(useWindow)
        # had to use shell=True flag here... not sure if I had to do that with RawToTxt
        # but eventually I may need to figure something else out since I am sure sure how
        # well it will work with this flag on Windows.
        print("\tCalling PreProcessTxt.exe...")
        print("\t~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print("\t" + functionCallLine)
        print("\t~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        # NOTE: call the executable with each of the params as separate args, this way we do not
        #       need the shell=True flag. Still haven't quite fixed the portability issue though.
        run(globals.PP_EXE_PATH, data_filename, specified_mass, mass_window)
        print("\t...Done\n")


    def fineFilterForMass(self, specified_mass, mass_window):
        """
RawData.fineFilterForMass

Looks through the data array from the pre-processed data file for masses within the
fine mass window, uses a zeroed 2D array to deal with possibly sparse input data

Input(s):
    specified_mass      - mass to extract data for (float)
    mass_window         - window of masses to bin data together for (float)
"""
        # prepare an array with dtbin and intensity values
        self.dtBinAndIntensity = zeros([2, 200])
        for n in range(1, 201):
            self.dtBinAndIntensity[0][n - 1] = n
        for n in range(len(self.data[0])):
            if abs(specified_mass - self.data[0][n]) <= mass_window:
                # add the intensity to its corresponding bin
                self.dtBinAndIntensity[1][int(self.data[1][n]) - 1] += self.data[2][n]
