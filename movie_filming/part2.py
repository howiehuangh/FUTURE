import roslibpy
import time

WHEELTEC_HOST = '192.168.199.147'
WHEELTEC_PORT = 9090
TOPIC = '/smoother_cmd_vel'
MESSAGE_TYPE = 'geometry_msgs/Twist'


def action(msg):
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

    move_forward_msg = roslibpy.Message({
        'linear': {
            'x': 0.2,
            'y': 0.0,
            'z': 0.0
        },
        'angular': {
            'x': 0.0,
            'y': 0.0,
            'z': 0.0,
        },
    })

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
    rotate_right_msg = roslibpy.Message({
        'linear': {
            'x': 0.0,
            'y': 0.0,
            'z': 0.0
        },
        'angular': {
            'x': 0.0,
            'y': 0.0,
            'z': -0.4,
        },
    })

    action(move_forward_msg)
    time.sleep(3)
    action(stop_msg)
    time.sleep(2)
    action(rotate_right_msg)
    time.sleep(7.5)
    action(stop_msg)

