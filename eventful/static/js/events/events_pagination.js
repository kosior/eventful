var events;

$(function () {
    events = $(".events");
});

function paginate (ref) {
    var pager = $(".pager");
    var pageNum = $(ref).attr("data-pagenum");
    pager.remove();
    $.get(url_events_ajax + "?page=" + pageNum, function (data) {
        events.append(data);
    });
}