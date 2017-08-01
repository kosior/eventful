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

$(function () {
    $('#inviteBtn').click(function () {
        var url = $(this).attr('data-url');
        $.get(url, function (friends) {
            var invSelect = $('#inviteSelect');
            invSelect.empty();
            invSelect.html('<option value="" disabled selected>Pick your friend</option>');
            friends.forEach(function (friend) {
                invSelect.append($('<option></option>').attr('value', friend.pk).text(friend.username));
            });

        });
    });

    $('#inviteModalBtn').click(function () {
        var url = $(this).attr('data-url');
        var pk = $('#inviteSelect').find(":selected").attr('value');
        var data = {'pk': pk, 'csrfmiddlewaretoken': csrf_token};
        if (pk) {
            $.post(url, data, function (json) {
                var invitePop = $('#invitePop');
                if (json.result) {
                        $('#modalInvite').modal('hide');
                        invitePop.attr('data-content', 'Invite sent.').popover('show');
                        setTimeout(function () {
                            invitePop.popover('hide');
                        }, 2000);
                    }
                    else {
                        $('#modalInvite').modal('hide');
                        invitePop.attr('data-content', 'Invite exist.').popover('show');
                        setTimeout(function () {
                            invitePop.popover('hide');
                        }, 2000);
                    }
            }, 'json');
        }
    });
});