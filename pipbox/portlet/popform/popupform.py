from zope.interface import implements
from zope.component import getMultiAdapter

from Acquisition import aq_inner

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from plone.memoize.instance import memoize

from zope import schema
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from pipbox.portlet.popform import PopupFormMessageFactory as _

from plone.app.vocabularies.catalog import SearchableTextSourceBinder
from plone.app.form.widgets.uberselectionwidget import UberSelectionWidget

from Products.PloneFormGen.interfaces import IPloneFormGenForm

pipbox_config = """
jQuery(function($) {
    if (popform.cookies_enabled("%s")) {
        $('a#%s').prepOverlay({
            subtype:'ajax',
            urlmatch:'$',
            urlreplace:'/fg_embedded_view_p3?show_text=1 .pfg-embedded,#content' + String.fromCharCode(62) + '*',
            formselector:'form',
            noform:'%s',
            config:{closeOnClick:false},
            width:"%s",
            redirect:"%s"});
        $(function(){ setTimeout( function() {
            $("a#%s").click()}, %s);
            });
    }
});
"""


class IPopupForm(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    target_form = schema.Choice(title=_(u"Target Form Folder"),
      description=_(u"Find the form you wish to display in a popup."),
      required=True,
      source=SearchableTextSourceBinder(
        {'object_provides': IPloneFormGenForm.__identifier__},
        default_query='path:'))

    display_after = schema.Int(title=_(u"Display Time"),
      description=_(u"One-tenth seconds to wait after page load before displaying the form."),
      required=True,
      default=10)

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
        default='')

    redir_url = schema.TextLine(title=_(u"Redirection Target"),
        description=_(u'If you select "redirect to" above, specify the target web address here.'),
        required=False,
        default=u'')


class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IPopupForm)

    redir_url = None
    target_form = None
    display_after = 1

    def __init__(self,
                 target_form=None,
                 display_after=1,
                 no_form='',
                 width="300px",
                 redir_url=''):
        self.target_form = target_form
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

    def delay(self):
        return self.data.display_after

    def jqtinit(self):
        uid = self.uid()
        return pipbox_config % (
            uid,
            uid,
            self.data.no_form,
            self.data.width,
            self.data.redir_url,
            uid,
            self.delay() * 100)

    @memoize
    def target_form(self):
        """ get the form the portlet is pointing to"""

        form_path = self.data.target_form
        if not form_path:
            return None

        if form_path.startswith('/'):
            form_path = form_path[1:]

        if not form_path:
            return None

        portal_state = \
            getMultiAdapter((aq_inner(self.context), self.request),
                            name=u'plone_portal_state')
        portal = portal_state.portal()
        return portal.restrictedTraverse(form_path, default=None)


class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(IPopupForm)
    form_fields['target_form'].custom_widget = UberSelectionWidget

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(IPopupForm)
    form_fields['target_form'].custom_widget = UberSelectionWidget
