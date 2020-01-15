import pigpio
import time

class RainSensor():
    def __init__(self, pi, pin=13):
        self.pi = pi
        self.pin = pin
        self.pi.set_mode(self.pin, pigpio.INPUT)

    def output(self):
        data = self.pi.read(self.pin)
        
        if data == 1:
            data = 0
        elif data == 0:
            data = 1
        
        return data

if __name__ == "__main__":
    pi = pigpio.pi()
    rain = RainSensor(pi)
    print(rain.output())
