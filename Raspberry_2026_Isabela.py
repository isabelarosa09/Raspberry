from gpiozero import Motor                     #Todas as bibliotecas usadas.
from gpiozero import LED
from gpio_config import factory
import paho.mqtt.client as mqtt
import json
import smbus2
import bme280
import time
from luma.core.interface.serial import i2c
from luma.oled.device import sh1106
from luma.core.render import canvas
from PIL import ImageFont
import board



port = 1
address = 0x76
bus = smbus2.SMBus(port)
calibration_params = bme280.load_calibration_params(bus, address)

# ==== CONFIGURAÇÕES DO DISPLAY OLED SH1106 ====
serial = i2c(port=1, address=0x3C)   # Endereço padrão do SH1106 é 0x3C
device = sh1106(serial)

motor = Motor(forward=12, backward=16, pin_factory=factory)
PINO_LED = LED(17, pin_factory=factory)
 

MQTT_BROKER = "broker.hivemq.com" # Usado o servidor MQTT
MQTT_PORT = 1883 
MQTT_TOPIC = "emc/projeto" # Diretório onde ta sendo executado o código

client = mqtt.Client()
client.connect(MQTT_BROKER, MQTT_PORT, 60)

# === Função para mostrar no display ===
def mostrar_display(estado):
    with canvas(device) as draw:
        draw.text((0, 10), f"Temp: {temp} °C", fill=255)
        draw.text((0, 30), f"{estado}", fill=255)
        
while True:
    data = bme280.sample(bus, address, calibration_params)
    temp = round(data.temperature, 1)

    print(f"Temperatura: {temp:.1f} °C")
    payload = json.dumps({"temperatura": temp})
    
    if temp > 25:
        PINO_LED.on()            #Modificação
        motor.forward()		    # liga motor
        estado = "Motor LIGADO"
        mostrar_display(estado)
        print("Motor LIGADO (ventilação)")
        client.publish(MQTT_TOPIC, "Motor LIGADO para ventilação")

    elif temp < 23:
        PINO_LED.off()
        motor.stop()            # desliga motor
        print("Motor DESLIGADO")
        estado = "Motor DESLIGADO"
        mostrar_display(estado)
        client.publish(MQTT_TOPIC, "Motor DESLIGADO")
    
    time.sleep(5)
    
    

     



