django.jQuery(document).ready(function () {
    django.jQuery.getScript('/media/lib/js/tiny_mce/tiny_mce_popup.js', function() {
        django.jQuery('#changelist tbody a').click(function(e) {
            if (window.parent && window.parent.IMAGE_UPLOADING == true) {
            
                var url = '/lib/img/'+django.jQuery(this).attr('href');
                var win = tinyMCEPopup.getWindowArg("window");

                win.document.getElementById(tinyMCEPopup.getWindowArg("input")).value = url;

                if (typeof(win.ImageDialog) != "undefined") {
                    if (win.ImageDialog.getImageData) win.ImageDialog.getImageData();
                    if (win.ImageDialog.showPreviewImage) win.ImageDialog.showPreviewImage(url);
                }

                tinyMCEPopup.close();
                return false;
            }
        });
    });
});
