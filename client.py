import serial
import time
import os
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
from paho.mqtt import client as mqtt_client
from telegram import __version__ as TG_VER
try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters


load_dotenv()

broker = os.getenv('BROKER')
port = int(os.getenv('PORT'))
topic = 'smarthome/power3'
client_id = 'kwh03'
username = os.getenv('USERNAME')
password = os.getenv('PASSWORD')
device = os.getenv('DEVICE')
baudrate = os.getenv('BAUDRATE')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

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
        #arduino.write(bytes('1', 'utf-8'))
        time.sleep(0.05)
        #data = arduino.readline()
        #y = json.loads(data)
        #_clnt.publish(topic+'/'+client_id,data)
        #print(broker + str(y["voltage"]))
        print("executed")
    except serial.SerialException as e:
        print("Koneksi serial arduino error :", str(e))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}! Welcome to Kaconk Smart Home ",
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    print("pesan help")
    await update.message.reply_text("Help!")

def lighton(bot, update):
  chat_id = update.message.chat_id
  bot.send_message(chat_id, text="Light has been turned ON")

def lightoff(bot, update):
  chat_id = update.message.chat_id
  bot.send_message(chat_id, text="Light has been turned OFF")

def given_message(bot, update):
  text = update.message.text.upper()
  text = update.message.text
  if text == 'Turn on the Light':
    lighton(bot,update)
  
  elif text == 'Turn off the Light':
    lightoff(bot,update)

if __name__ == '__main__':
    client = connect_mqtt()
    client.loop_start()
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help",help_command))

    application.run_polling()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        scheduler.shutdown()
        pass
    finally:
        client.loop_stop()