$(function () {
	$('.lib_nf_wrapper').each(function (i, item) {
		wrapper = $(item);
		wrapper.children('input').change(handle_changes).mouseover(make_active).mouseout(unmake_active);
	});  
});

function handle_changes(e)
{
    file = $(this).val();
    reWin = /.*\\(.*)/;
    var fileTitle = file.replace(reWin, "$1"); //выдираем название файла
    reUnix = /.*\/(.*)/;
    fileTitle = fileTitle.replace(reUnix, "$1"); //выдираем название файла
    
    fn = $(this).siblings('.lib_nf_filename')
    fn.text(fileTitle);
    
    var RegExExt =/.*\.(.*)/;
    var ext = fileTitle.replace(RegExExt, "$1");//и его расширение
    
    var pos;
    if (ext){
        switch (ext.toLowerCase())
        {
            case 'doc': pos = '0'; break;
            case 'bmp': pos = '16'; break;                       
            case 'jpg': pos = '32'; break;
            case 'jpeg': pos = '32'; break;
            case 'png': pos = '48'; break;
            case 'gif': pos = '64'; break;
            case 'psd': pos = '80'; break;
            case 'mp3': pos = '96'; break;
            case 'wav': pos = '96'; break;
            case 'ogg': pos = '96'; break;
            case 'avi': pos = '112'; break;
            case 'wmv': pos = '112'; break;
            case 'flv': pos = '112'; break;
            case 'pdf': pos = '128'; break;
            case 'exe': pos = '144'; break;
            case 'txt': pos = '160'; break;
            default: pos = '176'; break;
        };
        fn.css({
        	'display': 'block',
        	'background': 'url(/media/lib/fileinput/icons.png) no-repeat 0 -'+pos+'px'
        });
    };    
};
function make_active(e)
{
	ab = $(this).siblings('.lib_nf_activebutton');
	ab.show();
};
function unmake_active(e)
{
	ab = $(this).siblings('.lib_nf_activebutton');
    ab.hide();
};