# updates the documentation for the CcsCal package


# generate the updated documentation

ana-python -m pydoc -w CcsCal

    ana-python -m pydoc -w CcsCal.globals
    
    ana-python -m pydoc -w CcsCal.__main__
    
    ana-python -m pydoc -w CcsCal.input
    
        ana-python -m pydoc -w CcsCal.input.ParseInputFile
        
        ana-python -m pydoc -w CcsCal.input.RawData
        
    ana-python -m pydoc -w CcsCal.processing
    
        ana-python -m pydoc -w CcsCal.processing.GaussFit
        
        ana-python -m pydoc -w CcsCal.processing.CcsCalibration
        
        ana-python -m pydoc -w CcsCal.processing.Report
        
    ana-python -m pydoc -w CcsCal.tests
        
        ana-python -m pydoc -w CcsCal.tests.all_tests
        
        ana-python -m pydoc -w CcsCal.tests.input_parsing
        
        ana-python -m pydoc -w CcsCal.tests.external_data


# move all of the html files into the docs directory, overwrite whatever is there
mv -force .\*.html .\docs