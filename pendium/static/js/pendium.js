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

    /* Keyboard shortcuts */

    $(document).bind('keydown', 'j', function() {
        $(document).scrollTop( $(document).scrollTop() + 100);
    });

    $(document).bind('keydown', 'k', function() {
        $(document).scrollTop( $(document).scrollTop() - 100);
    });

    $(document).bind('keyup', 's', function() {
        $('#drop_plugins').dropdown('toggle');
        $('#searchbox_type').focus();
        this.value = this.value.replace('s', '');
    });

    $(document).bind('keyup', 'f', function() {
        $('#drop_files').dropdown('toggle');
    });

    $(document).bind('keyup', 'h', function() {
        $('#shortcuts_help').modal();
    });

});
