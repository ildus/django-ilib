dojo.addOnLoad(function() {
	document.body.className = "tundra";
});

dojo.require("dijit.Dialog");
dojo.require("dojox.data.JsonRestStore");
dojo.require("dijit.Tree");
dojo.require("dojo.string");

function row_selected() {return true; }

function log_error(e) {
	console.error(e);
}

function get_collection_params(link) {
	var col_params = '';
	collection = dojo.attr(link, 'collection');
	if (collection) {
		collection_id = dojo.byId('id_'+collection).value;
		if (collection_id) {
			col_params = collection_id+'/';
		}
	}
	return col_params;
}

function get_href(link) {
	url = dojo.attr(link, 'link');
	return url+get_collection_params(link);
}

//создает диалоговое окно, контент загружается по линку из атрибута link переданной ссылки
//после загрузки контента, вызывается onload_func
function create_dlg(link, onload_func) {
	var dlg = new dijit.Dialog({
		title: dojo.attr(link, 'data-dialog-title') || "Выберите объект",
        style: "width: 500px; max-height: 500px; overflow: auto;",
        href: get_href(link),
    });
	
	dlg.show();
	
	dojo.connect(dlg, 'onHide', dlg, function () {
		dlg.destroyRecursive();
	});
	
	dojo.connect(dlg, 'onLoad', dlg, onload_func);
	
	//при вызове row_selected это диалоговое окно скрывается, ну и заодно полностью удаляется
	dojo.connect(null, 'row_selected', dlg, function () {
		this.hide();
	})
	
	return dlg;
}

function showListDialog(link) {
	try {
		collection = dojo.attr(link, 'collection');
		if (collection) {
			if (!get_collection_params(link)) {
				alert('Необходимо сначала выбрать связанную запись ('+collection+')');
				return false;
			}
		}
		
		function onload_func() {
			dojo.query('.searchers a, .pagination a').onclick(function (e) {
				e.preventDefault();
				href = this.href;
				main_href = get_href(link);
				p = href.indexOf('?');
				if (p != -1) {
					params = href.substring(p);
					dlg.set('href', main_href+params);
				}
				return false;
			})
		}
		
		var dlg = create_dlg(link, onload_func);
	}
	catch (e) {
		log_error(e);
	}
    return false;
}

function showTreeDialog(link) {	
	try {
		function onload_func () {
			target = dojo.attr(link, 'target')
			init_tree(target);
		}
		
		var dlg = create_dlg(link, onload_func);
	}
	catch (e) {
		log_error(e);
	}
    return false;
}

var multiple_format = '<span class="popup_mm_value">'+
		'<label><span> ${0} </span>'+
		'	<input type="hidden" name="${1}" value="${2}"><small class="close" title="close">x</small>'+
		'</label></span>'
		
var input_format = 'input[type="hidden"][name="${0}"][value="${1}"]'
	
function deleteItem(item) {
	val_elem = item.parentNode.parentNode;
	par = val_elem.parentNode;
	par.removeChild(val_elem);
}
		
function already_selected(item) {
	var s  = dojo.string.substitute(input_format, [item.field_name, item.pk]);
	return django.jQuery(s).length > 0;
}
		
function addItemForMultiple(item) {
	var s  = dojo.string.substitute(multiple_format, [item.name, item.field_name, item.pk]);
	if (!already_selected(item)) {
		parent_id = 'id_' + item.field_name;
		dojo.place(s, dojo.byId(parent_id), 'first');
		dojo.destroy(dojo.query('#'+parent_id+' .empty')[0]);
		row_selected();
	}
	
	django.jQuery('small.close').unbind('click').click(function (e) {
		deleteItem(this);
	});
}

dojo.addOnLoad(function () {
	dojo.query('small.close').onclick(function (e) {
		deleteItem(this);
	});
})

//обработка клика в дереве
function onRowSelect(item) {
	if (item.selectable) {
		dojo.byId('id_'+item.field_name).value = item.pk
			
		dojo.byId('fk-name-'+item.field_name).innerHTML = item.name;
		row_selected();
	}
}

//обработка клика в списке
function onListSelect(link, id, field_name, for_multiple) {
	if (!for_multiple) {
		dojo.byId('id_' + field_name).value = id
		dojo.byId('fk-name-' + field_name).innerHTML = link.innerHTML
		row_selected();
		return false;
	}
	else {
		item = {
			field_name: field_name, 
			pk: id,
			name: link.innerHTML,
		}
		addItemForMultiple(item);
	}
}

//инициализация дерева
function init_tree(target_link) {
    try {
        root_query = page_root_query;        
    }
    catch (e) {
        root_query = 'root';
    }
    
	var store = new dojox.data.JsonRestStore({
        target: target_link,
        labelAttribute: "name"
    });

    var treeModel = new dijit.tree.ForestStoreModel({
        store: store,
        deferItemLoadingUntilExpand: true,
        query: root_query,
        childrenAttrs: ["children"]
    });

    tree = new dijit.Tree({
        model: treeModel,
        showRoot: false
    }, "treeOne");
    
    tree.startup();

    var tmph = dojo.connect(tree, 'onLoad', tree, function() {
        dojo.disconnect(tmph);
		dojo.connect(tree, 'onClick', tree, onRowSelect);
    });
}
