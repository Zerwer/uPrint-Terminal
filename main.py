import serial
from binascii import unhexlify


def read(material):
    # Baud rate is 38400
    s = serial.Serial("/dev/tty.usbserial", baudrate=38400)

    # Send command
    s.write(b'er '+bytes(str(material), 'utf-8')+b' 0 0 128\r\n')

    lines = []

    data = b''
    while b'000112' not in data:
        data = b''
        while b'\r\n' not in data:
            data += s.read()
        lines.append(data.decode('utf-8')[:-2])

    if material == 0:
        file = open('material.bin', 'wb')
    else:
        file = open('support.bin', 'wb')
    for line in lines[5:]:
        file.write(unhexlify(line[8:-19].replace(' ', '')))
        print(line[8:-19])

    s.close()


def read_command(s):
    x = b''
    while b'\r\n' not in x:
        x += s.read()
    return x


# bytes  should be byte = '\"00,00,00,00...\"'
def write_bytes(data_bytes, material):
    s = serial.Serial("/dev/tty.usbserial", baudrate=38400)
    s.write(b'ew ' + bytes(str(material), 'utf-8') + b' 0 0 '+bytes(data_bytes, 'utf-8')+b'\r\n')
    read_command(s)
    read_command(s)
    s.close()


def restore_save(material):
    if material == 0:
        file = open('material-save.bin', 'rb')
    else:
        file = open('support-save.bin', 'rb')

    info = file.readlines()[0].hex()
    write_bytes('\"' + (','.join([info[i:i + 2] for i in range(0, len(info), 2)])) + '\"', material)


def load():
    s = serial.Serial("/dev/tty.usbserial", baudrate=38400)
    read_command(s)
    read_command(s)


while True:
    command = input('>>> ')
    if command == 'readm':
        read(0)
    elif command == 'reads':
        read(1)
    elif command == 'restorem':
        restore_save(0)
    elif command == 'restores':
        restore_save(1)
    elif command == 'help':
        print('readm - read material EEPROM\n'
              'reads - read support EEPROM\n'
              'restorem - write material-save.bin to material EEPROM\n'
              'restores - write support-save.bin to support EEPROM\n'
              'help - disply this menu\n'
              'load - run after boot once\n'
              'exit - exit program')
    elif command == 'load':
        load()
    elif command == 'exit':
        exit(0)
    else:
        print('Not valid command!')