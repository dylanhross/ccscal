# updates the documentation for the CcsCal package


# generate the updated documentation

pydoc -w CcsCal

    pydoc -w CcsCal.globals
    
    pydoc -w CcsCal.__main__
    
    pydoc -w CcsCal.input
    
        pydoc -w CcsCal.input.ParseInputFile
        
        pydoc -w CcsCal.input.RawData
        
    pydoc -w CcsCal.processing
    
        pydoc -w CcsCal.processing.GaussFit
        
        pydoc -w CcsCal.processing.CcsCalibration
        
        pydoc -w CcsCal.processing.Report
        
    pydoc -w CcsCal.tests
        
        pydoc -w CcsCal.tests.all_tests
        
        pydoc -w CcsCal.tests.input_parsing
        
        pydoc -w CcsCal.tests.external_data

        
# move all of the html files into the docs directory, overwrite whatever is there
mv ./*.html docs/