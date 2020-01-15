import pigpio
import time

BUS_NUMBER = 1
I2C_ADDRESS = 0x76


class BME280():
    """
    温湿度・気圧センサ BME280

    Parameters
    -----------
    pi : pigpio.pi()
        pigpioのインスタンス
    busnum : int
        Bus Number デフォルト: 1
    i2cadr : int
        BME280のアドレス(16進) デフォルト: 0x76
    """

    def __init__(self, pi, busnum=BUS_NUMBER, i2cadr=I2C_ADDRESS):
        self.pi = pi

        self.i2c_address = i2cadr

        self.digT = []
        self.digP = []
        self.digH = []

        self.t_fine = 0.0

        self.handle = self.pi.i2c_open(busnum, i2cadr)
    
    def setup(self):
        self.__startup()
        self.__get_calib_param()

    def __startup(self):
        over_samp_temp = 1  # Temperature oversampling x 1
        over_samp_pres = 1  # Pressure oversampling x 1
        over_samp_humi = 1  # Humidity oversampling x 1
        mode = 3            # Normal Mode
        tstandby = 5        # Tstandby: 1000ms
        filter_ = 0         # filter:  off
        spi_3w = 0          # 3-wire SPI: Disable

        ctrl_meas_reg = (over_samp_temp << 5) | (over_samp_pres << 2) | mode
        config_reg = (tstandby << 5) | (filter_ << 2) | spi_3w
        ctrl_hum_reg = over_samp_humi

        self.__write_reg(0xF2, ctrl_hum_reg)
        self.__write_reg(0xF4, ctrl_meas_reg)
        self.__write_reg(0xF5, config_reg)

    def __write_reg(self, reg_address, data):
        self.pi.i2c_write_byte_data(self.handle, reg_address, data)

    def __get_calib_param(self):
        calib = []

        for i in range(0x88, 0x88+24):
            calib.append(self.pi.i2c_read_byte_data(self.handle, i))
        calib.append(self.pi.i2c_read_byte_data(self.handle, 0xA1))
        for i in range(0xE1, 0xE1+7):
            calib.append(self.pi.i2c_read_byte_data(self.handle, i))

        self.digT.append((calib[1] << 8) | calib[0])
        self.digT.append((calib[3] << 8) | calib[2])
        self.digT.append((calib[5] << 8) | calib[4])
        self.digP.append((calib[7] << 8) | calib[6])
        self.digP.append((calib[9] << 8) | calib[8])
        self.digP.append((calib[11] << 8) | calib[10])
        self.digP.append((calib[13] << 8) | calib[12])
        self.digP.append((calib[15] << 8) | calib[14])
        self.digP.append((calib[17] << 8) | calib[16])
        self.digP.append((calib[19] << 8) | calib[18])
        self.digP.append((calib[21] << 8) | calib[20])
        self.digP.append((calib[23] << 8) | calib[22])
        self.digH.append(calib[24])
        self.digH.append((calib[26] << 8) | calib[25])
        self.digH.append(calib[27])
        self.digH.append((calib[28] << 4) | (0x0F & calib[29]))
        self.digH.append((calib[30] << 4) | ((calib[29] >> 4) & 0x0F))
        self.digH.append(calib[31])
        
        for i in range(1, 2):
            if self.digT[i] & 0x8000:
                self.digT[i] = (-self.digT[i] ^ 0xFFFF) + 1
        
        for i in range(1, 8):
            if self.digP[i] & 0x8000:
                self.digP[i] = (-self.digP[i] ^ 0xFFFF) + 1
        
        for i in range(0, 6):
            if self.digH[i] & 0x8000:
                self.digH[i] = (-self.digH[i] ^ 0xFFFF) + 1

    def output(self):
        data = []
        for i in range(0xF7, 0xF7 + 8):
            data.append(self.pi.i2c_read_byte_data(self.handle, i))

        pres_raw = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)
        temp_raw = (data[3] << 12) | (data[4] << 4) | (data[5] >> 4)
        humi_raw = (data[6] << 8) | data[7]

        temp = self.__compensate_temp(temp_raw)
        pres = self.__compensate_pres(pres_raw)
        humi = self.__compensate_humi(humi_raw)

        bme_data = {
            "temp": temp,
            "humid": humi,
            "press" : pres
        }

        return bme_data

    def __compensate_pres(self, adc_P):
        
        pressure = 0.0
        
        v1 = (self.t_fine / 2.0) - 64000.0
        v2 = (((v1 / 4.0) * (v1 / 4.0)) / 2048) * self.digP[5]
        v2 = v2 + ((v1 * self.digP[4]) * 2.0)
        v2 = (v2 / 4.0) + (self.digP[3] * 65536.0)
        v1 = (((self.digP[2] * (((v1 / 4.0) * (v1 / 4.0)) / 8192)) / 8) + ((self.digP[1] * v1) / 2.0)) / 262144
        v1 = ((32768 + v1) * self.digP[0]) / 32768

        if v1 == 0:
            return 0
        
        pressure = ((1048576 - adc_P) - (v2 / 4096)) * 3125
        if pressure < 0x80000000:
            pressure = (pressure * 2.0) / v1
        else:
            pressure = (pressure / v1) * 2

        v1 = (self.digP[8] * (((pressure / 8.0) * (pressure / 8.0)) / 8192.0)) / 4096
        v2 = ((pressure / 4.0) * self.digP[7]) / 8192.0
        pressure = pressure + ((v1 + v2 + self.digP[6]) / 16.0)

        return pressure / 100   # hPa

    def __compensate_temp(self, adc_T):
        v1 = (adc_T / 16384.0 - self.digT[0] / 1024.0) * self.digT[1]
        v2 = (adc_T / 131072.0 - self.digT[0] / 8192.0) * (adc_T / 131072.0 - self.digT[0] / 8192.0) * self.digT[2]
        self.t_fine = v1 + v2
        temperature = self.t_fine / 5120.0

        return temperature

    def __compensate_humi(self, adc_H):
        var_h = self.t_fine - 76800.0
        if var_h != 0:
        	var_h = (adc_H - (self.digH[3] * 64.0 + self.digH[4]/16384.0 * var_h)) * (self.digH[1] / 65536.0 * (1.0 + self.digH[5] / 67108864.0 * var_h * (1.0 + self.digH[2] / 67108864.0 * var_h)))
        else:
        	return 0
        var_h = var_h * (1.0 - self.digH[0] * var_h / 524288.0)
        if var_h > 100.0:
        	var_h = 100.0
        elif var_h < 0.0:
        	var_h = 0.0

        return var_h


    def close(self):
        self.pi.i2c_close(self.handle)


if __name__ == "__main__":
    pi = pigpio.pi()
    bme = BME280(pi)
    bme.setup()
    print(bme.output())
    bme.close()
