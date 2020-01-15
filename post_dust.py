import pigpio
import requests, json
import dustsensor

def post(data, configjson):
    # GAS
    headers = {
        'Accept': 'application/json',
        'Content-type': 'application/json',
    }

    with open(configjson, 'r') as cf:
            config = json.load(cf)

    response = requests.post(config["dustlog"], headers=headers, data=json.dumps(data))

if __name__ == "__main__":
    pi = pigpio.pi()
    ds = dustsensor.DustSensor(pi, 14)
    post(ds.output(), "config.json")
