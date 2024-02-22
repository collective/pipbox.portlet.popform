from ComputedAttribute import ComputedAttribute
from pipbox.portlet.popform import PopupFormMessageFactory as _
from plone.app.portlets.browser import formhelper
from plone.app.portlets.portlets import base
from plone.app.vocabularies.catalog import CatalogSource
from plone.memoize.instance import memoize
from plone.portlets.interfaces import IPortletDataProvider
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zExceptions import NotFound
from zope import schema
from zope.interface import implementer

pipbox_config = """
if (popform.cookies_enabled("%s")) {
    $(function(){ setTimeout( function() {
        $("a#%s").click()}, %s);
        });
}
"""


class IPopupForm(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    target_form_uid = schema.Choice(title=_(u"Target Form Folder"),
        description=_(u"Find the form you wish to display in a popup."),
        required=True,
        source=CatalogSource(portal_type=['FormFolder', 'EasyForm']),
    )

    display_after = schema.Int(title=_(u"Display Time"),
        description=_(u"One-tenth seconds to wait after page load before displaying the form."),
        required=True,
        default=10,
    )

    width = schema.TextLine(title=_(u"Popup Width"),
        description=_(u"Width of the popup form in pixels (px) or percent (%)."),
        required=True,
        default=u'300px')

    no_form = schema.Choice(title=_(u"If Successful"),
        description=_(u"On a successful submission, what should happen?"),
        required=True,
        source=schema.vocabulary.SimpleVocabulary.fromItems([
            (_(u'Show thanks page in popup'), ''),
            (_(u'Close popup'), 'close'),
            (_(u'Close popup and refresh page'), 'reload'),
            (_(u'Redirect to specified page'), 'redirect'),
        ]),
        default='',
    )

    redir_url = schema.TextLine(title=_(u"Redirection Target"),
        description=_(u'If you select "redirect to" above, specify the target web address here.'),
        required=False,
        default=u'',
    )


@implementer(IPopupForm)
class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    redir_url = None
    target_form = None
    display_after = 1

    def __init__(self,
                 target_form_uid=None,
                 display_after=1,
                 no_form='',
                 width="300px",
                 redir_url=''):
        self.target_form_uid = target_form_uid
        self.display_after = display_after
        self.no_form = no_form
        self.width = width
        self.redir_url = redir_url

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return _(u"Popup Form")

    def _target_form_uid(self):
        # This is only called if the instance doesn't have a target_form_uid
        # attribute, which is probably because it has an old
        # 'target_form' attribute that needs to be converted.
        path = self.target_form
        portal = getToolByName(self, 'portal_url').getPortalObject()
        try:
            form = portal.unrestrictedTraverse(path.lstrip('/'))
        except (AttributeError, KeyError, TypeError, NotFound):
            return
        return form.UID()
    target_form_uid = ComputedAttribute(_target_form_uid, 1)


class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('popupform.pt')

    def uid(self):
        form_url = self.form_url()
        if form_url is not None:
            return "popform-%s" % form_url.split('/')[-1]

    def form_url(self):
        form = self.target_form()
        if form is None:
            return None
        else:
            return form.absolute_url()

    def embed_url(self):
        form = self.target_form()
        if form is None:
            return None
        embed_view = '/embedded'
        if form.portal_type == 'FormFolder':
            embed_view = '/fg_embedded_view_p3?show_text=1'
        return form.absolute_url().rstrip('/') + embed_view

    def delay(self):
        return self.data.display_after

    def jqtinit(self):
        uid = self.uid()
        return pipbox_config % (
            uid,
            uid,
            self.delay() * 100)

    @memoize
    def target_form(self):
        """ get the form the portlet is pointing to"""

        form_uid = self.data.target_form_uid
        if not form_uid:
            return None

        catalog = getToolByName(self.context, 'portal_catalog')
        results = catalog.searchResults(UID=form_uid)
        if not results:
            return None

        return results[0].getObject()


class AddForm(formhelper.AddForm):
    schema = IPopupForm
    label = _(u'Add Popup Form')

    def create(self, data):
        return Assignment(**data)


class EditForm(formhelper.EditForm):
    schema = IPopupForm
    label = _(u'Edit Popup Form')
