from flask import Flask, render_template, request
import requests
from taiwan_districts import districts, district_city_map

app = Flask(__name__)

API_KEY = "CWA-163D1E42-4393-42FE-8302-6E96BAB2974A"


@app.route("/", methods=["GET","POST"])
def index():

    weather=None
    temps=[]
    times=[]

    if request.method=="POST":

        search=request.form.get("city","").strip()

        display_name=search

        # 行政區轉縣市
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
                "city":display_name,
                "wx":location["weatherElement"][0]["time"][0]["parameter"]["parameterName"],
                "rain":location["weatherElement"][1]["time"][0]["parameter"]["parameterName"],
                "temp":location["weatherElement"][2]["time"][0]["parameter"]["parameterName"]
            }

            # 模擬溫度曲線資料
            temps=[weather["temp"],weather["temp"],weather["temp"]]
            times=["現在","12小時","24小時"]

        except:

            weather=None

    return render_template(
        "index.html",
        weather=weather,
        temps=temps,
        times=times,
        districts=districts
    )


if __name__=="__main__":
    app.run(debug=True)