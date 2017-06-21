"""
    RawToTxt.py
    Dylan H. Ross

    This program performs .raw to .txt conversion of all .raw files in a specified directory
    using CDCReader.exe and cdt.dll

"""

# need subprocess to execute CDCReader.exe
import subprocess
# glob can search a directory for file names using wildcards
import glob
# convenient path splitting tools
import os
# command-line argument parsing
import argparse

# buildFunctionCall     (method)
#
# generates a full function call to do the .raw to .txt file conversion
# using windows cmd. Usage (with subprocess.call):
#   subprocess.call(buildFunctionCall(*parameters*))
#
# paramters:
#   pathToCDCReader     (string)        - full path to CDCReader.exe executable (IMPORTANT:
#                                           cdt.dll must be in the same directory as
#                                           CDCReader.exe for it to work properly)
#   pathToInputFile     (string)        - full path to the input (.raw) file
#   outputPath          (string)        - path to directory to put output files into, closed
#                                           with a trailing /
#   outputBaseName      (string)        - the base name of the output files which
#                                           start with "IM_" or "MS_" and end with
#                                           "_out.txt"
#   imBin               (float)         - value to bin the masses by in the IM output file
#                                           (it says it should be a float but really it
#                                           could be an int or a string too, since it is 
#                                           cast to a string anyways) [default = 0.05]
#
# returns:
#   callLine            (string)        - the full function call to CDCReader.exe
#                                           executed by subprocess.call
def buildFunctionCall(pathToCDCReader,\
                      pathToInputFile,\
                      outputPath,\
                      outputBaseName,\
                      imBin = 0.05):
    # build all the function call flags
    rFlagLine = "--raw_file '" + pathToInputFile + "' "
    mFlagLine = "--ms_file '" + outputPath + "MS_" + outputBaseName + ".txt' "
    iFlagLine = "--im_file '" + outputPath + "IM_" + outputBaseName + "_bin-" + str(imBin) + ".txt' "
    # do not perform any smoothing
    numberSmoothFlagLine = "--ms_number_smooth 0 "
    smoothWindowFlagLine = "--ms_smooth_window 0 "
    imBinFlagLine = "--im_bin " + str(imBin) + " "
    # make the MS binning very large so that too much time isnt wasted creating it
    msBinFlagLine = "--ms_bin 10 "
    # call the function in powershell, via cmd
    callLine = "powershell " +\
               pathToCDCReader + " " +\
               rFlagLine + \
               mFlagLine + \
               iFlagLine + \
               numberSmoothFlagLine + \
               smoothWindowFlagLine + \
               imBinFlagLine + \
               msBinFlagLine
    # return the line containing the final function call
    return callLine

# batchConvertInDirectory     (method)
#
# converts all .raw files in a specified directory to .txt using buildFunctionCall() and
# subprocess.call()
#
# paramters:
#   dataDirectory       (string)        - full path to directory containing all of the .raw
#                                           files to be converted, closed with a trailing /
#   pathToCDCReader     (string)        - full path to CDCReader.exe executable (IMPORTANT:
#                                           cdt.dll must be in the same directory as
#                                           CDCReader.exe for it to work properly)
#   imBin               (float)         - value to bin the masses by in the IM output file
#                                           (it says it should be a float but really it
#                                           could be an int or a string too, since it is 
#                                           cast to a string anyways) [default = 0.05]
def batchConvertInDirectory(dataDirectory, pathToCDCReader, imBin=0.05):
    # make a list of all .raw files in the dataDirectory
    rawFileList = glob.glob(dataDirectory + "*.raw")
    count = 1
    for rawFile in rawFileList:
        # report to the user which file is being converted
        print "now converting file: ", \
              os.path.split(rawFile)[1], \
              "(" + str(count), "of", \
              str(len(rawFileList)) + ")..."
        # call CDCReader.exe with a function call from buildFunctionCall()
        subprocess.call(buildFunctionCall(pathToCDCReader, \
                                          rawFile, \
                                          os.path.split(rawFile)[0] + "/", \
                                          os.path.splitext(os.path.split(rawFile)[1])[0],\
                                          imBin=imBin))
        print "...DONE"
        count += 1

# prepParser            (method)
#
# prepares an ArgumentParser object with a program description and all necessary arguments
#
# paramters:
#   none
#
# returns:
#   parser              (ArgumentParser) - an ArgumentParser object for parsing command-line 
#                                           arguments
def prepParser():
    programDescription = "This program performs .raw to .txt conversion of all .raw files in \
                  a specified directory using CDCReader.exe"
    parser = argparse.ArgumentParser(description=programDescription)
    parser.add_argument('--data-dir',\
                        required=True,\
                        help='directory containing .raw files to convert',\
                        dest="dataDirectory",\
                        metavar='/full/path/to/data-dir/')
    parser.add_argument('--CDCR',\
                        required=True,\
                        help='full path to CDCReader.exe',\
                        dest="pathToCDCReader",\
                        metavar='/full/path/to/CDCReader.exe')
    parser.add_argument('--im-bin',\
                        required=False,\
                        help='value to bin masses by in IM-data.txt, default = 0.05',\
                        dest="imBin",\
                        default=0.05)
    return parser

# TODO
def cleanUpDataDirectory(dataDirectory):
    pass
    
    
### MAIN EXECUTION ###
if __name__ == '__main__':
    # prepare the argument parser and print the help message
    parser = prepParser()
    # get the command line arguments
    args = parser.parse_args()
    # perform the batch file conversion
    batchConvertInDirectory(args.dataDirectory, args.pathToCDCReader, args.imBin)
    # remove the MS_*.txt files from the data directory
    cleanUpDataDirectory(args.dataDirectory)
    
