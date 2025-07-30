# -*- coding: utf-8 -*-
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer

import collective.volto.footer


class CollectiveVoltoFooterLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        import plone.app.dexterity

        self.loadZCML(package=plone.app.dexterity)
        import plone.restapi

        self.loadZCML(package=plone.restapi)
        self.loadZCML(package=collective.volto.footer)

    def setUpPloneSite(self, portal):
        applyProfile(portal, "collective.volto.footer:default")


COLLECTIVE_VOLTO_FOOTER_FIXTURE = CollectiveVoltoFooterLayer()


COLLECTIVE_VOLTO_FOOTER_INTEGRATION_TESTING = IntegrationTesting(
    bases=(COLLECTIVE_VOLTO_FOOTER_FIXTURE,),
    name="CollectiveVoltoFooterLayer:IntegrationTesting",
)


COLLECTIVE_VOLTO_FOOTER_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(COLLECTIVE_VOLTO_FOOTER_FIXTURE,),
    name="CollectiveVoltoFooterLayer:FunctionalTesting",
)
