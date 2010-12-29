function add_related_field(url, collection_id, self_id, content_type_id, related_field, clear_related, current_value) {
	var obj = dojo.byId(collection_id);
	var cur_value = current_value;
	
	if (clear_related) obj.value = '';
	
	function reload() {
		data = {
				'value': obj.value,
				'content_type_id': content_type_id,
				'related_field': related_field,
			}
			xhrArgs = {
				url: url,
				handleAs: 'json',
				content: data,
				load: function(response) {
					dojo.empty(self_id);
					dojo.forEach(response, function (item) {
						function val(item) {
							if (item.id > 0) return '="'+item.id+'"'; else return '';
						}
						
						if (item.id == cur_value) sel = ' selected';
						else sel = '';
						dojo.place('<option value'+val(item)+sel+'>'+item.title+'</option>', dojo.byId(self_id), 'last');
					})
	            },
	            error: function(error) {
	            	dojo.empty(self_id);
	                dojo.place("<option> Ошибка </option> ", dojo.byId(self_id), 'first');
	            }
			}

			dojo.xhrPost(xhrArgs);
	}
	
	dojo.connect(obj, 'onchange', obj, reload);
	if (obj.value != '') reload();
}