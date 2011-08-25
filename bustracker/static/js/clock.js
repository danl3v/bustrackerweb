function updateClock() {
  var currentTime = new Date();
  
  var dayArray = new Array("Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday");
  var monthArray = new Array("January","February","March","April","May","June","July","August","September","October","November","December");
  
  var currentYear = currentTime.getYear(); if (currentYear < 1000) { currentYear += 1900; }
  var currentMonth = currentTime.getMonth();
  var currentDate = currentTime.getDate();
  var currentDay = currentTime.getDay();
  
  var currentHours = currentTime.getHours();
  var currentMinutes = currentTime.getMinutes();
  var currentSeconds = currentTime.getSeconds();

  currentHours = (currentHours == 0) ? 12 : currentHours;
  currentMinutes = (currentMinutes < 10 ? "0" : "") + currentMinutes;
  currentSeconds = (currentSeconds < 10 ? "0" : "") + currentSeconds;

  var currentTimeString = dayArray[currentDay] + ", " + monthArray[currentMonth] + " " + currentDate + ", " + currentYear + " " + currentHours + ":" + currentMinutes + ":" + currentSeconds;

  document.getElementById("clock").innerHTML = currentTimeString;
  
  setTimeout("updateClock()", 1000);
}

$(document).ready(function() {
	updateClock();
});