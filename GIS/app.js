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
