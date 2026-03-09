from flask import Flask, render_template, request
import requests
from taiwan_districts import districts, district_city_map

app = Flask(__name__)

API_KEY = "CWA-163D1E42-4393-42FE-8302-6E96BAB2974A"

@app.route("/", methods=["GET","POST"])
def index():

    weather=None
    forecast=[]
    temps=[]
    times=[]

    if request.method=="POST":

        search=request.form.get("city","").strip()

        if search in district_city_map:
            city=district_city_map[search]
        else:
            city=search

        url="https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001"

        params={
            "Authorization":API_KEY,
            "locationName":city
        }

        r=requests.get(url,params=params)
        data=r.json()

        try:

            location=data["records"]["location"][0]

            weather={
                "city":search,
                "wx":location["weatherElement"][0]["time"][0]["parameter"]["parameterName"],
                "rain":location["weatherElement"][1]["time"][0]["parameter"]["parameterName"],
                "temp":location["weatherElement"][2]["time"][0]["parameter"]["parameterName"]
            }

            times_data=location["weatherElement"][0]["time"]

            for i,t in enumerate(times_data):

                temp=location["weatherElement"][2]["time"][i]["parameter"]["parameterName"]
                rain=location["weatherElement"][1]["time"][i]["parameter"]["parameterName"]

                forecast.append({
                    "start":t["startTime"][5:16],
                    "wx":t["parameter"]["parameterName"],
                    "temp":temp,
                    "rain":rain
                })

                temps.append(int(temp))
                times.append(t["startTime"][11:16])

        except:
            weather=None

    return render_template(
        "index.html",
        weather=weather,
        forecast=forecast,
        temps=temps,
        times=times,
        districts=districts
    )

if __name__=="__main__":
    app.run(debug=True)