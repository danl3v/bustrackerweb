/* 
 * map.js
 * TrackMyBus
 */

var map;

function initialize() {
	var myOptions = {
		zoom: 18,
		center: new google.maps.LatLng(37.81154, -122.27744),
		mapTypeId: google.maps.MapTypeId.SATELLITE,
		disableDefaultUI: true,
	};
	map = new google.maps.Map(document.getElementById('map'), myOptions);
}

google.maps.event.addDomListener(window, 'load', initialize);