function gps(){

if(!navigator.geolocation){
alert("瀏覽器不支援GPS")
return
}

navigator.geolocation.getCurrentPosition(

function(pos){

let lat=pos.coords.latitude
let lon=pos.coords.longitude

fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}`)

.then(res=>res.json())

.then(data=>{

let address=data.address

let city=
address.city ||
address.town ||
address.county ||
address.state

if(!city){
alert("找不到城市")
return
}

city=city.replace("台","臺")

document.getElementById("cityInput").value=city

document.querySelector("form").submit()

})

.catch(()=>{
alert("定位解析失敗")
})

},

function(){
alert("GPS定位失敗")
}

)

}