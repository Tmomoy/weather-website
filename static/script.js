function gps(){

navigator.geolocation.getCurrentPosition(function(pos){

let lat=pos.coords.latitude
let lon=pos.coords.longitude

alert("GPS定位成功\nLat:"+lat+"\nLon:"+lon)

})

}