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