
#from CcsCal.input.RawData import RawData
#from CcsCal.processing.GaussFit import GaussFit



from openpyxl import load_workbook
import time


class ExcelIO():

    def __init__(self, xlsx_file, override_warning=True, auto_run=True):
        """
ExcelIO -- Class

An object for running the CcsCal main analysis workflow using a MS Excel (or probably any spreadsheet
software that implements the Office Open XML format) workbook for both input and output. Program exits
if the workbook is unable to be loaded.

Input(s):
    xlsx_file   -   name of the excel file to read from / write to (string)
    [override_warning]    - print a warning that the xlsx file will be overridden (bool) [optional, default=True]
    [auto_run]  -   automatically call the run() method after initialization (bool) [optional, default=True]
"""
        # load up the workbook
        try:
            self.xlsx_name_ = xlsx_file
            self.xlsx_ = load_workbook(xlsx_file)
        except:
            print "Unable to load Excel workbook, exiting..."
            exit(1)
        # check that it has all of the necessary information
        self.checkInput()
        # issue the override warning if asked to
        if override_warning:
            self.issueOverrideWarning()
        if auto_run():
            self.run()

    def checkInput(self):
        """
ExcelIO.checkInput

Checks that the provided input xlsx file contains the information necessary for
running the analysis workflow. Raises an exception if not.
"""
        # first check that the workbook has a sheet called 'Input'
        if 'Input' not in self.xlsx_.get_sheet_names():
            raise ValueError("CcsCal: ExcelIO: checkInput: no sheet named 'Input' in workbook")

    def issueOverrideWarning(self):
        """
ExcelIO.issueOverrideWarning

Warns the user that the current xlsx file will be overridden and asks if they wish to
proceed. Also warn that the file cannot be open in Excel otherwise the changes cannot be written.
"""
        print
        print "!!WARNING: the file " + self.xlsx_name_ + " will be overridden. Please ensure that " + \
                    "this is the correct file and it is not open in Excel before proceeding!!"
        print
        proceed = raw_input("Proceed? (y/n) ")
        if proceed not in ["y", "Y", "yes", "Yes", "YES"]:
            print "Exiting..."
            exit()

    def run(self):
        """
ExcelIO.run

performs all of the steps in the data analysis workflow, saves results in the xlsx file.
"""
        pass
