function createRealtimeLayer(url, container) {
    return L.realtime(url, {
	interval: 60 * 1000,
	getFeatureId: function(f) {
	    return f.properties.id;
	},
	cache: true,
	container: container,
	onEachFeature(f, l) {
	    l.bindPopup(function() {
		return '<h3>' + f.properties.id + '</h3>' +
		    '<p>' + 'Shape: <strong>' + 'width: ' + f.properties.det_w + ', length: ' + f.properties.det_l + '</strong></p>' +
		    '<p>Position: '+ f.geometry.coordinates[0].toPrecision(6) + ', ' + f.geometry.coordinates[1].toPrecision(6) + '</p>';
	    });
	}
    });
}


// Initialize the map

var map = new L.map('map');

// Set the position and zoom level of the map
map.setView([2.5, 105], 8);

// Initialize the base layer
L.tileLayer('https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', {
    maxZoom: 19,
    attribution: 'Google Satellite Hybrid'
}).addTo(map);

L.control.scale({
    position: 'bottomleft',
    metrics: true,
    imperial: false
}).addTo(map);

L.control.worldMiniMap({
    position: 'bottomright',
    style: {
	 opacity: 0.9,
	 borderRadius: '0px',
	 backgroundColor: 'lightblue'
    }
}).addTo(map);

L.control.coordinates({
    position:"topright",
    decimals:2,
    decimalSeperator:",",
    labelTemplateLat:"Latitude: {y}",
    labelTemplateLng:"Longitude: {x}"
}).addTo(map);

ship_detections_gdf = {
    "type": "FeatureCollection",
    "features": [
	{ "type": "Feature", "properties": { "id": "target_000", "det_w": 170.0, "det_l": 280.0 }, "geometry": { "type": "Point", "coordinates": [ 105.107863101076106, 2.304856816223837 ] } },
	{ "type": "Feature", "properties": { "id": "target_001", "det_w": 90.0, "det_l": 270.0 }, "geometry": { "type": "Point", "coordinates": [ 104.949913965124253, 2.300581554599592 ] } },
	{ "type": "Feature", "properties": { "id": "target_002", "det_w": 90.0, "det_l": 280.0 }, "geometry": { "type": "Point", "coordinates": [ 104.940367656218783, 2.255528158519057 ] } },
	{ "type": "Feature", "properties": { "id": "target_003", "det_w": 160.0, "det_l": 270.0 }, "geometry": { "type": "Point", "coordinates": [ 104.902626654065756, 2.125021698527313 ] } },
	{ "type": "Feature", "properties": { "id": "target_004", "det_w": 150.0, "det_l": 280.0 }, "geometry": { "type": "Point", "coordinates": [ 104.856804584458772, 2.186240289818167 ] } },
	{ "type": "Feature", "properties": { "id": "target_005", "det_w": 40.0, "det_l": 50.0 }, "geometry": { "type": "Point", "coordinates": [ 105.027053169124144, 2.043287565639268 ] } },
	{ "type": "Feature", "properties": { "id": "target_006", "det_w": 140.0, "det_l": 170.0 }, "geometry": { "type": "Point", "coordinates": [ 104.964837066274328, 2.102232903699841 ] } },
	{ "type": "Feature", "properties": { "id": "target_007", "det_w": 160.0, "det_l": 220.0 }, "geometry": { "type": "Point", "coordinates": [ 104.902542538161427, 2.124617102528414 ] } },
	{ "type": "Feature", "properties": { "id": "target_008", "det_w": 170.0, "det_l": 280.0 }, "geometry": { "type": "Point", "coordinates": [ 104.918699372042425, 2.118181477767156 ] } },
	{ "type": "Feature", "properties": { "id": "target_009", "det_w": 30.0, "det_l": 30.0 }, "geometry": { "type": "Point", "coordinates": [ 104.907795705568148, 2.097543174922881 ] } },
	{ "type": "Feature", "properties": { "id": "target_010", "det_w": 280.0, "det_l": 250.0 }, "geometry": { "type": "Point", "coordinates": [ 104.933362559469572, 2.084695416065979 ] } }
    ]
};


var markers = L.markerClusterGroup();

for (var i = 0; i < ship_detections_gdf.features.length; i++) {
    c_ship = ship_detections_gdf.features[i].geometry.coordinates;
    var boatMarker = L.boatMarker(new L.LatLng(c_ship[1], c_ship[0]), {color: "#dddddd", idleCircle: true, inconSize: [12, 12]});
    markers.addLayer(boatMarker)
}

map.addLayer(markers);
