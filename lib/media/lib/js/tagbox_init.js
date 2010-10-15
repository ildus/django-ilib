function init_tagboxes() {
	$('.tagbox').tagbox({
		name: 'tags',
		grouping: '"',
		separator:/[,;]/
	});
}

$(document).ready(function () {
	init_tagboxes();
})