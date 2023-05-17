import serial
import json
import time
import os
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
from paho.mqtt import client as mqtt_client

load_dotenv()


arduino = serial.Serial(port='/dev/cu.usbserial-14220', baudrate=19200, timeout=.1)
starttime = time.time()
scheduler = BackgroundScheduler()

broker = os.getenv('BROKER')
port = int(os.getenv('PORT'))
topic = 'smarthome/power'
client_id = 'kwh01'
username = os.getenv('USERNAME')
password = os.getenv('PASSWORD')


def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
            if scheduler.running:
                scheduler.resume()
            else:
                scheduler.add_job(write_read, args=['1'],trigger='interval', seconds=10)
                scheduler.start()
            print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))
            
        else:
            print("Failed to connect, return code %d\n", rc)
    
    def on_disconnect(client, userdata, rc):
        print("Unexpected disconnection.")
        scheduler.pause()

    client = mqtt_client.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.connect(broker, port)
    return client

def write_read(x):
    data = ""
    try:
        arduino.write(bytes(x, 'utf-8'))
        time.sleep(0.05)
        data = arduino.readline()
    except serial.SerialException as e:
        print("Koneksi serial arduino error :", str(e))
    y = json.loads(data)
    print(broker + str(y["voltage"]))

if __name__ == '__main__':
    client = connect_mqtt()
    client.loop_start()
    #scheduler = BackgroundScheduler()
    #scheduler.add_job(write_read, args=['1'],trigger='interval', seconds=10)
    #scheduler.start()
    #print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))

    """try:
        # This is here to simulate application activity (which keeps the main thread alive).
        while True:
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        # Not strictly necessary if daemonic mode is enabled but should be done if possible
        scheduler.shutdown()
    """
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        scheduler.shutdown()
        pass
    finally:
        client.loop_stop()