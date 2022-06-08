console.log("connected")

var x = document.getElementById("demo");

function getLocation() {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(showPosition);
  } else { 
    x.innerHTML = "Geolocation is not supported by this browser.";
  }
}

function showPosition(position) {

  let sender = {
    'Latitude':position.coords.latitude, 
    'Longitude':position.coords.longitude,
  }

  sender = JSON.stringify(sender);
  console.log(sender)
  const xhr = new XMLHttpRequest();
  const URL = '/get-coordinates/' + sender

  xhr.open('POST', URL);
  xhr.send(sender);

  xhr.onreadystatechange = function() {
    if (xhr.readyState === 4) {
      document.getElementById("a1").href = xhr.response;
      document.getElementById("p1").innerHTML = "Your nearest garage";

    }
  }
}
