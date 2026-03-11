from flask import Flask, render_template, request
import requests
import os

app = Flask(__name__)

API_KEY="CWA-163D1E42-4393-42FE-8302-6E96BAB2974A"


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/weather",methods=["POST"])
def weather():

    city=request.form.get("city","臺北市")

    url="https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001"

    params={
        "Authorization":API_KEY,
        "locationName":city
    }

    weather={
        "city":city,
        "wx":"--",
        "temp":"--",
        "rain":"--"
    }

    forecast=[]
    temps=[]
    rains=[]
    humidity=[]
    times=[]

    try:

        r=requests.get(url,params=params,timeout=10)
        data=r.json()

        location=data["records"]["location"][0]

        wx_data=location["weatherElement"][0]["time"]
        rain_data=location["weatherElement"][1]["time"]
        temp_data=location["weatherElement"][2]["time"]

        weather={
            "city":city,
            "wx":wx_data[0]["parameter"]["parameterName"],
            "temp":temp_data[0]["parameter"]["parameterName"],
            "rain":rain_data[0]["parameter"]["parameterName"]
        }

        for i in range(len(temp_data)):

            time=temp_data[i]["startTime"][11:16]

            temp=temp_data[i]["parameter"]["parameterName"]
            rain=rain_data[i]["parameter"]["parameterName"]

            forecast.append({
                "time":time,
                "temp":temp,
                "rain":rain
            })

            temps.append(int(temp))
            rains.append(int(rain))
            humidity.append(60)
            times.append(time)

    except Exception as e:

        print("API error:",e)

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