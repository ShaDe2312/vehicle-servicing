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
                var emptyDiv = document.getElementById("emptyDiv")
                var a = document.createElement('a'); 
                var link = document.createTextNode("Fill the rest of your profile");
                a.appendChild(link); 
                a.title = "Enter information"; 
                a.href = "http://127.0.0.1:5000/merchant-info"; 
                emptyDiv.innerHTML = "Your location was recorded successfully!<br><br>";
                emptyDiv.appendChild(a);
               
      // window.location.replace("");
    }
  }
}
