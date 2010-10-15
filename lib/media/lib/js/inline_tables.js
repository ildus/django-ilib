$(document).ready(function () {
    fieldsets = $('.inline_table')
    fieldsets.each(function (i, fs) {
        $.ajax(
            'type': 'GET',
            'url': 'get_table/'+i+'/'+
    });
})
