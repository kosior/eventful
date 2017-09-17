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
        customPost($(this), csrf_token, function (json, ref) {
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
        var invitedPks = [];
        $('.invites a').each(function () {
            invitedPks.push($(this).attr('data-pk'));
        });

        $.get(url, function (friends) {
            var invSelect = $('#id_invite');
            invSelect.empty();
            friends.forEach(function (friend) {
                if($.inArray(friend.pk.toString(), invitedPks) === -1) {
                    invSelect.append($('<option></option>').attr('value', friend.pk).attr(
                    'data-subtext', friend.first_name + ' ' + friend.last_name).text(friend.username));
                }
            });
            invSelect.selectpicker('refresh');
        });
    });

    $('#inviteModalBtn').click(function () {
        var url = $(this).attr('data-url');
        var pks = $('#id_invite').val();
        var data = {'pks[]': pks, 'csrfmiddlewaretoken': csrf_token};
        if (pks) {
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

function setUpFriendsOpts(friends) {
    var invSelect = $('#id_invite');
    invSelect.attr('multiple', 'multiple');
    friends.forEach(function (friend) {
        var fullName = friend.first_name + ' ' + friend.last_name;
        invSelect.append($('<option></option>').attr('value', friend.pk).attr('data-subtext', fullName).text(friend.username));
    });
}

function setUpFriendSelect(friends) {
    if (friends) {
        setUpFriendsOpts(friends);
    }
    $('#id_invite').selectpicker({
        template: {
                caret: '<span class="fa fa-users"></span>'
            },
        style: 'tz-select',
        liveSearch: true,
        actionsBox: true,
        selectedTextFormat: 'count',
        countSelectedText: '{0} friends selected',
        });
}