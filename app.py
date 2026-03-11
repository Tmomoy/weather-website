from flask import Flask, render_template, request
import requests
import os
import urllib3

from taiwan_districts import districts, district_city_map

urllib3.disable_warnings()

app = Flask(__name__)

CWA_KEY = "CWA-163D1E42-4393-42FE-8302-6E96BAB2974A"

CITIES = [
"臺北市","新北市","桃園市","臺中市","臺南市","高雄市",
"基隆市","新竹市","嘉義市",
"新竹縣","苗栗縣","彰化縣","南投縣","雲林縣","嘉義縣",
"屏東縣","宜蘭縣","花蓮縣","臺東縣",
"澎湖縣","金門縣","連江縣"
]


@app.route("/")
def home():
    return render_template("index.html", cities=CITIES)


@app.route("/weather", methods=["POST"])
def weather():

    search = request.form.get("city","").strip()

    # 368行政區 → 縣市
    if search in district_city_map:
        city = district_city_map[search]
    else:
        city = search

    city = city.replace("台","臺")

    if not city.endswith("市") and not city.endswith("縣"):

        if city in ["臺北","新北","桃園","臺中","臺南","高雄","基隆","新竹","嘉義"]:
            city += "市"
        else:
            city += "縣"


    weather={"city":city,"wx":"--","temp":"--","rain":"--"}

    forecast=[]
    forecast7=[]
    temps=[]
    rains=[]
    humidity=[]
    times=[]

    try:

        # -----------------------
        # 36小時預報
        # -----------------------
        url="https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001"

        params={
            "Authorization":CWA_KEY,
            "locationName":city
        }

        r=requests.get(url,params=params,verify=False,timeout=10)
        data=r.json()

        locations=data.get("records",{}).get("location",[])

        if locations:

            location=locations[0]

            wx=location["weatherElement"][0]["time"]
            rain=location["weatherElement"][1]["time"]
            temp=location["weatherElement"][2]["time"]

            weather={
                "city":city,
                "wx":wx[0]["parameter"]["parameterName"],
                "temp":temp[0]["parameter"]["parameterName"],
                "rain":rain[0]["parameter"]["parameterName"]
            }

            for i in range(len(temp)):

                t=temp[i]["startTime"][11:16]

                forecast.append({
                    "time":t,
                    "temp":temp[i]["parameter"]["parameterName"],
                    "rain":rain[i]["parameter"]["parameterName"]
                })

                temps.append(int(temp[i]["parameter"]["parameterName"]))
                rains.append(int(rain[i]["parameter"]["parameterName"]))
                humidity.append(60)
                times.append(t)


        # -----------------------
        # 7天預報 (修正版)
        # -----------------------

        url7="https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-D0047-091"

        params7={
            "Authorization":CWA_KEY,
            "locationName":city
        }

        r7=requests.get(url7,params=params7,verify=False,timeout=10)
        data7=r7.json()

        locations7=data7.get("records",{}).get("locations",[])

        if locations7:

            location_data=locations7[0].get("location",[])

            if location_data:

                loc=location_data[0]

                elements=loc["weatherElement"]

                wx7=[]
                temp7=[]

                for e in elements:

                    if e["elementName"]=="Wx":
                        wx7=e["time"]

                    if e["elementName"]=="T":
                        temp7=e["time"]

                for i in range(min(7,len(wx7),len(temp7))):

                    day=wx7[i]["startTime"][5:10]

                    forecast7.append({
                        "day":day,
                        "wx":wx7[i]["elementValue"][0]["value"],
                        "temp":temp7[i]["elementValue"][0]["value"]
                    })

    except Exception as e:
        print("Weather API error:",e)

    return render_template(
        "result.html",
        weather=weather,
        forecast=forecast,
        forecast7=forecast7,
        temps=temps,
        rains=rains,
        humidity=humidity,
        times=times
    )


if __name__=="__main__":

    port=int(os.environ.get("PORT",10000))

    app.run(host="0.0.0.0",port=port)