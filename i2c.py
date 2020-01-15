import pigpio, time
from sensor import *

pi = pigpio.pi()
bme = bme280.BME280(pi)
mma = mma8452.MMA8452(pi)

bme.setup()
mma.setup()

while 1:
    try:
        print(bme.output())
        print(mma.output())
    except KeyboardInterrupt:
        print("exit")
        break
    time.sleep(1)

