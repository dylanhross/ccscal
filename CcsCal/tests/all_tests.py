"""
    Runs all (completed) tests

    2017/06/01
    Dylan H. Ross
"""


from CcsCal.tests import input_parsing


# run all of the tests
def run():

    # tests for the ParseInputFile object
    try:
        print "testing ParseInputFile..."
        assert input_parsing.run()
        print "...PASS"
    except AssertionError:
        print "...FAIL"
    print

