# updates the documentation for the CcsCal package


# change the py alias to wherever your Python 3.x is
# Set-Alias py C:/your/path/to/Python3x.exe


# generate the updated documentation

py -m pydoc -w CcsCal

    py -m pydoc -w CcsCal.globals
    
    py -m pydoc -w CcsCal.__main__
    
    py -m pydoc -w CcsCal.input
    
        py -m pydoc -w CcsCal.input.ParseInputFile
        
        py -m pydoc -w CcsCal.input.RawData

        py -m pydoc -w CcsCal.input.ExcelIO

    py -m pydoc -w CcsCal.metabolism

        py -m pydoc -w CcsCal.metabolism.Metabolites

        py -m pydoc -w CcsCal.metabolism.Encoder
        
    py -m pydoc -w CcsCal.processing
    
        py -m pydoc -w CcsCal.processing.GaussFit
        
        py -m pydoc -w CcsCal.processing.CcsCalibration
        
        py -m pydoc -w CcsCal.processing.Report
        
    py -m pydoc -w CcsCal.tests
        
        py -m pydoc -w CcsCal.tests.all_tests
        
        py -m pydoc -w CcsCal.tests.input_parsing
        
        py -m pydoc -w CcsCal.tests.external_data

        py -m pydoc -w CcsCal.tests.ccscal_main


# move all of the html files into the docs directory, overwrite whatever is there
mv -force .\*.html .\docs