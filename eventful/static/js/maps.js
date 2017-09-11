function createMap() {
    var eventMap = L.map('eventMap');
    L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors',
    }).addTo(eventMap);
    return eventMap;
}

function eventDetailMap(lat, lng) {
    var eventMap = createMap();
    var zoom = 16;
    var url = 'http://nominatim.openstreetmap.org/reverser?format=json&lat=' + lat + '&lon=' + lng;

    eventMap.setView([lat, lng], zoom);

    $.get(url, function (json) {
        L.marker([lat, lng]).addTo(eventMap).bindPopup(json.display_name).openPopup();
    });
}

function eventCreateUpdateMap(lat, lng, action) {
    var eventMap = createMap();
    var eventMarker;
    var zoom;

    L.DomUtil.addClass(eventMap._container, 'crosshair-cursor-enabled');

    if (action === 'create') {
        zoom = 6;
    }
    else if (action === 'update') {
        zoom = 15;
        eventMarker = L.marker([lat, lng]).addTo(eventMap);
    }

    eventMap.setView([lat, lng], zoom);

    function onMapClick(e) {
        $('#id_latitude').val((e.latlng.lat).toFixed(7));
        $('#id_longitude').val((e.latlng.lng).toFixed(7));
        if (eventMarker === undefined) {
            eventMarker = L.marker(e.latlng);
            eventMarker.addTo(eventMap);
        }
        else {
            eventMarker.setLatLng(e.latlng);
        }
        eventMarker.bindPopup('Event location').openPopup();
    }

    eventMap.on('click', onMapClick);
}

var events;
var eventsMap;
var calendar;

function getEvents() {
    var newEvents = [];
    var lat;
    var lon;
    var title;
    var desc;
    var url;
    var start;
    var created_by;

    var rows = $('.events > .row:not([data-old])');

    $(rows).find('.event').each(function () {
        var latlon = $(this).find('#data-latlon');
        lat = $(latlon).attr('data-lat');
        lon = $(latlon).attr('data-lon');
        var urlTitle = $(this).find('#data-url-title');
        title = $(urlTitle).attr('title');
        url = $(urlTitle).attr('href');
        desc = $(this).find('#data-desc').text();
        start = $(this).find('#data-start-date').attr('data-start-date');
        created_by = $(this).find('#data-username').text();
        newEvents.push({lat: lat, lon: lon, title: title, desc: desc, url: url, start: start, created_by: created_by});
    });

    $(rows).each(function () {
       $(this).attr('data-old', 'true');
    });

    return newEvents;
}

function setEvents() {
    events = getEvents();
}

function updateMapCalEvents() {
    var newEvents = getEvents();
    events = $.extend([], events, newEvents);
    if (eventsMap) {
        addMarkers(newEvents);
    }

    if (calendar) {
        $('#calendar').fullCalendar('renderEvents', newEvents, true);
    }
}

function addMarkers(events) {
    if (eventsMap) {
        events.forEach(function (event) {
            if (event.lat !== 'None' && event.lon !== 'None') {
                var marker = L.marker([event.lat, event.lon], {title: event.title});
                var divTitle = '<div>'+ event.title +'</div><br><div>'+ event.created_by +'</div><br>';
                var content = divTitle + '<a href="' + event.url + '">URL</a>';
                marker.addTo(eventsMap).bindPopup(content);
                marker.on('mouseover', function (e) {
                            this.openPopup();
                        });
            }
        });
    }
}

function initAndSetEventsMap() {
    var lat = 52.069167;
    var lng = 19.480556;
    var zoom = 4;
    eventsMap = createMap();
    eventsMap.setView([lat, lng], zoom);
    addMarkers(events);
}

function loadEventsMap() {
    if (eventsMap) {
        eventsMap.invalidateSize();
    }
    else {
        initAndSetEventsMap();
    }
}

function initAndSetCalendar() {
    if (!calendar) {
        $('#calendar').fullCalendar({
            locale: 'en-gb',
            header: {
                left: 'prev,next today',
                center: 'title',
                right: 'month,agendaWeek,agendaDay,listMonth'
            },
            firstDay: 1,
            height: 450,
            events: events,
            eventMouseover: function (event, jsEvent, view) {
                console.log(event.title);
            },
            eventRender: function (event, element) {
                $(element).popover({
                    container: 'body',
                    title: event.title,
                    content: event.description,
                    trigger: 'hover',
                    placement: 'top'
                });
            },
        });
    calendar = true;
    }
}

function mapCalSwitchBtnClickInit() {
    $('#showMapBtn').on('click', function () {
        $("#theCal").hide();
        $("#theMap").show();
        $(this).addClass("active");
        $('#showCalBtn').removeClass("active");
        loadEventsMap();
    });

    $('#showCalBtn').on('click', function () {
        $("#theMap").hide();
        $("#theCal").show();
        $(this).addClass("active");
        $('#showMapBtn').removeClass("active");
        initAndSetCalendar();

    });
}

function mapCalBtnClickInit(mapCalHidden) {
    $('#mapCalBtn').on('click', function () {
        if (mapCalHidden.is(':visible')) {
            mapCalHidden.hide();
            $(this).html('<span class="glyphicon glyphicon-chevron-down" aria-hidden="true"></span> Map / Calendar <span class="glyphicon glyphicon-chevron-down" aria-hidden="true"></span>');
        }
        else {
            mapCalHidden.show();
            $(this).html('<span class="glyphicon glyphicon-chevron-up" aria-hidden="true"></span> Map / Calendar <span class="glyphicon glyphicon-chevron-up" aria-hidden="true"></span>');
            loadEventsMap();
        }
    });
}

function mainMapCalInit() {
    setEvents();
    mapCalBtnClickInit($('#mapCalHidden'));
    mapCalSwitchBtnClickInit();
}