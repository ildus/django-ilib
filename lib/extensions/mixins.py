#coding: utf-8

from django.conf import settings as django_settings
from django.contrib import admin
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpResponseNotFound, HttpResponseServerError
from django.utils import simplejson

from django.utils.safestring import mark_safe

import logging

def django_boolean_icon(field_val, alt_text=None, title=None):
    """
    Return HTML code for a nice representation of true/false.
    """

    # Origin: contrib/admin/templatetags/admin_list.py
    BOOLEAN_MAPPING = { True: 'yes', False: 'no', None: 'unknown' }
    alt_text = alt_text or BOOLEAN_MAPPING[field_val]
    if title is not None:
        title = 'title="%s" ' % title
    else:
        title = ''
    return mark_safe(u'<img src="%simg/admin/icon-%s.gif" alt="%s" %s/>' %
            (django_settings.ADMIN_MEDIA_PREFIX, BOOLEAN_MAPPING[field_val], alt_text, title))
    
def ajax_editable_boolean_cell(item, attr, text='', override=None):
    """
    Generate a html snippet for showing a boolean value on the admin page.
    Item is an object, attr is the attribute name we should display. Text
    is an optional explanatory text to be included in the output.

    This function will emit code to produce a checkbox input with its state
    corresponding to the item.attr attribute if no override value is passed.
    This input is wired to run a JS ajax updater to toggle the value.

    If override is passed in, ignores the attr attribute and returns a
    static image for the override boolean with no user interaction possible
    (useful for "disabled and you can't change it" situations).
    """
    if text:
        text = '&nbsp;(%s)' % unicode(text)

    if override is not None:
        a = [ django_boolean_icon(override, text), text ]
    else:
        value = getattr(item, attr)
        a = [
              '<input type="checkbox"',
              value and ' checked="checked"' or '',
              ' onclick="return inplace_toggle_boolean(%d, \'%s\')";' % (item.id, attr),
              ' />',
              text,
            ]

    a.insert(0, '<div id="wrap_%s_%d">' % ( attr, item.id ))
    a.append('</div>')
    return unicode(''.join(a))

def ajax_editable_boolean(attr, short_description):
    """
    Convenience function: Assign the return value of this method to a variable
    of your ModelAdmin class and put the variable name into list_display.

    Example:
        class MyTreeEditor(TreeEditor):
            list_display = ('__unicode__', 'active_toggle')

            active_toggle = ajax_editable_boolean('active', _('is active'))
    """
    def _fn(self, item):
        return ajax_editable_boolean_cell(item, attr)
    _fn.allow_tags = True
    _fn.short_description = short_description
    _fn.editable_boolean_field = attr
    return _fn

class AjaxEditable(admin.ModelAdmin):
    ''' Add ajax changing functionality in change list '''
    
    def _collect_editable_booleans(self):
        """
        Collect all fields marked as editable booleans. We do not
        want the user to be able to edit arbitrary fields by crafting
        an AJAX request by hand.
        """
        if hasattr(self, '_ajax_editable_booleans'):
            return

        self._ajax_editable_booleans = {}

        for field in self.list_display:
            # The ajax_editable_boolean return value has to be assigned
            # to the ModelAdmin class
            item = getattr(self.__class__, field, None)
            if not item:
                continue

            attr = getattr(item, 'editable_boolean_field', None)
            if attr:
                def _fn(self, page):
                    return [ ajax_editable_boolean_cell(page, _fn.attr) ]
                _fn.attr = attr
                result_func = getattr(item, 'editable_boolean_result', _fn)
                self._ajax_editable_booleans[attr] = result_func
                
    def _toggle_boolean(self, request):
        """
        Handle an AJAX toggle_boolean request
        """
        try:
            item_id = int(request.POST.get('item_id', None))
            attr = str(request.POST.get('attr', None))
        except:
            return HttpResponseBadRequest("Malformed request")

        if not request.user.is_staff:
            logging.warning("Denied AJAX request by non-staff %s to toggle boolean %s for page #%s", request.user, attr, item_id)
            return HttpResponseForbidden("You do not have permission to access this page")

        self._collect_editable_booleans()

        if not self._ajax_editable_booleans.has_key(attr):
            return HttpResponseBadRequest("not a valid attribute %s" % attr)

        try:
            obj = self.model._default_manager.get(pk=item_id)
        except self.model.DoesNotExist:
            return HttpResponseNotFound("Object does not exist")

        can_change = False

        if hasattr(obj, "user_can") and obj.user_can(request.user, change_page=True):
            can_change = True
        else:
            can_change = request.user.has_perm("page.change_page")

        if not can_change:
            logging.warning("Denied AJAX request by %s to toggle boolean %s for page %s", request.user, attr, item_id)
            return HttpResponseForbidden("You do not have permission to access this page")

        logging.info("Processing request by %s to toggle %s on %s", request.user, attr, obj)

        try:
            before_data = self._ajax_editable_booleans[attr](self, obj)

            setattr(obj, attr, not getattr(obj, attr))
            obj.clean()
            obj.save()

            # Construct html snippets to send back to client for status update
            data = self._ajax_editable_booleans[attr](self, obj)

        except Exception, e:
            logging.exception("Unhandled exception while toggling %s on %s", attr, obj)
            return HttpResponseServerError("Unable to toggle %s on %s because: %s" % (attr, obj, e))

        # Weed out unchanged cells to keep the updates small. This assumes
        # that the order a possible get_descendents() returns does not change
        # before and after toggling this attribute. Unlikely, but still...
        d = []
        for a, b in zip(before_data, data):
            if a != b:
                d.append(b)

        return HttpResponse(simplejson.dumps(d), mimetype="application/json")
    
    def changelist_view(self, request, extra_context=None, *args, **kwargs):
        # handle common AJAX requests
        if request.is_ajax():
            cmd = request.POST.get('__cmd')
            if cmd == 'toggle_boolean':
                return self._toggle_boolean(request)
            else:
                return HttpResponseBadRequest('Oops. AJAX request not understood.')

        return super(AjaxEditable, self).changelist_view(request, extra_context, *args, **kwargs)
    
    def _media(self):
        location_libs = django_settings.MEDIA_URL+'lib/js/'
        media = super(AjaxEditable, self)._media()
        media.add_js([location_libs+'ajax_boolean_fields.js'])
        return media
    media = property(_media)