# -*- coding: utf-8 -*-

from imio.smartweb.common.adapters import BaseCroppingProvider
from imio.smartweb.locales import SmartwebMessageFactory as _
from plone.app.content.namechooser import NormalizingNameChooser
from plone.app.textfield import RichText
from plone.app.z3cform.widget import SelectFieldWidget
from plone.autoform import directives
from plone.autoform.directives import read_permission
from plone.autoform.directives import write_permission
from plone.dexterity.content import Container
from plone.supermodel import model
from zope import schema
from zope.container.interfaces import INameChooser
from zope.interface import implementer


class NewsItemCroppingProvider(BaseCroppingProvider):
    def get_scales(self, fieldname, request=None):
        if fieldname == "image":
            # scales used for lead image field
            return [
                "portrait_affiche",
                "paysage_affiche",
                "carre_affiche",
            ]
        return []


class IDETranslations(model.Schema):
    model.fieldset(
        "de_translations",
        label=_("German translations"),
        fields=["title_de", "description_de", "text_de"],
    )
    title_de = schema.TextLine(
        title=_("Title"),
        description=_(
            "This field is required if the content must be available in this language"
        ),
        required=False,
    )
    description_de = schema.Text(title=_("Description"), required=False)
    text_de = RichText(title=_("Text"), required=False)


class IENTranslations(model.Schema):
    model.fieldset(
        "en_translations",
        label=_("English translations"),
        fields=["title_en", "description_en", "text_en"],
    )
    title_en = schema.TextLine(
        title=_("Title"),
        description=_(
            "This field is required if the content must be available in this language"
        ),
        required=False,
    )
    description_en = schema.Text(title=_("Description"), required=False)
    text_en = RichText(title=_("Text"), required=False)


class INLTranslations(model.Schema):
    model.fieldset(
        "nl_translations",
        label=_("Dutch translations"),
        fields=["title_nl", "description_nl", "text_nl"],
    )
    title_nl = schema.TextLine(
        title=_("Title"),
        description=_(
            "This field is required if the content must be available in this language"
        ),
        required=False,
    )
    description_nl = schema.Text(title=_("Description"), required=False)
    text_nl = RichText(title=_("Text"), required=False)


class ITranslations(IENTranslations, IDETranslations, INLTranslations):
    """ """


class INewsItem(ITranslations):
    """Marker interface and Dexterity Python Schema for NewsItem"""

    site_url = schema.URI(
        title=_("Website"),
        description=_("NewsItem website url"),
        required=False,
    )

    video_url = schema.URI(
        title=_("Video url"),
        description=_("Video url from youtube, vimeo"),
        required=False,
    )

    facebook = schema.URI(
        title=_("Facebook"),
        description=_("Facebook url for this news"),
        required=False,
    )

    twitter = schema.URI(
        title=_("Twitter"),
        description=_("Twitter url for this news"),
        required=False,
    )

    instagram = schema.URI(
        title=_("Instagram"),
        description=_("Instagram url for this news"),
        required=False,
    )

    model.fieldset(
        "categorization", fields=["selected_news_folders", "category", "local_category"]
    )
    directives.widget(selected_news_folders=SelectFieldWidget)
    selected_news_folders = schema.List(
        title=_("Selected news folders"),
        description=_(
            "Select news folders where this news item will be displayed. Current news folder is always selected."
        ),
        value_type=schema.Choice(vocabulary="imio.news.vocabulary.NewsFoldersUIDs"),
        default=[],
        required=False,
    )

    category = schema.Choice(
        title=_("Category"),
        description=_(
            "Important! These categories are used to supplement the information provided by the topics"
        ),
        source="imio.news.vocabulary.NewsCategories",
        required=False,
    )

    local_category = schema.Choice(
        title=_("Specific category"),
        description=_(
            "Important! These categories allow you to use criteria that are specific to your organization"
        ),
        source="imio.news.vocabulary.NewsLocalCategories",
        required=False,
    )

    read_permission(selected_news_folders="imio.news.core.AddEntity")
    write_permission(selected_news_folders="imio.news.core.AddEntity")


@implementer(INewsItem)
class NewsItem(Container):
    """NewsItem class"""


@implementer(INameChooser)
class NewsItemNameChooser(NormalizingNameChooser):
    def chooseName(self, name, obj):
        if INewsItem.providedBy(obj):
            return obj.UID()
        return super(NewsItemNameChooser, self).chooseName(name, obj)
