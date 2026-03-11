from flask import Flask, render_template, request
import requests
import os
import urllib3

urllib3.disable_warnings()

app = Flask(__name__)

CWA_KEY = "CWA-163D1E42-4393-42FE-8302-6E96BAB2974A"

# 22縣市
CITIES = [
"臺北市","新北市","桃園市","臺中市","臺南市","高雄市",
"基隆市","新竹市","嘉義市",
"新竹縣","苗栗縣","彰化縣","南投縣","雲林縣","嘉義縣",
"屏東縣","宜蘭縣","花蓮縣","臺東縣",
"澎湖縣","金門縣","連江縣"
]


@app.route("/")
def home():
    return render_template("index.html",cities=CITIES)


@app.route("/weather",methods=["POST"])
def weather():

    city=request.form.get("city","臺北市")

    city=city.replace("台","臺")

    if not city.endswith("市") and not city.endswith("縣"):
        city+="市"

    weather={"city":city,"wx":"--","temp":"--","rain":"--"}

    forecast=[]
    temps=[]
    rains=[]
    humidity=[]
    times=[]

    try:

        url="https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001"

        params={
            "Authorization":CWA_KEY,
            "locationName":city
        }

        # 唯一修改的地方
        r=requests.get(url,params=params,timeout=10,verify=False)

        data=r.json()

        location=data["records"]["location"][0]

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

    except:
        pass

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

    port=int(os.environ.get("PORT",10000))

    app.run(host="0.0.0.0",port=port)