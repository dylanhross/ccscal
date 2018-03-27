"""
"""


from numpy import genfromtxt, array


class ParseInputFile:

    def __init__(self, input_filename):
        # take in the input parameters
        self.rawData = self.getInputParams(input_filename)
        # unpack the single parameters into easy to access fields
        self.unpackSingleParams()
        # create arrays with the list input parameters
        self.unpackListParams()


    def getInputParams(self, filename):
        """
ParseInputFile.getInputParams

Searches through the specified input file for the (all) parameters and returns an
array of the parameters grouped by categories (general, calibrants, and compounds):

params contents by index:
    params[0][0]            - path and file name to save reoprt under
    params[0][1]            - mass window to extract drift time data from
    params[0][2]            - edc parameter
    params[0][3]            - TOF pusher interval
    params[0][4]            - Savitsky-Golay smooth window
    params[0][5]            - Savitsky-Golay smooth polynomial order
    params[1][0]            - full path and name to save calibration curve file under
    params[1][1]            - full path and name of the CCS calibration data file
    params[2][0]            - full path to the directory containing the compound data files
    params[3]               - array containing the list data (calibrant masses and lit ccs
                                values, compound data file names and masses)

### TODO:   FIX THIS CRAP, this system is terrible because it breaks if any of the
###         keywords are omitted or out of order

Input(s):
    filename            - file name (and full path to) CcsCalInput file (string)

Returns:
    params              - an array (list of three lists and one numpy.array() object)
                                containing the parameters from the input file
"""
        ### TODO:   FIX THIS CRAP, this system is terrible because it breaks if any of the
        ###         keywords are omitted
        params = [[],[],[]]
        with open(filename) as input:
            done = False
            for line in input:
                if not done:
                    if line.split()[0] == ";rfn":
                        params[0].append(line.split()[2])
                    elif line.split()[0] == ";mwn":
                        params[0].append(line.split()[2])
                    elif line.split()[0] == ";edc":
                        params[0].append(line.split()[2])
                    elif line.split()[0] == ";tpi":
                        params[0].append(line.split()[2])
                    elif line.split()[0] == ";sgw":
                        params[0].append(line.split()[2])
                    elif line.split()[0] == ";sgp":
                        params[0].append(line.split()[2])
                    elif line.split()[0] == ";cff":
                        params[1].append(line.split()[2])
                    elif line.split()[0] == ";cdf":
                        params[1].append(line.split()[2])
                    elif line.split()[0] == ";crd":
                        params[2].append(line.split()[2])
                        done = True
                else:
                    break
        params.append(genfromtxt(filename, dtype=str, comments=";"))
        return params


    def unpackSingleParams(self):
        """
ParseInputFile.unpackSingleParams

Unpack the paramters from the params array into fields with names that make sense for easy
access from the main execution. Cast the values into the proper types that they should be
for how they are going to be used.

unpacked parameters:
    self.reportFileName     <- rfn
    self.massWindow         <- mwn
    self.edc                <- edc
    self.TOFPusherInt       <- tpi
    self.savgolWindow       <- sgw
    self.savgolPoly         <- sgp
    self.calCurveFileName   <- cff
    self.calDataFile        <- cdf
    self.compoundDataDir    <- crd

    TODO:   FIX THIS CRAP, this system is terrible because it breaks if any of the
            keywords are omitted

Input(s):
    none
"""
        # TODO:   FIX THIS CRAP, this system is terrible because it breaks if any of the
        #         keywords are omitted or out of order
        self.reportFileName = self.rawData[0][0]
        # cast massWindow, edc, and TOFPusherInt to type float
        self.massWindow = float(self.rawData[0][1])
        self.edc = float(self.rawData[0][2])
        self.TOFPusherInt = float(self.rawData[0][3])
        # cast Savgol window and poly order to ints
        self.savgolWindow = int(self.rawData[0][4])
        self.savgolPoly = int(self.rawData[0][5])
        self.calCurveFileName = self.rawData[1][0]
        self.calDataFile = self.rawData[1][1]
        self.compoundDataDir = self.rawData[2][0]


    def unpackListParams(self):
        """
ParseInputFile.unpackListParams

Breaks the rawData[3] array into two easy to access arrays with calibration data and
compound data separated from one another

Input(s):
    none
"""
        # temporary lists to build the arrays from
        templist1 = []
        templist2 = []
        templist3 = []
        templist4 = []
        flag = False
        for thing in self.rawData[3]:
            if flag:
                templist3.append(thing[0])
                # need to cast compound mass to float
                templist4.append(float(thing[1]))
            elif thing[0] == "compound":
                flag = True
            else:
                # temporary list values for ccs data are cast to floats so that the resulting array
                # will have type float
                templist1.append(float(thing[0]))
                templist2.append(float(thing[1]))
        # array of floats
        self.calibrantData = array([templist1, templist2])
        # make separate lists for the compound file names and compound masses
        self.compoundFileNames = templist3
        self.compoundMasses = templist4

    def __str__(self):
        """
ParseInputFile.__str__
    description:
        prints all of the named parameters

unpacked parameters:
    self.reportFileName     <- rfn
    self.massWindow         <- mwn
    self.edc                <- edc
    self.TOFPusherInt       <- tpi
    self.savgolWindow       <- sgw
    self.savgolPoly         <- sgp
    self.calCurveFileName   <- cff
    self.calDataFile        <- cdf
    self.compoundDataDir    <- crd

    parameters:
        none
    returns:
        string representation of the object
"""
        out =  "reportFileName   (rfn) = '{:s}'\n".format(self.reportFileName)
        out += "massWindow       (mwn) = {: 6.4f}\n".format(self.massWindow)
        out += "edc              (edc) = {: 6.4f}\n".format(self.edc)
        out += "TOFPusherInt     (tpi) = {: 6.3f}\n".format(self.TOFPusherInt)
        out += "savgolWindow     (sgw) = {: 3d}\n".format(self.savgolWindow)
        out += "savgolPoly       (sgp) = {: 3d}\n".format(self.savgolPoly)
        out += "calCurveFileName (cff) = '{:s}'\n".format(self.calCurveFileName)
        out += "calDataFile      (cdf) = '{:s}'\n".format(self.calDataFile)
        out += "compoundDataDir  (crd) = '{:s}'\n".format(self.compoundDataDir)
        return out
