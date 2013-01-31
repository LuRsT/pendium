$(document).ready(function() {
    $('table').each(function() {
        $(this).addClass('table');
    });

    $('.toc').each( function() {
        $(this).append('<hr>');
    });

    $('#searchbox_type').typeahead({
        updater: function ( item ) {
            location = '/' + mapped[item];
        },
        source: function (query, process) {
            return $.get('/search', { 'q' : query }, function ( data ) {
                labels = [];
                mapped = {};
                $.each(data['results'], function( i, item ) {
                    mapped[ item['hit'] ] = item['path'];
                    labels.push( item['hit'] );
                });
                return process( labels );
            });
        }
    });
});
