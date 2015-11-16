import serial
import struct


class CommUART:
    msg_type = {
        "write": 0x01,
        "read":  0x02
    }
    def __init__(self, port, baudrate=115200, debug=False):
        self.port = port
        self.baudrate = str(baudrate)
        self.csr_data_width = None
        self.debug = debug
        self.port = serial.serial_for_url(port, baudrate)

    def open(self, csr_data_width):
        self.csr_data_width = csr_data_width
        if hasattr(self, "port"):
            return
        self.port.open()

    def close(self):
        if not hasattr(self, "port"):
            return
        del self.port

    def _read(self, length):
        r = bytes()
        while len(r) < length:
            r += self.port.read(length - len(r))
        return r

    def _write(self, data):
        remaining = len(data)
        pos = 0
        while remaining:
            written = self.port.write(data[pos:])
            remaining -= written
            pos += written

    def read(self, addr, length=None):
        r = []
        length_int = 1 if length is None else length
        self._write([self.msg_type["read"], length_int])
        self._write(list((addr//4).to_bytes(4, byteorder="big")))
        for i in range(length_int):
            data = int.from_bytes(self._read(4), "big")
            if self.debug:
                print("read {:08x} @ {:08x}".format(data, addr + 4*i))
            if length is None:
                return data
            r.append(data)
        return r

    def write(self, addr, data):
        data = data if isinstance(data, list) else [data]
        length = len(data)
        self._write([self.msg_type["write"], length])
        self._write(list((addr//4).to_bytes(4, byteorder="big")))
        for i in range(len(data)):
            self._write(list(data[i].to_bytes(4, byteorder="big")))
            if self.debug:
                print("write {:08x} @ {:08x}".format(data[i], addr + 4*i))
