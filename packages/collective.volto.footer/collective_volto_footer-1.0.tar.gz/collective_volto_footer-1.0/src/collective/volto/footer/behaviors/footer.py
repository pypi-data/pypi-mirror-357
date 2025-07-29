# -*- coding: utf-8 -*-

from collective.volto.footer import _
from plone import schema
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from Products.CMFPlone.utils import safe_hasattr
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface
from zope.interface import provider


class IEditableFooterMarker(Interface):
    """Marker interface for editable footer blocks in Volto projects."""

    pass


@provider(IFormFieldProvider)
class IEditableFooter(model.Schema):
    """Behavior for editable footer blocks in Volto projects."""

    model.fieldset(
        "layout",
        label=_("Layout"),
        fields=["footer"],
    )

    footer = schema.JSONField(
        title=_("Footer Blocks"),
        description=_("Define the footer blocks for this project"),
        default={
            "blocks": {
                "e113cf00-f7fb-4870-a49c-a15b84fcfd99": {
                    "@type": "slate",
                    "value": [
                        {
                            "type": "p",
                            "children": [
                                {"text": ""},
                                {
                                    "type": "link",
                                    "data": {"url": "http://localhost:3000/edit"},
                                    "children": [{"text": "Edit"}],
                                },
                                {"text": ""},
                            ],
                        }
                    ],
                    "plaintext": " Edit ",
                }
            },
            "blocks_layout": {"items": ["e113cf00-f7fb-4870-a49c-a15b84fcfd99"]},
        },
        required=False,
    )


@implementer(IEditableFooter)
@adapter(IEditableFooterMarker)
class EditableFooter(object):
    def __init__(self, context):
        self.context = context

    @property
    def footer(self):
        if safe_hasattr(self.context, "footer"):
            return self.context.footer
        return None

    @footer.setter
    def footer(self, value):
        self.context.footer = value
