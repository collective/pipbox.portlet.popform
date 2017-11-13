Introduction
============

`Popup Forms for Plone` is a Plone add-on that enables timed popups of
`PloneFormGen`_ forms.

Popup forms are configured as a portlet. When you add it, you specify
a PloneFormGen form and the time delay (in 1/10th seconds). The form will
then be shown as an AJAX popup form.

When the popup is viewed, a cookie is set with a 1-year expiration, and the
popup will not display again unless the cookie is absent. That prevents it
from annoying more than once. Cookie support is also checked first, so
the form will not be displayed if cookies aren't enabled. Again, the
idea is to avoid annoying users.

popform is a very small product that's mainly used to control a bit
of `pipbox`_ functionality. If there are visual display or AJAX problems,
please file a bug report against pipbox.

.. _`PloneFormGen`: http://plone.org/products/ploneformgen
.. _`pipbox`: http://plone.org/products/pipbox

Compatibility
=============

Popup Forms for Plone has been tested with Plone 3.  Support for Plone 4 is
pending a PloneFormGen release that works in Plone 4.

It requires Products.pipbox 3.0a8 or greater (which should get installed
automatically as an egg dependency).

Credits
=======

Popup Forms for Plone was developed by `Steve McMahon`_ for `Groundwire`_.

.. _`Steve McMahon`: http://reidmcmahon.com
.. _`Groundwire`: http://groundwire.org
