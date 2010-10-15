function tinyDjangoBrowser(field_name, url, type, win) {
    var managerURL = '/admin/lib/simpleimage/?type=' + type;

    tinyMCE.activeEditor.windowManager.open({
        file: managerURL,
        title: 'Выберите нужную картинку',
        width: 800,
        height: 450,
        resizable: 'yes',
        inline: 'yes',
        close_previous: 'no',
        popup_css : false
    }, {
        window: win,
        input: field_name
    });

    return false;
}

window.IMAGE_UPLOADING = true;

$(document).ready(function () {
    jQuery('textarea.tinymce_editor').tinymce({
        //script_url : '/media/lib/js/tiny_mce/tiny_mce.js',
        mode : "textareas",
        convert_urls : false,
        width:  585,
        height: 250,
        theme : "advanced",
        plugins : "table,searchreplace,paste,inlinepopups",
        theme_advanced_buttons1 : "bold,italic,underline,separator,pastetext,pasteword,separator,link,unlink,image,strikethrough,separator,bullist,numlist,separator,indent,outdent,separator,justifyleft,justifycenter,justifyright,justifyfull,separator,undo,redo,separator,formatselect,separator,search,replace,separator,code",
        theme_advanced_buttons2 : "tablecontrols",
        theme_advanced_buttons3 : "",
        theme_advanced_toolbar_location : "top",
        theme_advanced_toolbar_align : "left",
        theme_advanced_path_location : "bottom",
        extended_valid_elements : "a[name|href|target|title|onclick]",
        file_browser_callback: 'tinyDjangoBrowser'
    });   
});
