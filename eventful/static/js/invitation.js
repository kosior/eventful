function customPost(ref, csrf_token, callback) {
    var url = $(ref).attr('data-url');
    var pk = $(ref).attr('data-pk');
    var change = $(ref).attr('data-change');
    var data = {'pk': pk, 'csrfmiddlewaretoken': csrf_token};
    $.post(url, data, function (json) {
        if (json.result) {
                $(ref).html(change).addClass('btn-success disabled');
            }
            else {
                $(ref).html('Error').addClass('btn-danger disabled');
            }
        if (callback){
            callback(json, ref, pk);
        }
    }, 'json');
}

$(function () {
    $('.actionRequestBtn').click(function () {
        customPost($(this), csrf_token);
    });

    $('#removeFriendBtn').click(function () {
        customPost($(this), csrf_token, function (json, ref, pk) {
            $(ref).unbind('mouseenter mouseleave')
        });
    }).hover(function () {
        $(this).addClass('btn-danger');
        $(this).html('Remove from friends <span class="glyphicon glyphicon-remove"></span>');
    }, function () {
        $(this).removeClass('btn-danger');
        $(this).html('Friends <span class="glyphicon glyphicon-ok"></span>');
    });
});