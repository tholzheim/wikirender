'''
Created on 12.07.2021

@author: wf
'''
import unittest
from wikifile.cmdline import CmdLineAble


class TestCommandLine(unittest.TestCase):
    '''
    test the command line handling
    '''

    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testCommandLineHandling(self):
        '''
        test looping over the command line arguments
        

        '''
        args=["--pages","3DUI","--source","orclone" ]
        # "--template","Event series"
        cmdLine=CmdLineAble()
        cmdLine.getParser()
        args = cmdLine.parser.parse_args(args)
        cmdLine.initLogging(args)
        pageTitles=cmdLine.getPageTitlesForArgs(args)
        print(pageTitles)
        
        
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()