import requests
import json

AGV_HOST = '192.168.0.124'
AGV_PORT = '3546'

URL = f"http://{AGV_HOST}:{AGV_PORT}/api/v1/system/speed"


def rotate_360():
    body = {'speed_x': 0, 'speed_y': 0, 'speed_angle': 2.2}
    print(URL)
    r = requests.put(URL, data=json.dumps(body))
    print(r.json())


def rotate_left():
    print('checking rotate left')
    body = {'speed_x': 0, 'speed_y': 0, 'speed_angle': 1.95}
    print(URL)
    r = requests.put(URL, data=json.dumps(body))
    print(r.json())


def rotate_right():
    body = {'speed_x': 0, 'speed_y': 0, 'speed_angle': -1.95}
    print(URL)
    r = requests.put(URL, data=json.dumps(body))
    print(r.json())


def move_front():
    body = {'speed_x': 0.07, 'speed_y': 0, 'speed_angle': 0}
    print(URL)
    r = requests.put(URL, data=json.dumps(body))
    print(r.json())

def move_backward():
    body = {'speed_x': -0.07, 'speed_y': 0, 'speed_angle': 0}
    print(URL)
    r = requests.put(URL, data=json.dumps(body))
    print(r.json())

def turn_left():
    body = {'speed_x': 0, 'speed_y': 0, 'speed_angle': 0.2}
    print(URL)
    r = requests.put(URL, data=json.dumps(body))
    print(r.json())
    return r.json()

def turn_right():
    body = {'speed_x': 0, 'speed_y': 0, 'speed_angle': -0.2}
    print(URL)
    r = requests.put(URL, data=json.dumps(body))
    print(r.json())

def movement_stop():
    body = {'speed_x': 0, 'speed_y': 0, 'speed_angle': 0}
    print(URL)
    r = requests.put(URL, data=json.dumps(body))
    print(r.json())


def main():
    rotate_360()


if __name__ == "__main__":
    main()
