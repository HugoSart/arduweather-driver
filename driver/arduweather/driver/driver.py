import sys
import requests
import serial
import time

API_KEY = "5d509d5fe05688d975f9645c029c01e4"
lat = -23.4273
lon = -51.9375


def int_to_bytes(value, length):
    result = []

    s = str()
    for i in range(0, length):
        result.append(value >> (i * 8) & 0xff)
        s += str((i * 8) & 0xff)
    result.reverse()

    return result


def send(ser):
    url = "http://api.openweathermap.org/data/2.5/weather?lat=" + str(lat) + "&lon=" + str(lon) + "&appid=" + str(
        API_KEY)
    print(url)
    r = requests.get(url)
    code = r.status_code

    if code == 200:
        j = r.json()
        weather = j['weather'][0]['main']
        temp = j['main']['temp']
        hum = j['main']['humidity']
        dt = j['dt']

        bt = bytearray(int_to_bytes(int(temp - 273.15), 1))
        bh = bytearray(int_to_bytes(int(hum), 1))
        bdt = bytearray(int_to_bytes(int(dt), 8))
        bw = bytearray()
        bw.extend(map(ord, weather + "\n"))

        data = bytearray()
        data.extend(bt)
        data.extend(bh)
        data.extend(bdt)
        data.extend(bw)

        s = str()
        for b in data:
            s += str(b)
            s += ', '
        print('Send: ' + s)

        ser.write(data)
    else:
        print("Request error: " + code)


def wait_request(ser):
    ser.read(1)
    print('Weather requested by ' + ser.name)


def receive_data(ser):
    line = ser.read(64)
    s = str()
    for b in line:
        s += str(b)
        s += ', '
    print('Confirm: ' + s)


def main():
    ser = serial.Serial(
        port=str(sys.argv[1]),
        baudrate=9600
    )

    while True:
        wait_request(ser)
        send(ser)
        receive_data(ser)

    ser.close()


if __name__ == "__main__":
    main()
