$(document).ready(function() {
    $('table').each(function() {
        $(this).addClass('table');
    });
    $('.toc').each( function() {
        $(this).append('<hr>');
    });
    //$('#sidebar').affix();
});
