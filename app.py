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

    url="https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001"

    params={
        "Authorization":API_KEY,
        "locationName":city
    }

    forecast=[]
    temps=[]
    rains=[]
    humidity=[]
    times=[]

    weather=None

    try:

        r=requests.get(url,params=params,timeout=10,verify=False)
        data=r.json()

        location=data["records"]["location"][0]

        wx=location["weatherElement"][0]["time"][0]["parameter"]["parameterName"]
        rain=location["weatherElement"][1]["time"][0]["parameter"]["parameterName"]
        temp=location["weatherElement"][2]["time"][0]["parameter"]["parameterName"]

        weather={
            "city":city,
            "wx":wx,
            "temp":temp,
            "rain":rain
        }

        times_data=location["weatherElement"][2]["time"]

        for t in times_data:

            temp=t["parameter"]["parameterName"]

            forecast.append({
                "time":t["startTime"][5:16],
                "temp":temp
            })

            temps.append(int(temp))
            rains.append(int(rain))
            humidity.append(60)
            times.append(t["startTime"][11:16])

    except Exception as e:

        print("Weather API error:",e)

        weather={
            "city":city,
            "wx":"查詢不到資料",
            "temp":"--",
            "rain":"--"
        }

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