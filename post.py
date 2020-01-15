import requests
import json
import pigpio
from sensor import *
import weather

def post():
    """
    POST
    センサ値を取得し、WebAPIにPOST
    同階層に以下を記述した'config.json'を用意
    {
        "token" : "POST先のtoken",
        "posturl" : "POSTするURL",
        "yj_appid" : "Yahoo WebAPIのid",
        "ow_key" : "OpenWeatherMapのキー",
        "zip" : "郵便番号 xxx-xxxx"
    } 
    """

    pi = pigpio.pi()

    # BME280
    bme = bme280.BME280(pi)
    bme.setup()
    bme_data = bme.output()
    #print(bme_data)

    # ダストセンサー
    dust = dustsensor.DustSensor(pi)
    dust_data = dust.output()
    #print(dust_data)

    # 雨センサー
    rain = rainsensor.RainSensor(pi)
    rain_data = rain.output()
    #print(rain_data)

    # 気象予報取得
    wh = weather.WeatherAPI('config.json')
    wh_data = wh.get()

    # POSTするURL, tokenを読み込み
    with open('config.json', 'r') as cf:
        config = json.load(cf)

    headers = {
        'Accept': 'application/json',
        'Content-type': 'application/json',
    }

    # POSTするデータ
    data = {
        "token": config["token"],                       # access token
        "type": "update",       # 処理の種類 (update)
        "ratio": str(dust_data["ratio"]),       # ホコリの比率[%]
        "concent": str(dust_data["concentration"]),       # ホコリの濃度[pcs/0.01cf]
        "temp": str(bme_data["temp"]),        # 気温[℃]
        "humid": str(bme_data["humid"]),            # 湿度[%]
        "press": str(bme_data["press"]),            # 気圧[hPa]
        "light": "",            # 明るさ
        "wind": "",             # 風が強いか(bool)
        "rain": str(rain_data),             # 雨(センサ, bool)
        "weather": str(wh_data["weather"]),          # 現在の天気
        "precipitation": str(wh_data["precipitation"])     # 降水量(数値)

    }

    # POST
    response = requests.post(config["posturl"], headers=headers, data=json.dumps(data))
    #print(data)

if __name__ == "__main__":
    post()
