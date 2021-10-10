'''
Created on 13.07.2021

@author: wf
'''
from wikibot.wikiuser import WikiUser
import os
import getpass

class DefaultWikiUser(object):
    '''
    provides a default WikiFilUser for certain wikiIds
    '''
    @staticmethod    
    def inPublicCI():
        '''
        are we running in a public Continuous Integration Environment?
        '''
        return getpass.getuser() in [ "travis", "runner" ]
            
    @classmethod
    def getSMW_WikiUser(cls,wikiId="or",save=None):
        '''
        get semantic media wiki users for SemanticMediawiki.org and openresearch.org
        '''
        if save is None:
            save=DefaultWikiUser.inPublicCI()
        iniFile=WikiUser.iniFilePath(wikiId)
        wikiUser=None
        if not os.path.isfile(iniFile):
            wikiDict=None
            if wikiId=="or":
                wikiDict={"wikiId": wikiId,"email":"noreply@nouser.com","url":"https://www.openresearch.org","scriptPath":"/mediawiki/","version":"MediaWiki 1.31.1"}
            if wikiId=="orclone":
                wikiDict={"wikiId": wikiId,"email":"noreply@nouser.com","url":"https://confident.dbis.rwth-aachen.de","scriptPath":"/or/","version":"MediaWiki 1.35.1"}
            if wikiId=="cr":
                wikiDict={"wikiId": wikiId,"email":"noreply@nouser.com","url":"https://cr.bitplan.com","scriptPath":"/","version":"MediaWiki 1.33.4"}
            if wikiId=="wikirenderTest":
                wikiDict={"wikiId": wikiId,"email":"noreply@nouser.com","url":"http://localhost:8000","scriptPath":"","version":"MediaWiki 1.31.14", "user":"Sysop","password":"sysop-1234!"}   # tries fixing the missing wikiuser that normally be created by the wikicluster in the startDocker script
                
            if wikiDict is None:
                raise Exception("wikiId %s is not known" % wikiId)
            else:
                encrypted= 'password' not in wikiDict
                wikiUser=WikiUser.ofDict(wikiDict, encrypted=encrypted, lenient=True)   # ToDo: Why does encrypted needs to be false to enable encryption?
                if save:
                    wikiUser.save()
        else:
            wikiUser=WikiUser.ofWikiId(wikiId,lenient=True)
        return wikiUser