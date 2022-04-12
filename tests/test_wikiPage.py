import datetime
import uuid
from unittest import TestCase
from tests.default_wikiuser import DefaultWikiUser
from wikifile.wikiFile import WikiFile
from wikifile.wikiPage import WikiPage


class TestWikiPage(TestCase):
    """
    Tests WikiPageUpdater
    """

    def setUp(self) -> None:
        self.wikiId = "wikirenderTest"
        _wikiUser = DefaultWikiUser.getSMW_WikiUser(self.wikiId)
        self.pageUpdater = WikiPage(self.wikiId)
        self.testWikiSonEntity = "Test"

    def test_updatePageWikiSON_create(self):
        """
        tests updating a non-existing entity
        """
        record = {
            "uuid": str(uuid.uuid1()),
            "startdate": datetime.datetime.now(),
            "name": "Test WikiPage",
            "test": "test_updatePageWikiSON_create"
        }
        pageTitle = record['uuid']
        self.pageUpdater.updatePageWikiSON(pageTitle, self.testWikiSonEntity, record)
        pageRecord = self.pageUpdater.getWikiSonFromPage(pageTitle, self.testWikiSonEntity)
        self.assertEqual(record['uuid'], pageRecord['uuid'])

    def test_updatePageWikiSON_update(self):
        """
        tests updating an existing entity
        """
        record = {
            "uuid": str(uuid.uuid1()),
            "startdate": datetime.datetime.now(),
            "name": "Test WikiPage",
            "test": "test_updatePageWikiSON_update"
        }
        pageTitle = record['uuid']
        self.pageUpdater.updatePageWikiSON(pageTitle, self.testWikiSonEntity, record)
        updateRecord = {
            "startdate": '2000'
        }
        self.pageUpdater.updatePageWikiSON(pageTitle, self.testWikiSonEntity, updateRecord)
        pageRecord = self.pageUpdater.getWikiSonFromPage(pageTitle, self.testWikiSonEntity)
        self.assertEqual(updateRecord['startdate'], pageRecord['startdate'])

    def test_updatePageWikiSON_delete(self):
        """
        tests deleting a property of an existing entity
        """
        record = {
            "uuid": str(uuid.uuid1()),
            "startdate": datetime.datetime.now(),
            "name": "Test WikiPage",
            "test": "test_updatePageWikiSON_delete"
        }
        pageTitle = record['uuid']
        self.pageUpdater.updatePageWikiSON(pageTitle, self.testWikiSonEntity, record)
        updateRecord = {
            "startdate": None
        }
        self.pageUpdater.updatePageWikiSON(pageTitle, self.testWikiSonEntity, updateRecord)
        pageRecord = self.pageUpdater.getWikiSonFromPage(pageTitle, self.testWikiSonEntity)
        self.assertEqual(record['uuid'], pageRecord['uuid'])
        self.assertNotIn('startdate', pageRecord)

    def test_getWikiSonFromPage(self):
        """
        tests getWikiSonFromPage
        """
        wikiMarkup = """{{Test
        |name=getWikiSonFromPage
        |test=test_getWikiSonFromPage
        }}
        Free Text outside of the WikiSON."""
        pageTitle = str(uuid.uuid1())
        wikiFile = WikiFile(pageTitle, self.pageUpdater.wikiFileManager, wikiMarkup)
        wikiFile.pushToWiki("Added page for test_getWikiSonFromPage")
        record = self.pageUpdater.getWikiSonFromPage(pageTitle, wikiSonEntity=self.testWikiSonEntity)
        self.assertEqual(2, len(record))
        self.assertNotIn("wikiMarkup", record)
        self.assertEqual('getWikiSonFromPage', record.get('name'))
        # test with wikiMarkup inclusion
        recordWithMarkup = self.pageUpdater.getWikiSonFromPage(pageTitle, wikiSonEntity=self.testWikiSonEntity, includeWikiMarkup=True)
        self.assertEqual(3, len(recordWithMarkup))
        self.assertIn("wikiMarkup", recordWithMarkup)
        self.assertEqual(wikiMarkup, recordWithMarkup.get('wikiMarkup'))


