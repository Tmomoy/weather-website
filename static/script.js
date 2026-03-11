function gps(){

navigator.geolocation.getCurrentPosition(function(pos){

let lat=pos.coords.latitude
let lon=pos.coords.longitude

fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}`)

.then(res=>res.json())
.then(data=>{

let city=data.address.city || data.address.county

document.getElementById("cityInput").value=city

})

})

}