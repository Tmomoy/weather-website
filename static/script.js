function gps(){

navigator.geolocation.getCurrentPosition(function(pos){

let lat=pos.coords.latitude
let lon=pos.coords.longitude

fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}`)

.then(res=>res.json())

.then(data=>{

let city=data.address.city ||
data.address.town ||
data.address.county ||
data.address.state

document.getElementById("cityInput").value=city

document.querySelector("form").submit()

})

})

}


function mapCity(city){

document.getElementById("cityInput").value=city

document.querySelector("form").submit()

}


// 雷達動畫
setInterval(function(){

let radar=document.getElementById("radar")

if(radar){

radar.src="https://www.cwa.gov.tw/Data/radar/CV1_3600.png?"+Date.now()

}

},120000)