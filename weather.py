import requests
import json

class WeatherAPI():
    """
    気象情報API処理

    Parameters
    -----------
    jsonpath : str
        appid、位置情報が記述されたjsonのファイルパス
        jsonには以下のよう記述
        {
            "yj_appid" : "Yahoo WebAPIのid",
            "ow_key" : "OpenWeatherMapのキー",
            "zip" : "郵便番号"
        }

    """
    def __init__(self, jsonpath):

        with open(jsonpath, 'r') as cf:
            config = json.load(cf)
        self.yj_appid = config["yj_appid"]
        self.ow_key = config["ow_key"]
        self.zip = config["zip"]
        self.longitude = None
        self.latitude = None

    def zipsearch(self):
        """
        郵便番号検索から緯度経度取得
        """

        # パラメーター
        payload = {
            "appid" : self.yj_appid,
            "output" : 'json',
            "query": self.zip
        }

        # リクエスト
        r = requests.get("https://map.yahooapis.jp/search/zip/V1/zipCodeSearch", params=payload)

        # レスポンスを読み取り
        data = r.json()

        # 緯度、経度を抽出
        coordinates = data["Feature"][0]["Geometry"]["Coordinates"].split(',')
        
        self.longitude = coordinates[0]
        self.latitude = coordinates[1]

    def get(self):
        """
        天気・降水量取得
        """

        # OpenWeatherMap リクエストパラメーター
        ow_payload = {
            "zip" : self.zip + ',JP',
            "APPID" : self.ow_key
        }

        # リクエスト
        ow_r = requests.get("http://api.openweathermap.org/data/2.5/weather", params=ow_payload)

        # レスポンスを読み取り
        ow_data = ow_r.json()

        weather = ow_data["weather"][0]["main"]


        # 郵便番号から経度、緯度を抽出
        self.zipsearch()

        # YOLPリクエストパラメーター
        yh_payload = {
            "appid" : self.yj_appid,   # Client ID
            "output" : 'json',      # 出力方式
            "coordinates" : self.longitude + ',' + self.latitude    # 位置情報(経度, 緯度)
        }

        # リクエスト
        yh_r = requests.get("https://map.yahooapis.jp/weather/V1/place", params=yh_payload)

        # レスポンスを読み取り
        yh_data = yh_r.json()

        # 降水量を抽出
        weather_list = yh_data['Feature'][0]['Property']['WeatherList']['Weather']
        precipitation = weather_list[0]['Rainfall']

        rt_data = {
            "weather" : weather,
            "precipitation" : precipitation
        }

        return rt_data


if __name__ == '__main__':
    weatherapi = WeatherAPI("config.json")
    print(weatherapi.get())
