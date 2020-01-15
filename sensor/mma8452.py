import pigpio, time

BUS_NUMBER = 1
I2C_ADDRESS = 0x1d

class MMA8452():
    """
    加速度センサ MMA8452

    Parameters
    -----------
    pi : pigpio.pi()
        pigpioのインスタンス
    busnum : int
        Bus Number デフォルト: 1
    i2cadr : int
        MMA8452のアドレス(16進) デフォルト: 0x1d
    """

    def __init__(self, pi, busnum=BUS_NUMBER, i2cadr=I2C_ADDRESS):
        self.pi = pi
        self.i2c_address = i2cadr
        self.handle = self.pi.i2c_open(busnum, i2cadr)

    def setup(self):
        # コントロールレジスタ選択 (0x2a, 0x00: StandBy)
        self.pi.i2c_write_byte_data(self.handle, 0x2a, 0x00)
        
        # コントロールレジスタ選択 (0x2a, 0x01: Active)
        self.pi.i2c_write_byte_data(self.handle, 0x2a, 0x01)

        # 設定レジスタ選択 (0x0e, 0x00: Set Range +-2g)
        self.pi.i2c_write_byte_data(self.handle, 0x0e, 0x00) 

    def output(self):
        data = []
        # 必要データ取得
        for i in range(0x00, 0x00 + 7):
            data.append(self.pi.i2c_read_byte_data(self.handle, i))
        
        # x軸
        xAccl = (data[1] * 256 + data[2]) / 16
        if xAccl > 2047:
            xAccl -= 4096

        # y軸
        yAccl = (data[3] * 256 + data[4]) / 16
        if yAccl > 2047:
            yAccl -= 4096

        # z軸
        zAccl = (data[5] * 256 + data[6]) / 16
        if zAccl > 2047:
            zAccl -= 4096

        mma_data = {
            "x": xAccl,
            "y": yAccl,
            "z": zAccl
        }

        return mma_data

    def close(self):
        self.pi.i2c_close(self.handle)


if __name__ == "__main__":
    pi = pigpio.pi()
    mma = MMA8452(pi)
    mma.setup()
    while 1:
        try:
            print(mma.output())
        except KeyboardInterrupt:
            break
        time.sleep(0.5)
    mma.close()

