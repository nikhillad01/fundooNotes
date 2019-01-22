(function($) {
  $('#lazyLoadLink').on('click', function() {
    var link = $(this);
    var page = link.data('page');

    $.ajax({
      type: 'notes',
      url: '/lazy_load_notes/',
      data: {
        'page': page,
        'csrfmiddlewaretoken': window.CSRF_TOKEN // from index.html
      },
      success: function(data) {
        // if there are still more pages to load,
        // add 1 to the "Load More Posts" link's page data attribute
        // else hide the link
        if (data.has_next) {
            link.data('page', page+1);
        } else {
          link.hide();
        }
        // append html to the posts div
        $('#div').append(data.notes/notes_list.html);
      },
      error: function(xhr, status, error) {
        // shit happens friends!
      }
    });
  });
}(jQuery));