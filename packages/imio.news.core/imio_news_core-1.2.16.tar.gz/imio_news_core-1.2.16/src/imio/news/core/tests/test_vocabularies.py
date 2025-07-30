# -*- coding: utf-8 -*-

from imio.news.core.testing import IMIO_NEWS_CORE_INTEGRATION_TESTING
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory

import unittest


class TestVocabularies(unittest.TestCase):
    layer = IMIO_NEWS_CORE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

    def test_news_categories(self):
        factory = getUtility(IVocabularyFactory, "imio.news.vocabulary.NewsCategories")
        vocabulary = factory()
        self.assertEqual(len(vocabulary), 4)

    def test_news_local_categories_on_root(self):
        factory = getUtility(
            IVocabularyFactory, "imio.news.vocabulary.NewsLocalCategories"
        )
        vocabulary = factory(self.portal)
        self.assertEqual(len(vocabulary), 0)

    def test_news_categories_topics_basic(self):
        entity = api.content.create(
            container=self.portal,
            type="imio.news.Entity",
            title="Entity",
            local_categories=[],
        )
        newsfolder = api.content.create(
            container=entity,
            type="imio.news.NewsFolder",
            title="News folder",
        )

        news_item = api.content.create(
            container=newsfolder, type="imio.news.NewsItem", title="title"
        )
        factory = getUtility(
            IVocabularyFactory,
            "imio.news.vocabulary.NewsCategoriesAndTopicsVocabulary",
        )
        vocabulary = factory(news_item)
        self.assertEqual(len(vocabulary), 21)  # must be updated if add new vocabulary

    def test_news_categories_topics_local_cat(self):
        entity = api.content.create(
            container=self.portal,
            type="imio.news.Entity",
            title="Entity",
            local_categories=[
                {"fr": "Foo", "nl": "", "de": "", "en": ""},
                {"fr": "baz", "nl": "", "de": "", "en": ""},
                {"fr": "bar", "nl": "", "de": "", "en": ""},
            ],
        )
        newsfolder = api.content.create(
            container=entity,
            type="imio.news.NewsFolder",
            title="News folder",
        )

        news_item = api.content.create(
            container=newsfolder, type="imio.news.NewsItem", title="title"
        )

        factory = getUtility(
            IVocabularyFactory,
            "imio.news.vocabulary.NewsCategoriesAndTopicsVocabulary",
        )
        vocabulary = factory(news_item)
        self.assertEqual(len(vocabulary), 24)  # must be updated if add new vocabulary

    def test_news_folders_UIDs(self):
        entity1 = api.content.create(
            container=self.portal,
            type="imio.news.Entity",
            title="Entity1",
        )
        entity2 = api.content.create(
            container=self.portal,
            type="imio.news.Entity",
            title="Entity2",
        )
        news_folder1 = api.content.create(
            container=entity1,
            type="imio.news.NewsFolder",
            title="NewsFolder1",
        )
        news_folder2 = api.content.create(
            container=entity2,
            type="imio.news.NewsFolder",
            title="NewsFolder2",
        )
        folder = api.content.create(
            container=news_folder1,
            type="imio.news.Folder",
            title="Folder",
        )
        news_item1 = api.content.create(
            container=folder,
            type="imio.news.NewsItem",
            title="NewsItem1",
        )
        news_item2 = api.content.create(
            container=news_folder2,
            type="imio.news.NewsItem",
            title="NewsItem2",
        )
        all_news_folders = []
        nf_entity1 = entity1.listFolderContents(
            contentFilter={"portal_type": "imio.news.NewsFolder"}
        )
        nf_entity2 = entity2.listFolderContents(
            contentFilter={"portal_type": "imio.news.NewsFolder"}
        )
        all_news_folders = [*set(nf_entity1 + nf_entity2)]
        factory = getUtility(IVocabularyFactory, "imio.news.vocabulary.NewsFoldersUIDs")
        vocabulary = factory(self.portal)
        self.assertEqual(len(vocabulary), len(all_news_folders))
        vocabulary = factory(news_item1)
        self.assertEqual(len(vocabulary), len(all_news_folders))

        vocabulary = factory(news_item2)
        uid = news_folder2.UID()
        vocabulary.getTerm(uid)
        self.assertEqual(vocabulary.getTerm(uid).title, "Entity2 » NewsFolder2")

        vocabulary = factory(self.portal)
        ordered_news_folders = [a.title for a in vocabulary]
        titles = []
        for news_folder in nf_entity1 + nf_entity2:
            titles.append(f"{news_folder.aq_parent.Title()} » {news_folder.Title()}")
        titles.sort()
        ordered_news_folders.sort()
        self.assertEqual(ordered_news_folders, titles)
        news_folder1.title = "Z Change order!"
        news_folder1.reindexObject()
        vocabulary = factory(self.portal)
        ordered_news_folders = [a.title for a in vocabulary]
        self.assertIn("Entity1 » Z Change order!", ordered_news_folders)
