"""
    Runs all (completed) tests

    2017/06/01
    Dylan H. Ross
"""


from CcsCal.tests import input_parsing
from CcsCal.tests import external_data


def run_subtest(subtest, name):
    """
all_tests.run_subtest
    description:
        performs all of the tests specified by a subtest module's run() method within a try/except block
    parameters:
        subtest (test module) -- a subtest module with a run() method
        name (str) -- name of the component/feature being tested by the subtest module
    returns:
        no
"""
    try:
        print "testing " + name + "..."
        assert subtest.run()
        print "...PASS"
    except AssertionError:
        print "...FAIL"
    print


# run all of the tests
def run():
    """
all_tests.run
    description:
        runs all specified subtests
    parameters:
        no
    returns:
        no
"""
    run_subtest(input_parsing, "ParseInputFile")
    run_subtest(external_data, "CcsCalibrationExt with external data source")

