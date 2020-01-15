import pigpio
import time

class DustSensor():
    """
    ダストセンサー

    Parameters
    -----------
    pi : pigpio.pi()
        pigpioのインスタンス
    """
    def __init__(self, pi, pin=14):
        self.starttime = 0
        self.sampling = 30
        self.low_duration = 0
        self.low_occupancy = 0
        self.ratio = 0
        self.concentration = 0
        
        self.pin = pin
        self.pi = pi
        self.pi.set_mode(self.pin, pigpio.INPUT)

    def pulse(self):
        low_start = time.time()
        low_end = low_start

        # LOWになるまで待機
        while self.pi.read(self.pin) == 1:
            low_start = time.time()

        # 次にHIGHになるまで待機
        while self.pi.read(self.pin) == 0:
            low_end = time.time()

        low_duration = low_end - low_start
        
        # LOW信号が一瞬だけ入力された場合、負の値になるので0にする
        if low_duration < 0:
            low_duration = 0

        # LOWの時間を返す
        return low_duration

    def output(self):
        self.starttime = time.time()

        while 1:
            self.low_duration = self.pulse()
            #print(self.low_duration)
            self.low_occupancy += self.low_duration

            if (time.time() - self.starttime) > self.sampling:
                self.ratio = (self.low_occupancy * 100) / self.sampling
                self.concentration = 1.1 * pow(self.ratio, 3) - 3.8 * pow(self.ratio, 2) + 520 * self.ratio + 0.62
                
                dust_data = {
                    "ratio": self.ratio,
                    "concentration": self.concentration
                }

                return dust_data
            

if __name__ == "__main__":
    pi = pigpio.pi()
    dustsensor = DustSensor(pi, 14)
    print(dustsensor.output())
