/* 
 * map.js
 * TrackMyBus
 */

var map;
var saveMapDefaultsTimer;

function initialize() {

	window.onresize = layoutFooter;

	var myOptions = {
		disableDefaultUI: true,
	};
	map = new google.maps.Map(document.getElementById('map'), myOptions);
	
	$.get("/map", function(data) {
		map.setZoom(data.zoom);
		map.setCenter(new google.maps.LatLng(data.lat, data.lon));
		setMapType(data.mapType);
		
		google.maps.event.addListener(map, 'center_changed', function() {
			clearTimeout(saveMapDefaultsTimer);
			saveMapDefaultsTimer = window.setTimeout(saveMapDefaults, 2000);
		});
		
		google.maps.event.addListener(map, 'zoom_changed', function() {
			clearTimeout(saveMapDefaultsTimer);
			saveMapDefaultsTimer = window.setTimeout(saveMapDefaults, 2000);
		});
		
		plotUserLocation();
		layoutFooter();
		
	}, 'json');
}

function layoutFooter() {
	var windowHeight = $(window).height();
	var wrapperHeight = document.getElementById("wrapper").scrollHeight;
	if (wrapperHeight == windowHeight) {
		//$("#footer").css("position", "absolute");
		//$("#footer").css("bottom", "0");
	}
	else if (wrapperHeight > windowHeight) {
		//$("#footer").css("position", "relative");
	}
}

function setMapType(mapType) {
	if (mapType == "roadmap") {
		map.setMapTypeId(google.maps.MapTypeId.ROADMAP);
	}
	else {
		map.setMapTypeId(google.maps.MapTypeId.SATELLITE);
	}
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
			
			var image = new google.maps.MarkerImage('/images/user-location.png',
				null, // size
				new google.maps.Point(0,0), // origin
				new google.maps.Point(15, 23) // anchor
			);
			
			var locationPoint = new google.maps.Marker({
				position: new google.maps.LatLng(lat, lng),
				map: map,
				icon: image
			});
		});
	}
}

google.maps.event.addDomListener(window, 'load', initialize);