const ws_client_id = Date.now();

function addCommas(num) {
  let numString = num.toString();
  let lastThree = numString.match(/\d{1,3}(?=(\d{3})+$)/);
  while (lastThree) {
    numString = numString.replace(lastThree[0], lastThree[0] + ",");
    lastThree = numString.match(/\d{1,3}(?=(\d{3})+$)/);
  }
  return numString;
}

function onEachFeatureShips(feature, layer) {
  layer.bindPopup(function () {
    return (
      "<h2 style='text-align: center;'><strong>Detection " +
      feature.properties.id +
      "</strong></h2>" +
      "<p><strong>Acquisition time: </strong>" +
      feature.properties.acquisition_time +
      "</p>" +
      "<p><img src='/images/cargo_ship.jpg' alt='Picture of a cargo' width='100%' height='150'/></p>" +
      "<h3><strong>Position:</strong></h3>" +
      "<p style='text-align: center;'><strong>Longitude: </strong>" +
      feature.geometry.coordinates[0].toFixed(2) +
      " deg&nbsp;&nbsp;&nbsp;&nbsp; <strong>Latitude: </strong>" +
      feature.geometry.coordinates[1].toFixed(2) +
      " deg</p>" +
      "<h3 style='text-align: left;'><strong>Characteristics:</strong></h3>" +
      "<p style='text-align: center;'><strong>Width: </strong>" +
      feature.properties.width +
      " meters &nbsp;&nbsp;&nbsp; <strong>Length: </strong>" +
      feature.properties.length +
      " meters</p>"
    );
  });
}

function onEachFeaturePorts(feature, layer) {
  layer.bindPopup(function () {
    return (
      "<h2 style='text-align: center;'><strong>Port " +
      feature.properties.name +
      "</strong></h2>" +
      "<p style='text-align: center;'><strong>Country: </strong>" +
      feature.properties.country +
      "&nbsp;&nbsp;&nbsp;&nbsp;<strong>LOCODE: </strong>" +
      feature.properties.locode +
      "</p>" +
      "<p><img src='/images/port.jpg' alt='Picture of a port' width='100%' height='150'/></p>" +
      "<h3><strong>Position:</strong></h3>" +
      "<p style='text-align: center;'><strong>Longitude: </strong>" +
      feature.geometry.coordinates[0].toFixed(2) +
      " deg&nbsp;&nbsp;&nbsp;&nbsp; <strong>Latitude: </strong>" +
      feature.geometry.coordinates[1].toFixed(2) +
      " deg</p>" +
      "<h3 style='text-align: left;'><strong>Characteristics:</strong></h3>" +
      "<p style='text-align: center;'><strong>Outflows: </strong>" +
      addCommas(feature.properties.outflows.toFixed(0)) +
      " TEU for Q1 of 2020</p>"
    );
  });
}

function getDates() {
  const fromInput = document.getElementById("from");
  const toInput = document.getElementById("to");

  return { from: fromInput.value, to: toInput.value };
}

function createStringForURLParameters() {
  const range = getDates();

  const searchParams = new URLSearchParams();
  searchParams.set("start_date", range.from);
  searchParams.set("end_date", range.to);
  searchParams.set("client_id", ws_client_id.toString());
  return searchParams.toString();
}

function setButtonState(activate) {
  document.getElementById("export").disabled = !activate;
  document.getElementById("analysis").disabled = !activate;
}

// Initialize the map -------------------------------------------------------------------

var southWest = L.latLng(-90, -180),
  northEast = L.latLng(90, 180),
  bounds = L.latLngBounds(southWest, northEast);

// Initialize the base layers
var googleHybrid = L.tileLayer(
  "https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
  {
    attribution: "Google Satellite Hybrid",
  },
);

var osm = L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
  maxZoom: 19,
  attribution: "© OpenStreetMap",
});

var map = L.map("map", {
  center: [0, 0],
  zoom: 2,
  maxZoom: 18,
  minZoom: 2,
  maxBounds: bounds,
  layers: [osm, googleHybrid],
});

var clusterGroup = L.markerClusterGroup();

var baseMaps = {
  GoogleSatelliteHybrid: googleHybrid,
  OpenStreetmap: osm,
};

var overlayMaps = { Ships: clusterGroup };

var layerControl = L.control.layers(baseMaps, overlayMaps).addTo(map);

L.control
  .coordinates({
    position: "bottomleft",
    decimals: 2,
    decimalSeparator: ",",
    labelTemplateLat: "Latitude: {y}",
    labelTemplateLng: "Longitude: {x}",
  })
  .addTo(map);

L.control
  .scale({
    position: "bottomleft",
    metrics: true,
    imperial: false,
  })
  .addTo(map);

L.control
  .worldMiniMap({
    position: "bottomright",
    style: {
      opacity: 0.9,
      borderRadius: "0px",
      backgroundColor: "lightblue",
    },
  })
  .addTo(map);

// Initialize date form -----------------------------------------------------------------

// Get the input elements
var fromInput = document.getElementById("from");
var toInput = document.getElementById("to");

// Get today's date or local storage
var endDate = new Date();
var startDate = new Date(endDate);
startDate.setDate(endDate.getDate() - 5);

// Format the date as a string in the "yyyy-mm-dd" format
var endDateString =
  endDate.getFullYear() +
  "-" +
  (endDate.getMonth() + 1).toString().padStart(2, "0") +
  "-" +
  endDate.getDate().toString().padStart(2, "0");
var startDateString =
  startDate.getFullYear() +
  "-" +
  (startDate.getMonth() + 1).toString().padStart(2, "0") +
  "-" +
  startDate.getDate().toString().padStart(2, "0");

// Set the value of the input elements to the formatted date string
fromInput.value = startDateString;
toInput.value = endDateString;

// Create url for server query ----------------------------------------------------------

const origin = window.location.origin;
const data_server_url = origin.replace(/:\d{4}/, ":9967") + "/";

// Boat detections

const url_ships = new URL(data_server_url + "ships.geojson");

url_ships.search = createStringForURLParameters();

function updateShips() {
  clusterGroup.clearLayers();

  const url = new URL(url_ships);
  url.search = createStringForURLParameters();

  $.ajax({
    url: url,
    type: "GET",
    dataType: "json",
    success: function (data) {
      L.geoJSON(data, {
        onEachFeature: onEachFeatureShips,
        pointToLayer: function (feature, latlng) {
          const marker = L.marker(latlng);
          clusterGroup.addLayer(marker);
          return marker;
        },
      });
      map.addLayer(clusterGroup);
    },
    error: function (xhr, status, error) {
      const message = JSON.parse(xhr.responseText).detail;
      alert(message);
    },
  });
}

// Ports

var searchParams = new URLSearchParams();
searchParams.set("number", 50);
var searchString = searchParams.toString();

const url_ports = new URL(data_server_url + "ports.geojson");

url_ports.search = searchString;

// Query server -------------------------------------------------------------------------

// Boat detections

updateShips();

// Ports

var maxOutflows = 0;

$.ajax({
  url: url_ports,
  type: "GET",
  dataType: "json",
  success: function (data) {
    for (var i = 0; i < data.features.length; i++) {
      var outflows = data.features[i].properties.outflows;
      if (outflows > maxOutflows) {
        maxOutflows = outflows;
      }
    }
    var geoJSONLayer = L.geoJSON(data, {
      pointToLayer: function (feature, latlng) {
        var outflows = feature.properties.outflows;
        var size = (outflows / maxOutflows) * 20;
        var marker = L.circleMarker(latlng, {
          radius: size,
          color: "red",
          weight: 1,
          fillOpacity: 0.8,
        });
        return marker;
      },
      onEachFeature: onEachFeaturePorts,
    });
    layerControl.addOverlay(geoJSONLayer, "Ports");
    map.addLayer(geoJSONLayer);
  },
  error: function (xhr, status, error) {
    console.log("Error: " + error);
  },
});

// Set up the WebSockets

const ws_data_server_url =
  data_server_url.replace(/http:\/\//, "ws://") + "ws/";
const ws = new WebSocket(ws_data_server_url + ws_client_id);

ws.onmessage = function (event) {
  if (event.data === "success") {
    setButtonState(true);
    return;
  }

  alert(event.data);
  setButtonState(true);
};

// Draw ---------------------------------------------------------------------------------

// FeatureGroup is to store editable layers
var drawnItems = new L.FeatureGroup();
map.addLayer(drawnItems);
map.addControl(
  new L.Control.Draw({
    draw: {
      marker: false,
      polygon: true,
      polyline: false,
      rectangle: true,
      circle: true,
    },
    edit: { featureGroup: drawnItems },
  }),
);

map.on("draw:created", function (e) {
  // Each time a feaute is created, delete previously existing features
  drawnItems.clearLayers();
  drawnItems.addLayer(e.layer);
});

// Analysis -----------------------------------------------------------------------------

const polygon_url = new URL(data_server_url + "polygon");

document.getElementById("analysis").onclick = function (e) {
  // Extract GeoJson from featureGroup
  const data = drawnItems.toGeoJSON();
  const parameters = createStringForURLParameters();
  let polygon_with_parameters = polygon_url;
  polygon_with_parameters.search = parameters;
  setButtonState(false);
  $.ajax({
    url: polygon_with_parameters,
    async: true,
    type: "post",
    dataType: "json",
    data: JSON.stringify(data),
    success: function (result) {},
    error: function (xhr, resp, text) {
      console.log(xhr, resp, text);
    },
  });
};

// Export -------------------------------------------------------------------------------

document.getElementById("export").onclick = function (e) {
  setButtonState(false);
  $.ajax({
    url: url_ships,
    async: true,
    type: "get",
    dataType: "text",
    data: "data_type=csv",
    success: function (result) {
      setButtonState(true);
      result = result.slice(1, result.length - 1);
      var lines = result.split("\\n");
      var items = [];
      var header = lines[0].split(",");
      for (var i = 1; i < lines.length; i++) {
        var obj = {};
        var currentline = lines[i].split(",");

        for (var j = 0; j < header.length; j++) {
          obj[header[j]] = currentline[j];
        }

        items.push(obj);
      }
      const csv = [
        header.join(","), // header row first
        ...items.map((row) =>
          header.map((fieldName) => JSON.stringify(row[fieldName])).join(","),
        ),
      ].join("\r\n");
      let csvContent = "data:text/csv;charset=utf-8," + csv;
      var encodedUri = encodeURI(csvContent);
      var link = document.createElement("a");
      link.setAttribute("href", encodedUri);
      link.setAttribute(
        "download",
        "detections_from_" + startDateString + "_to_" + endDateString + ".csv",
      );
      if (link.download !== undefined) {
        document.body.appendChild(link);
        link.click();
      } else {
        alert(
          "Your browser does not support automatic download, please click OK and manually save the file",
        );
        window.open(encodedUri);
      }
    },
    error: function (xhr, resp, text) {
      console.log(xhr, resp, text);
    },
  });
};
