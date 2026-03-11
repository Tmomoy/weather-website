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

document.getElementById("cityInput").value=city

document.querySelector("form").submit()

})

})

}


let chart

function draw(data,label,color){

const ctx=document.getElementById("chart")

if(!ctx)return

if(chart){

chart.destroy()

}

chart=new Chart(ctx,{

type:'line',

data:{

labels:times,

datasets:[{

label:label,

data:data,

borderColor:color,

backgroundColor:color,

tension:0.4

}]

}

})

}


function showTemp(){

draw(temps,"溫度","#ff5733")

}

function showRain(){

draw(rains,"降雨","#3498db")

}

function showHum(){

draw(hum,"濕度","#2ecc71")

}