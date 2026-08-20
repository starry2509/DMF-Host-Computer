from time import sleep
import serial
import serial.tools.list_ports
import time
from typing import Optional
class SerialDriver(object):
    def __init__(self,log=None):
        super().__init__()
        self.com_num = None
        self.baudrate = 115200
        self.ser = None
        self.rx_buffer = bytearray()
        self.packet_start = bytes([0xa5,0xa5])
        self.packet_end = bytes([0x5a,0x5a])
        self.read_time_out = 0.1
        self.available_port = []
        self.log=log
        self.data=None
        self.voltage_module = 2  # 交流模式
    def _is_usb_serial_port(self, port_info) -> bool:
        """
        仅筛选通过 USB 枚举出来的串口（Windows: hwid 常含 'USB' / 可取到 vid/pid）。
        """
        try:
            hwid = (getattr(port_info, "hwid", "") or "").upper()
            location = (getattr(port_info, "location", "") or "").upper()
            manuf = (getattr(port_info, "manufacturer", "") or "").upper()
            product = (getattr(port_info, "product", "") or "").upper()
            interface = (getattr(port_info, "interface", "") or "").upper()
            vid = getattr(port_info, "vid", None)
            pid = getattr(port_info, "pid", None)
            if vid is not None and pid is not None:
                return True
            if "USB" in hwid or "USB" in location:
                return True
            usb_keywords = ("CH340", "CH341", "FTDI", "CP210", "SILICON LABS", "PROLIFIC")
            hay = " ".join([hwid, manuf, product, interface])
            return any(k in hay for k in usb_keywords)
        except Exception:
            return False
    def find_available_port(self):
        # 每次刷新都重新枚举，避免累计旧数据
        self.available_port = []
        ports = list(serial.tools.list_ports.comports())
        for i in range(len(ports)):
            if not self._is_usb_serial_port(ports[i]):
                continue
            try:
                s = serial.Serial(
                    ports[i].device,
                    self.baudrate,
                    serial.EIGHTBITS,
                    serial.PARITY_NONE,
                    serial.STOPBITS_ONE,
                    self.read_time_out
                )
                s.close()
                desc = getattr(ports[i], "description", "") or ""
                # UI 下拉框里展示：COMx - 描述
                self.available_port.append(f"{ports[i].device} - {desc}")
            except (OSError, serial.SerialException):
                continue
        return self.available_port
    def open(self,port:str):
        self.ser = serial.Serial(
                port,
                self.baudrate,
                serial.EIGHTBITS,
                serial.PARITY_NONE,
                serial.STOPBITS_ONE,
                self.read_time_out
            )
        if self.ser.isOpen():
            self.ser.flushInput()
            self.log.debug(True,"{}串口成功打开".format(self.available_port[0]))
            return True
        else:
            self.ser = None
            self.log.debug(True,"{}串口成功打开".format(self.available_port[0]))
            return False
    def write_packet(self,data=b''):
        time.sleep(0.001)
        try:
            packet = bytearray()
            packet.extend(self.packet_start)
            packet.extend(data)
            packet.extend(self.packet_end)
            if self.available_port:
                self.ser.write(packet)
                self.data = packet
                self.log.info(False, f"Send:{self.data}")
                return True
            else:
                self.log.debug(True,"串口打开失败")
        except serial.SerialException as e:
            self.close()
            self.available_port = []
            return False
    def readbytes(self,num=16):
        if self.ser is None:
            if not self.open(): return ''
        data = self.ser.read(num)
        self.log.info(False,f"Receive:{data}")
        return data
    def writereadbytes(self,data=b''):
        if self.ser is None:
            if not self.open(): return False
        self.write_packet(data)
        inwaiting_time = 0
        while (inwaiting_time < self.read_time_out and self.ser.inWaiting() == 0):#最多等待100ms
            time.sleep(0.01)
            inwaiting_time += 0.01
        if self.ser.inWaiting() >0 :
            data =  self.ser.read(16)
            self.log.info(False,f"Receive:{data}")
            return data
        else:
            return None
    def close(self):
        if self.ser is not None:
            self.ser.close()
            self.log.debug(False,"{}串口成功关闭".format(self.available_port[0]))
            return True
        else:
            return False
    def bottom_cmd1(self):#物理检查
        data = bytes(bytearray([0x00,0x01,0x00]))
        return int.from_bytes(self.writereadbytes(data),byteorder='big')
    def bottom_cmd2(self):#adc采样
        data = bytes(bytearray([0x00,0x02,0x00]))
        return int.from_bytes(self.writereadbytes(data),byteorder='big')
    def bottom_cmd3(self):#adc采样
        data = bytes(bytearray([0x00,0x03,0x00]))
        return int.from_bytes(self.writereadbytes(data),byteorder='big')
    def bottom_cmd4(self,para1:list):#EEPROM读取
        data = bytes(bytearray([0x00, 0x04, 0x02])+bytes(bytearray(para1)))
        return int.from_bytes(self.writereadbytes(data),byteorder='big')
    def bottom_cmd5(self,para1:list):#EEPROM写入
        data = bytes(bytearray([0x00, 0x05, 0x03])+bytes(bytearray(para1)))
        self.write_packet(data)
    def drive_cmd1(self):#读取电压设定值
        data = bytes(bytearray([0x01,0x01,0x00]))
        return int.from_bytes(self.writereadbytes(data),byteorder='big')
    def drive_cmd2(self):  #读取直流/交流模式
        data = bytes(bytearray([0x01,0x02,0x00]))
        return int.from_bytes(self.writereadbytes(data),byteorder='big')
    def drive_cmd3(self):  #读取逻辑设定值
        data = bytes(bytearray([0x01,0x03,0x00]))
        return self.writereadbytes(data)
    def drive_cmd4(self,para1:list):#设定驱动电压值
        data = bytes(bytearray([0x01, 0x04, 0x02])+bytes(bytearray(para1)))
        self.write_packet(data)
    def drive_cmd5(self,para1:int):  #设置交流/直流模式
        data = bytes(bytearray([0x01,0x05,0x01,para1]))
        self.write_packet(data)
    def drive_cmd6(self,para1:list):  #设定控制逻辑
        self.drive_cmd5(self.voltage_module)#关闭
        sleep(0.01)#等待10ms
        data = bytes(bytearray([0x01, 0x06, 0x10]))+bytes(bytearray(para1))
        self.write_packet(data)
        sleep(0.01)#等待10ms
        self.drive_cmd5(self.voltage_module)#打开原始模式
    def temp_cmd1(self,para1:int):#左侧加热开启或暂停
        data = bytes(bytearray([0x02, 0x01, 0x01,para1]))
        return int.from_bytes(self.writereadbytes(data),byteorder='big')
    def temp_cmd2(self,para1:int):#右侧加热开启或暂停
        data = bytes(bytearray([0x02, 0x02, 0x01,para1]))
        return int.from_bytes(self.writereadbytes(data),byteorder='big')
    def temp_cmd3(self,para1:list):#左侧目标温度设定
        data = bytes(bytearray([0x02, 0x03, 0x02]))+bytes(bytearray(para1))
        return int.from_bytes(self.writereadbytes(data),byteorder='big')
    def temp_cmd4(self,para1:list):#右侧目标温度设定
        data = bytes(bytearray([0x02, 0x04, 0x02]))+bytes(bytearray(para1))
        return int.from_bytes(self.writereadbytes(data),byteorder='big')
    def temp_cmd5(self,para1:list):#左侧PID参数设定
        data = bytes(bytearray([0x02, 0x05, 0x06]))+bytes(bytearray(para1))
        ret_data = self.writereadbytes(data)
        return [int.from_bytes(ret_data[0:2],byteorder='big'),
                int.from_bytes(ret_data[2:4],byteorder='big'),
                int.from_bytes(ret_data[4:6],byteorder='big')]
    def temp_cmd6(self,para1:list):#右侧PID参数设定
        data = bytes(bytearray([0x02, 0x06, 0x06]))+bytes(bytearray(para1))
        ret_data = self.writereadbytes(data)
        return [int.from_bytes(ret_data[0:2], byteorder='big'),
                int.from_bytes(ret_data[2:4], byteorder='big'),
                int.from_bytes(ret_data[4:6], byteorder='big')]
    def temp_cmd7(self):#获取当前左侧温度
        data = bytes(bytearray([0x02, 0x07,0x00 ]))
        return int.from_bytes(self.writereadbytes(data),byteorder='big')
    def temp_cmd8(self):#获取当前右侧温度
        data = bytes(bytearray([0x02, 0x08,0x00 ]))
        return int.from_bytes(self.writereadbytes(data),byteorder='big')
    def temp_cmd9(self):#获取左侧PID参数设定
        data = bytes(bytearray([0x02, 0x09, 0x00]))
        ret_data = self.writereadbytes(data)
        return [int.from_bytes(ret_data[0:2], byteorder='big'),
                int.from_bytes(ret_data[2:4], byteorder='big'),
                int.from_bytes(ret_data[4:6], byteorder='big')]
    def temp_cmda(self):#获取右侧PID参数设定
        data = bytes(bytearray([0x02, 0x0a, 0x00]))
        ret_data = self.writereadbytes(data)
        return [int.from_bytes(ret_data[0:2], byteorder='big'),
                int.from_bytes(ret_data[2:4], byteorder='big'),
                int.from_bytes(ret_data[4:6], byteorder='big')]
    def temp_cmdb(self):#获取当前左侧加热功率
        data = bytes(bytearray([0x02, 0x0b,0x00]))
        return int.from_bytes(self.writereadbytes(data),byteorder='big')
    def temp_cmdc(self):#获取当前右侧加热功率
        data = bytes(bytearray([0x02, 0x0c,0x00]))
        return int.from_bytes(self.writereadbytes(data),byteorder='big')
    def detector_cmd1(self, para1: int):  # 单次荧光读取
        data = bytes(bytearray([0x03, 0x01, 0x01, para1]))
        ret = self.writereadbytes(data)
        print(ret)
        if not ret:
            return None
        return int.from_bytes(ret, byteorder='little')

    def detector_cmd2(self):  # 激发 LED 关闭
        data = bytes(bytearray([0x03, 0x02, 0x00]))
        self.write_packet(data)

    def detector_cmd3(self):  # 激发 LED 打开
        data = bytes(bytearray([0x03, 0x03, 0x00]))
        self.write_packet(data)

    def detector_cmd4(self):  # 读取荧光值
        data = bytes(bytearray([0x03, 0x04, 0x00]))
        ret = self.writereadbytes(data)
        if not ret:
            return None
        return int.from_bytes(ret, byteorder='little')
if __name__ == "__main__":
    driver = SerialDriver()








