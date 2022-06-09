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
      emptyDiv = document.getElementById('empty');
      garageInfo= JSON.parse(xhr.response)
      console.log(garageInfo)
      document.getElementById("a1").href = garageInfo["URL"];
      document.getElementById("p1").innerHTML = "Your nearest garage";
      data = 'Contact Details are: <br> ' + garageInfo["Name"] + '<br>' + garageInfo['Address']+ '<br>' + garageInfo["Phone"] + '<br>'

      if(garageInfo["Person"]=="Yes"){
        data += "Vehicle Pickup: Available";
      }
      else{
        data += "Vehicle Pickup: Not Available";
      }

      emptyDiv.innerHTML= data; 

    }
  }
}
