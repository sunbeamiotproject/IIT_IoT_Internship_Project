import paho.mqtt.client as mqtt
import mysql.connector
import json
import requests

# Database connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="iot_project"
)
cursor = db.cursor()

API_KEY = "MCO5UXNWY4CRVAGX"

# When connected to broker
def on_connect(client, userdata, flags, reason_code, properties):
    print("Connected to MQTT Broker")
    client.subscribe("env/data")
    print("Subscribed to topic: env/data")

# When message received
def on_message(client, userdata, msg):
    data = json.loads(msg.payload.decode())

    temperature = data["temperature"]
    humidity = data["humidity"]
    gas = data["gas"]

    #  PRINT OUTPUT IN SEQUENCE
    print("Data Received:")
    print(f"Temperature : {temperature} °C")
    print(f"Humidity    : {humidity} %")
    print(f"Gas Level   : {gas}")
    print("-" * 30)

    # Store in database
    cursor.execute(
        "INSERT INTO sensor_data (temperature, humidity, gas) VALUES (%s, %s, %s)",
        (temperature, humidity, gas)
    )
    db.commit()

    # Upload to ThingSpeak
    requests.get(
        "https://api.thingspeak.com/update",
        params={
            "api_key": API_KEY,
            "field1": temperature,
            "field2": humidity,
            "field3": gas
        }
    )

# MQTT client (new API)
client = mqtt.Client(
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2
)

client.on_connect = on_connect
client.on_message = on_message

client.connect("test.mosquitto.org", 1883, 60)
client.loop_forever()