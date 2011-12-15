/* 
 * map.js
 * TrackMyBus
 */

var map;
var saveMapDefaultsTimer;

function initialize() {
	var myOptions = {
		mapTypeId: google.maps.MapTypeId.ROADMAP,
		disableDefaultUI: true,
	};
	map = new google.maps.Map(document.getElementById('map'), myOptions);
	
	$.get("/map", function(data) {
		map.setZoom(data.zoom);
		map.setCenter(new google.maps.LatLng(data.lat, data.lon));
		
		google.maps.event.addListener(map, 'center_changed', function() {
			clearTimeout(saveMapDefaultsTimer);
			saveMapDefaultsTimer = window.setTimeout(saveMapDefaults, 2000);
		});
		
		google.maps.event.addListener(map, 'zoom_changed', function() {
			clearTimeout(saveMapDefaultsTimer);
			saveMapDefaultsTimer = window.setTimeout(saveMapDefaults, 2000);
		});
		
		plotUserLocation();
		
	}, 'json');
}

function saveMapDefaults() {
	$.post("/map", { "zoom": map.getZoom(), "lat": map.getCenter().lat(), "lon": map.getCenter().lng() });
}

function plotUserLocation() {
	if (navigator.geolocation) { // check if browser support this feature or not 
		navigator.geolocation.getCurrentPosition(function(position) {
			var lat = position.coords.latitude;
			var lng = position.coords.longitude;
			lat = 37.750695935238916;
			lng = -122.4302528878357;
			
			var locationCircle = new google.maps.Circle({
				strokeColor: "#FFAD29",
				strokeOpacity: 0.8,
				strokeWeight: 2,
				fillColor: "#000000",
				fillOpacity: 0.2,
				map: map,
				center: new google.maps.LatLng(lat, lng),
				radius: 300
			});
			
			var locationPoint = new google.maps.Circle({
				strokeColor: "#FFFFFF",
				strokeOpacity: 1,
				strokeWeight: 2,
				fillColor: "#5CE1FF",
				fillOpacity: 1,
				map: map,
				center: new google.maps.LatLng(lat, lng),
				radius: 15
			});
		});
	}
}

google.maps.event.addDomListener(window, 'load', initialize);