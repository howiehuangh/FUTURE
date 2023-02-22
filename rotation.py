import roslibpy
import sys
import time

WHEELTEC_HOST = '192.168.199.147'
WHEELTEC_PORT = 9090
TOPIC = '/smoother_cmd_vel'
MESSAGE_TYPE = 'geometry_msgs/Twist'
#DIRECTION = 'left'
DIRECTION = sys.argv[1]
WHEELTEC_HOST = sys.argv[2]



def rotation(msg):
    client = roslibpy.Ros(WHEELTEC_HOST, WHEELTEC_PORT)
    client.run()
    print('Is ROS connected?', client.is_connected)

    talker_node = roslibpy.Topic(ros=client, name=TOPIC, message_type=MESSAGE_TYPE)
    if client.is_connected:
        talker_node.publish(msg)
        print("Sending message...")
        time.sleep(1)
    talker_node.unadvertise()


if __name__ == "__main__":
    if DIRECTION == 'left':
        start_msg = roslibpy.Message({
            'linear': {
                'x': 0.0,
                'y': 0.0,
                'z': 0.0
            },
            'angular': {
                'x': 0.0,
                'y': 0.0,
                'z': 1.0,
            },
        })
    elif DIRECTION == 'right':
        start_msg = roslibpy.Message({
            'linear': {
                'x': 0.0,
                'y': 0.0,
                'z': 0.0
            },
            'angular': {
                'x': 0.0,
                'y': 0.0,
                'z': -1.0,
            },
        })
    else:
        print("Missing argument: 'left'/'right'")
        sys.exit()

    stop_msg = roslibpy.Message({
        'linear': {
            'x': 0.0,
            'y': 0.0,
            'z': 0.0
        },
        'angular': {
            'x': 0.0,
            'y': 0.0,
            'z': 0.0,
        },
    })

    rotation(start_msg)
    time.sleep(5.5)
    rotation(stop_msg)



