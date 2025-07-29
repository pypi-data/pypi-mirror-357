# -*- coding: utf-8 -*-
"""
collective.iconifiedcategory
----------------------------

Created by mpeeters
:license: GPL, see LICENCE.txt for more details.
"""

from collective.iconifiedcategory import testing
from zope.component import getUtility
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent
from zope.schema.interfaces import IVocabularyFactory

import unittest


class TestVocabularies(unittest.TestCase):
    layer = testing.COLLECTIVE_ICONIFIED_CATEGORY_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def _check_category_vocabulary(self, vocabulary):
        """ """
        terms = [t.title for t in vocabulary]
        self.assertEqual(2 * 3 * 3, len(terms))
        categories = [
            'Category 1-3',
            'Category 2-3',
            'Category 1-2',
            'Category 2-2',
            'Category 1-1',
            'Category 2-1',
        ]
        self.assertListEqual(
            [t for t in terms if t.startswith('Category')],
            categories,
        )
        subcategories = [
            'Subcategory 1-3-2', 'Subcategory 1-3-1',
            'Subcategory 2-3-2', 'Subcategory 2-3-1',
            'Subcategory 1-2-2', 'Subcategory 1-2-1',
            'Subcategory 2-2-2', 'Subcategory 2-2-1',
            'Subcategory 1-1-2', 'Subcategory 1-1-1',
            'Subcategory 2-1-2', 'Subcategory 2-1-1',
        ]
        self.assertListEqual(
            [t for t in terms if t.startswith('Subcategory')],
            subcategories,
        )

    def test_category_vocabulary(self):
        vocabulary = getUtility(
            IVocabularyFactory,
            name='collective.iconifiedcategory.categories',
        )
        vocabulary = vocabulary(self.portal)
        self._check_category_vocabulary(vocabulary)

    def test_category_vocabulary_use_category_uid_as_token(self):
        vocabulary = getUtility(
            IVocabularyFactory,
            name='collective.iconifiedcategory.categories',
        )
        vocabulary = vocabulary(self.portal, use_category_uid_as_token=True)
        self._check_category_vocabulary(vocabulary)

    def test_category_title_vocabulary(self):
        vocabulary = getUtility(
            IVocabularyFactory,
            name='collective.iconifiedcategory.category_titles',
        )
        terms = [t.title for t in vocabulary(self.portal)]
        self.assertEqual(6, len(terms))
        expected = [
            'Category 1-1', 'Category 1-2', 'Category 1-3',
            'Category 2-1', 'Category 2-2', 'Category 2-3',
        ]
        self.assertListEqual(sorted(expected), sorted(terms))

        # add some predefined_title to some subcategories
        subcat = self.portal.config['group-1']['category-1-1']['subcategory-1-1-1']
        self.assertIsNone(subcat.predefined_title)
        subcat.predefined_title = u'Some predefined title'
        notify(ObjectModifiedEvent(subcat))
        terms = [t.title for t in vocabulary(self.portal)]
        self.assertEqual(7, len(terms))
        expected = [
            'Category 1-1', u'Some predefined title',
            'Category 1-2', 'Category 1-3',
            'Category 2-1', 'Category 2-2', 'Category 2-3',
        ]
        self.assertListEqual(sorted(expected), sorted(terms))

    def test_category_title_only_pdf_vocabulary(self):
        vocabulary = getUtility(
            IVocabularyFactory,
            name='collective.iconifiedcategory.categories',
        )
        # change only_pdf to True for a category and a subcategory
        cat = self.portal.config['group-1']['category-1-1']
        cat.only_pdf = True
        subcat = self.portal.config['group-1']['category-1-1']['subcategory-1-1-1']
        subcat.only_pdf = True

        terms = [t.title for t in vocabulary(self.portal)]
        self.assertEqual(
            terms,
            ['Category 1-3', 'Subcategory 1-3-2', 'Subcategory 1-3-1',
             'Category 2-3', 'Subcategory 2-3-2', 'Subcategory 2-3-1',
             'Category 1-2', 'Subcategory 1-2-2', 'Subcategory 1-2-1',
             'Category 2-2', 'Subcategory 2-2-2', 'Subcategory 2-2-1',
             'Category 1-1 [PDF!]', 'Subcategory 1-1-2', 'Subcategory 1-1-1 [PDF!]',
             'Category 2-1', 'Subcategory 2-1-2', 'Subcategory 2-1-1'])

    def test_category_title_show_preview_vocabulary(self):
        vocabulary = getUtility(
            IVocabularyFactory,
            name='collective.iconifiedcategory.categories',
        )
        # change only_pdf to True for a category and a subcategory
        cat = self.portal.config['group-1']['category-1-1']
        cat.show_preview = 1
        subcat = self.portal.config['group-1']['category-1-1']['subcategory-1-1-1']
        subcat.only_pdf = True
        subcat.show_preview = 2

        terms = [t.title for t in vocabulary(self.portal)]
        self.assertEqual(
            terms,
            ['Category 1-3', 'Subcategory 1-3-2', 'Subcategory 1-3-1',
             'Category 2-3', 'Subcategory 2-3-2', 'Subcategory 2-3-1',
             'Category 1-2', 'Subcategory 1-2-2', 'Subcategory 1-2-1',
             'Category 2-2', 'Subcategory 2-2-2', 'Subcategory 2-2-1',
             'Category 1-1 [Preview!]', 'Subcategory 1-1-2', 'Subcategory 1-1-1 [PDF!] [Preview!]',
             'Category 2-1', 'Subcategory 2-1-2', 'Subcategory 2-1-1'])

    def test_every_categories_vocabulary(self):
        vocabulary = getUtility(
            IVocabularyFactory,
            name='collective.iconifiedcategory.every_categories',
        )
        terms = [t.token for t in vocabulary(self.portal)]
        self.assertEqual(
            terms,
            ['plone-config_-_group-1_-_category-1-3',
             'plone-config_-_group-1_-_category-1-3_-_subcategory-1-3-2',
             'plone-config_-_group-1_-_category-1-3_-_subcategory-1-3-1',
             'plone-config_-_group-2_-_category-2-3',
             'plone-config_-_group-2_-_category-2-3_-_subcategory-2-3-2',
             'plone-config_-_group-2_-_category-2-3_-_subcategory-2-3-1',
             'plone-config_-_group-1_-_category-1-2',
             'plone-config_-_group-1_-_category-1-2_-_subcategory-1-2-2',
             'plone-config_-_group-1_-_category-1-2_-_subcategory-1-2-1',
             'plone-config_-_group-2_-_category-2-2',
             'plone-config_-_group-2_-_category-2-2_-_subcategory-2-2-2',
             'plone-config_-_group-2_-_category-2-2_-_subcategory-2-2-1',
             'plone-config_-_group-1_-_category-1-1',
             'plone-config_-_group-1_-_category-1-1_-_subcategory-1-1-2',
             'plone-config_-_group-1_-_category-1-1_-_subcategory-1-1-1',
             'plone-config_-_group-2_-_category-2-1',
             'plone-config_-_group-2_-_category-2-1_-_subcategory-2-1-2',
             'plone-config_-_group-2_-_category-2-1_-_subcategory-2-1-1'])

    def test_every_category_uids_vocabulary(self):
        vocabulary = getUtility(
            IVocabularyFactory,
            name='collective.iconifiedcategory.every_category_uids',
        )
        terms = [t.token for t in vocabulary(self.portal)]
        grp1 = self.portal.config.get('group-1')
        grp2 = self.portal.config.get('group-2')
        self.assertTrue(grp1.get('category-1-1').UID() in terms)
        self.assertTrue(grp1.get('category-1-1').get('subcategory-1-1-2').UID() in terms)
        self.assertTrue(grp2.get('category-2-3').UID() in terms)
        self.assertTrue(grp2.get('category-2-2').get('subcategory-2-2-2').UID() in terms)
