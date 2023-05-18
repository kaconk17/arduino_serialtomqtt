import serial
import time
import os
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
from paho.mqtt import client as mqtt_client

load_dotenv()

broker = os.getenv('BROKER')
port = int(os.getenv('PORT'))
topic = 'smarthome/power'
client_id = 'kwh01'
username = os.getenv('USERNAME')
password = os.getenv('PASSWORD')
device = os.getenv('DEVICE')
baudrate = os.getenv('BAUDRATE')

starttime = time.time()
scheduler = BackgroundScheduler()
arduino = serial.Serial(port=device, baudrate=baudrate, timeout=.1)

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
            if scheduler.running:
                scheduler.resume()
            else:
                scheduler.add_job(write_read, args=[client],trigger='interval', seconds=10)
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

def write_read(_clnt):
   
    try:
        arduino.write(bytes('1', 'utf-8'))
        time.sleep(0.05)
        data = arduino.readline()
        #y = json.loads(data)
        _clnt.publish(topic+'/'+client_id,data)
        #print(broker + str(y["voltage"]))
    except serial.SerialException as e:
        print("Koneksi serial arduino error :", str(e))

if __name__ == '__main__':
    client = connect_mqtt()
    client.loop_start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        scheduler.shutdown()
        pass
    finally:
        client.loop_stop()