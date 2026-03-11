from flask import Flask, render_template, request
import requests
import urllib3
from taiwan_districts import districts, district_city_map

urllib3.disable_warnings()

app = Flask(__name__)

API_KEY="CWA-163D1E42-4393-42FE-8302-6E96BAB2974A"


@app.route("/")
def home():
    return render_template("index.html", districts=districts)


@app.route("/weather",methods=["POST"])
def weather():

    search=request.form.get("city","").strip()

    if search in district_city_map:
        city=district_city_map[search]
    else:
        city=search

    city=city.replace("台","臺")

    if not city.endswith("市") and not city.endswith("縣"):

        if city in ["臺北","新北","桃園","臺中","臺南","高雄","基隆","新竹","嘉義"]:
            city+="市"
        else:
            city+="縣"

    url="https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-D0047-091"

    params={
        "Authorization":API_KEY,
        "locationName":city
    }

    forecast=[]
    temps=[]
    rains=[]
    humidity=[]
    times=[]

    weather={
        "city":city,
        "wx":"查詢不到資料",
        "temp":"--",
        "rain":"--"
    }

    try:

        r=requests.get(url,params=params,verify=False,timeout=10)

        data=r.json()

        location=data["records"]["locations"][0]["location"][0]

        elements=location["weatherElement"]

        temp_data=elements[3]["time"]
        rain_data=elements[7]["time"]
        hum_data=elements[1]["time"]
        wx_data=elements[6]["time"]

        weather={
            "city":city,
            "wx":wx_data[0]["elementValue"][0]["value"],
            "temp":temp_data[0]["elementValue"][0]["value"],
            "rain":rain_data[0]["elementValue"][0]["value"]
        }

        for i in range(min(8,len(temp_data))):

            t=temp_data[i]["startTime"]

            temp=temp_data[i]["elementValue"][0]["value"]
            rain=rain_data[i]["elementValue"][0]["value"]
            hum=hum_data[i]["elementValue"][0]["value"]

            forecast.append({
                "time":t[5:10],
                "temp":temp,
                "rain":rain,
                "hum":hum
            })

            temps.append(int(temp))
            rains.append(int(rain))
            humidity.append(int(hum))
            times.append(t[11:16])

    except Exception as e:

        print("Weather API error:",e)

    return render_template(
        "result.html",
        weather=weather,
        forecast=forecast,
        temps=temps,
        rains=rains,
        humidity=humidity,
        times=times
    )


if __name__=="__main__":
    app.run(host="0.0.0.0",port=10000)