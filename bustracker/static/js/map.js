/* 
 * map.js
 * TrackMyBus
 */

var map;

function initialize() {
	var myOptions = {
		mapTypeId: google.maps.MapTypeId.ROADMAP,
		disableDefaultUI: true,
	};
	map = new google.maps.Map(document.getElementById('map'), myOptions);
	
	plotUserLocation();
	
	$.get("/map", function(data) {
		map.setZoom(data.zoom);
		map.setCenter(new google.maps.LatLng(data.lat, data.lon));
		
		google.maps.event.addListener(map, 'center_changed', function() {
			$.post("/map", { "zoom": map.getZoom(), "lat": map.getCenter().lat(), "lon": map.getCenter().lng() });
		});
		
		google.maps.event.addListener(map, 'zoom_changed', function() {
			$.post("/map", { "zoom": map.getZoom(), "lat": map.getCenter().lat(), "lon": map.getCenter().lng() });
		});
		
		
	}, 'json');
}

function plotUserLocation() {
	if (navigator.geolocation) // check if browser support this feature or not
	{
		navigator.geolocation.getCurrentPosition(function(position)
			{
				  var lat = position.coords.latitude;
				  var lng = position.coords.longitude;
				  lat = 37.81154;
				  lng = -122.27744;
				  
				  var locationCircle = new google.maps.Circle({
						strokeColor: "#FFAD29",
						strokeOpacity: 0.8,
						strokeWeight: 2,
						fillColor: "#000000",
						fillOpacity: 0.2,
						map: map,
						center: new google.maps.LatLng(lat, lng),
						radius: 200 * (20/map.zoom)
					});
			 }
		);
	}
}

google.maps.event.addDomListener(window, 'load', initialize);