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

var map = L.map('map'),
    clusterGroup = L.markerClusterGroup().addTo(map),
    realtime = createRealtimeLayer('http://localhost:8000/ships.geojson', clusterGroup).addTo(map);

realtime.once('update', function() {
    map.fitBounds(realtime.getBounds(), {maxZoom: 3});
});

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

