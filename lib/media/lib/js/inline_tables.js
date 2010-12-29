$(document).ready(function () {
    fieldsets = $('.inline_table')
    fieldsets.each(function (i, fs) {
        $.ajax(
            'type': 'GET',
            'url': 'get_table/'+i+'/'+
    });
        
    dismissAddAnotherPopup_orig = dismissAddAnotherPopup;
        
    function add_link(link) {
        showAddAnotherPopup(link);
        dismissAddAnotherPopup = function (win, newId, newRepr) {
            reload_inlinetables();
            win.close();
            dismissAddAnotherPopup = dismissAddAnotherPopup_orig;
        }
        return false;
    }
})
