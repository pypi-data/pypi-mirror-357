# -*- coding: utf-8 -*-
from collective.volto.footer.behaviors.footer import IEditableFooterMarker
from collective.volto.footer.testing import (  # noqa
    COLLECTIVE_VOLTO_FOOTER_INTEGRATION_TESTING,
)
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.behavior.interfaces import IBehavior
from zope.component import getUtility

import unittest


class EditableFooterIntegrationTest(unittest.TestCase):

    layer = COLLECTIVE_VOLTO_FOOTER_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

    def test_behavior_footer_editable(self):
        behavior = getUtility(IBehavior, "collective.volto.footer.editable")
        self.assertEqual(
            behavior.marker,
            IEditableFooterMarker,
        )
