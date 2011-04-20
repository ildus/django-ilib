var replace_element = function(i, html) {
    var r_id = $(html).attr('id');
    $('#' + r_id).replaceWith(html);
}

/* Same as above, but processes an array of html snippets */
var replace_elements = function(data) {
    $.each(data, replace_element);
}

/* OnClick handler to toggle a boolean field via AJAX */
var inplace_toggle_boolean = function(item_id, attr) {
    $.ajax({
      url: ".",
      type: "POST",
      dataType: "json",
      data: { '__cmd': 'toggle_boolean', 'item_id': item_id, 'attr': attr },

      success: replace_elements,

      error: function(xhr, status, err) {
          alert("Unable to toggle " + attr + ": " + xhr.responseText);
      }
    });

    return false;
}