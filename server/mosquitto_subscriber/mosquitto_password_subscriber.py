import json
import signal
import argparse
import paho.mqtt.client as mqtt

client = None

def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code.is_failure:
        print(f"Client could not connect to broker in: {user_data['broker']}:{user_data['port']} | Error code: {reason_code}.")
    else:
        print(f"Client connected to broker in: {user_data['broker']}:{user_data['port']}.")
        client.subscribe(user_data['topic'])

def on_connect_fail(client, userdata):
    print(f"Client could not connect to broker in: {user_data['broker']}:{user_data['port']}.")

def on_disconnect(client, userdata, disconnect_flags, reason_code, properties):
    print(f"Client disconnected from broker in: {user_data['broker']}:{user_data['port']}.")

def on_message(client, userdata, message):
    print(message)

def on_subscribe(client, userdata, mid, reason_code_list, properties):
    if reason_code_list[0].is_failure:
        print(f"The broker rejected the subscription to the topic: {user_data['topic']} | Error code: {reason_code_list[0]}")
    else:
        print(f"The broker granted the subscription to the topic: {user_data['topic']} | QoS: {reason_code_list[0].value}")

def on_log(client, userdata, level, buf):
    print(buf)

def disconnect_client(signal_number, frame):
    print(f"Client interrupted with signal: {signal_number}.")
    client.disconnect()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--broker', required=True)
    parser.add_argument('-p', '--port', type=int, required=True)
    parser.add_argument('-t', '--topic', required=True)
    parser.add_argument('-u', '--username', required=True)
    parser.add_argument('-P', '--password', required=True)
    parser.add_argument('-l', '--logger', action="store_true")
    args = parser.parse_args()

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    
    client.on_connect = on_connect
    client.on_connect_fail = on_connect_fail
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    client.on_subscribe = on_subscribe
    
    if (args.logger):
        client.on_log = on_log

    user_data = {
        "broker": args.broker,
        "port": args.port,
        "topic": args.topic
    }
    client.user_data_set(user_data)

    client.username_pw_set(args.username, args.password)
    client.connect(args.broker, args.port)

    signal.signal(signal.SIGINT, disconnect_client)
    signal.signal(signal.SIGTERM, disconnect_client)

    client.loop_forever(retry_first_connection=True)
