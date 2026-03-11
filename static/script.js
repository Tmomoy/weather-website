function gps(){

if(!navigator.geolocation){
alert("瀏覽器不支援GPS")
return
}

navigator.geolocation.getCurrentPosition(function(pos){

let lat=pos.coords.latitude
let lon=pos.coords.longitude

fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}`)

.then(res=>res.json())

.then(data=>{

let city=
data.address.city ||
data.address.town ||
data.address.county ||
data.address.state

city=city.replace("台","臺")

document.getElementById("cityInput").value=city

document.querySelector("form").submit()

})

})

}


function mapWeather(){

let city=prompt("請輸入城市名稱")

if(city){

document.getElementById("cityInput").value=city

document.querySelector("form").submit()

}

}