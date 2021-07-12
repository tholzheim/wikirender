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
        args=["--pages","3DUI","--wikiTextPath=." ]
        # "--template","Event series", "--source","orclone"]
        cmdLine=CmdLineAble()
        cmdLine.getParser()
        cmdLine.parser.add_argument("--listFile", dest="file_list",
                                 help="List of pages from which the data should be extracted", required=False)

        args = cmdLine.parser.parse_args(args)
        cmdLine.initLogging(args)
        pageTitles=cmdLine.getPageTitlesForArgs(args)
        print(pageTitles)
        
        
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()