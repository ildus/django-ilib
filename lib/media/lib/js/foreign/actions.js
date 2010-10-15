dojo.addOnLoad(function() {
	document.body.className = "tundra";
});

dojo.require("dijit.Dialog");
dojo.require("dojox.data.JsonRestStore");
dojo.require("dijit.Tree");

function row_selected() {return true; }

function log_error(e) {
	console.error(e);
}

//создает диалоговое окно, контент загружается по линку из атрибута link переданной ссылки
//после загрузки контента, вызывается onload_func
function create_dlg(link, onload_func) {
	var dlg = new dijit.Dialog({
		title: "Выберите объект",
        style: "width: 500px; max-height: 500px; overflow: auto;",
        href: dojo.attr(link, 'link'),
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
		//var dlg = null;
		function onload_func() {
			dojo.query('.searchers a, .pagination a').onclick(function (e) {
				e.preventDefault();
				href = this.href;
				main_href = dojo.attr(link, 'link');
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

//обработка клика в дереве
function onRowSelect(item) {
	if (item.selectable) {
		dojo.byId('id_'+item.field_name).value = item.pk
		
		dojo.byId('fk-name-'+item.field_name).innerHTML = item.name
		row_selected();
	}
}

//обработка клика в списке
function onListSelect(link, id, field_name) {
	dojo.byId('id_'+field_name).value = id
	dojo.byId('fk-name-'+field_name).innerHTML = link.innerHTML
	row_selected();
	return false;
}

//инициализация дерева
function init_tree(target_link) {		
	var store = new dojox.data.JsonRestStore({
        target: target_link,
        labelAttribute: "name"
    });

    var treeModel = new dijit.tree.ForestStoreModel({
        store: store,
        deferItemLoadingUntilExpand: true,
        query: "root",
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