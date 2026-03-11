function gps(){

if(!navigator.geolocation){
alert("GPS 不支援")
return
}

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