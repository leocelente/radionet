
WAIT = 0
COMMAND = 1
BODY = 2
ESCAPE = 3

FESC = b'\xDB'
TFESC = b'\xDD'
FEND = b'\xC0'
TFEND = b'\xDC'

CMD_DATA = 0
CMD_CONF = 1


class KISS():
    state: int = WAIT
    cmd_type = 255
    rx_buffer = []
    def __init__(self, callback) -> None:
        self.callback = callback

    def ingest(self, input: int) -> int:
        if (self.state == WAIT and input == FEND): 
            self.state = COMMAND
            return 0
        elif (self.state == COMMAND): 
            self.cmd_type = input
            self.state = BODY
            return 0
        elif (self.state == BODY and input == FEND): 
            data = b''.join(self.rx_buffer)
            self.callback(self.cmd_type, bytes(data))
            self.rx_buffer.clear()
            self.state = WAIT
            return 0
        elif (self.state == BODY and input == FESC): 
            self.state = ESCAPE
            return 0
        elif (self.state == ESCAPE and input == TFESC): 
            self.rx_buffer.append(FESC)
            self.state = ESCAPE
            return 0
        elif (self.state == ESCAPE and input == TFEND): 
            self.rx_buffer.append(FEND)
            self.state = ESCAPE
            return 0
        elif (self.state == BODY): 
            self.rx_buffer.append(input)
            return 0
        else:
            self.state = WAIT
            return 1

    @staticmethod
    def transform(cmd: int, raw: bytes) -> bytes:
        B = lambda b: int.from_bytes(b, byteorder='big')
        transformed: list[int] = [B(FEND), cmd]        
        for b in raw:
            b = int(b)
            if b == B(FEND):
                transformed.append(B(FESC))
                transformed.append(B(TFEND))
                continue
            elif b == B(FESC):
                transformed.append(B(FESC))
                transformed.append(B(TFESC))
                continue
            transformed.append(b)
        transformed.append(B(FEND))
        return bytes(transformed)