# instalar pymavlink, paho-mqtt (version 1.6.1), opencv-python, python-socketio, requests
# websocket-client

import json
import threading
import tkinter as tk
from Dron import Dron
import random
import paho.mqtt.client as mqtt
import time
import socketio # instalar python-socketio
import cv2
import base64

def allowExternal ():
    global client
    global allowExternalBtn

    clientName = "demoDash" + str(random.randint(1000, 9000))
    client = mqtt.Client(clientName, transport="websockets")

    broker_address = "dronseetac.upc.edu"
    broker_port = 8000

    client.username_pw_set(
        'dronsEETAC', 'mimara1456.'
    )

    client.on_message = on_message
    client.on_connect = on_connect
    client.connect(broker_address, broker_port)
    print('Conectado a broker.hivemq.com:8000')

    # me subscribo a cualquier mensaje  que venga del mobileFlask
    client.subscribe('mobileFlask/ground/#')
    print('demoDash esperando peticiones ')
    client.loop_start()
    allowExternalBtn['text'] = "Peticiones externas permitidas"
    allowExternalBtn['fg'] = 'white'
    allowExternalBtn['bg'] = 'green'


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("connected OK Returned code=", rc)
    else:
        print("Bad connection Returned code=", rc)


def procesarTelemetria(telemetryInfo):
    # cada vez que recibo un paquete de telemetría del dron lo envio al broker
    client.publish('ground/mobileFlask/telemetryInfo', json.dumps(telemetryInfo))


def publish_event ( event):
    # publico en el broker el evento, que en este caso será 'flying' porque es el único que se
    # considera en esta aplicación
    print ('en el aire')
    client.publish('ground/mobileFlask/'+event)

# aqui recibimos los mensajes de la web app
def on_message(client, userdata, message):
        global dron
        # el formato del topic siempre será:
        # mobileFlask/demoDash/comando

        parts = message.topic.split ('/')
        command = parts[2]
        print ('recibo ', command)
        if command == 'connect':
            # me conecto al simulador
            connection_string = 'tcp:127.0.0.1:5763'
            baud = 115200
            dron.connect(connection_string, baud)
            print ('conectado')
            # le pido los datos de telemetria y le indico la función a ejecutar cada vez que tenga un nuevo
            # paquete de datos
            print ('pido datos de telemetria')
            dron.send_telemetry_info(procesarTelemetria)

        # aqui atiendo las peticiones externas (que vienen del movil)
        if command == 'arm_takeOff':
            if dron.state == 'connected':
                # recupero la altura a alcanzar, que viene como payload del mensaje
                alt = int( message.payload.decode("utf-8"))
                dron.arm()
                print ('armado')
                # operación no bloqueante. Cuando acabe publicará el evento correspondiente
                dron.takeOff(alt, blocking=False, callback=publish_event, params='flying')

        if command == 'go':
            if dron.state == 'flying':
                direction = message.payload.decode("utf-8")
                print ('vamos al: ', direction)
                dron.go(direction)

        if command == 'Land':
            if dron.state == 'flying':
                print ('voy a aterrizar')
                # operación no bloqueante
                dron.Land(blocking=False)

def videoMQTT ():
    global sendingMQTT
    global videoMQTTBtn

    if sendingMQTT:
        sendingMQTT = False
        videoMQTTBtn['text'] = "Enviar vídeo por MQTT"
        videoMQTTBtn['fg'] = 'black'
        videoMQTTBtn['bg'] = 'dark orange'
    else:
        t = threading.Thread (target = video_MQTT_thread).start()
        videoMQTTBtn['text'] = "Detener vídeo por MQTT"
        videoMQTTBtn['fg'] = 'white'
        videoMQTTBtn['bg'] = 'green'

def video_MQTT_thread ():
    global cap, sendingMQTT
    global frequencySlider, qualitySlider

    sendingMQTT = True

    while sendingMQTT:
        if frequencySlider.get() > 0:
            ret, frame = cap.read()
            if not ret:
                break
            # genero el frame con el nivel de calidad seleccionado (entre 0 y 100)
            quality = qualitySlider.get()
            _, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
            frame_b64 = base64.b64encode(buffer).decode('utf-8')

            # Enviar el frame por MQTT
            client.publish('ground/mobileFlask/frame', frame_b64)
            # espero el tiempo establecido según la frecuencia seleccionada
            periodo = 1 / frequencySlider.get()
            time.sleep(periodo)


def videoWebsockets ():
    global sendingWebsockets
    global videoWebsocketBtn

    if sendingWebsockets:
        sendingWebsockets = False
        videoWebsocketBtn['text'] = "Enviar vídeo por websockets"
        videoWebsocketBtn['fg'] = 'black'
        videoWebsocketBtn['bg'] = 'dark orange'

    else:
        t = threading.Thread (target = video_Websocket_thread).start()
        videoWebsocketBtn['text'] = "Detener vídeo por websockets"
        videoWebsocketBtn['fg'] = 'white'
        videoWebsocketBtn['bg'] = 'green'

def video_Websocket_thread ():
    global cap, sendingWebsockets, sio
    global frequencySlider, qualitySlider


    sendingWebsockets= True
    while sendingWebsockets:
        if frequencySlider.get() > 0:
            ret, frame = cap.read()
            if not ret:
                break
            # genero el frame con el nivel de calidad seleccionado (entre 0 y 100)
            quality = qualitySlider.get()
            _, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
            frame_b64 = base64.b64encode(buffer).decode('utf-8')
            # envio el frame por el webbsocket
            sio.emit('video_frame', frame_b64)
            # espero el tiempo establecido según la frecuencia seleccionada
            periodo = 1/frequencySlider.get()
            time.sleep(periodo)



# Capturar video desde la cámara
cap = cv2.VideoCapture(0)
sendingMQTT = False
sendingWebsockets = False
sio = socketio.Client()

# esto es para conectarme al websocket del servidor en desarrollo
sio.connect('http://localhost:8766')

# esto es para conectarme al websocket del servidor en producción
#sio.connect('http://dronseetac.upc.edu:8106')

print("Conectado al websocket")
dron = Dron()

ventana = tk.Tk()
ventana.geometry ('250x600')
ventana.title("Pequeña estación de tierra")

# La interfaz tiene 12 filas y una columna

ventana.rowconfigure(0, weight=1)
ventana.rowconfigure(1, weight=1)
ventana.rowconfigure(2, weight=1)
ventana.rowconfigure(3, weight=1)
ventana.rowconfigure(4, weight=1)
ventana.rowconfigure(5, weight=1)
ventana.rowconfigure(6, weight=1)
ventana.rowconfigure(7, weight=1)
ventana.rowconfigure(8, weight=1)
ventana.rowconfigure(9, weight=1)
ventana.rowconfigure(10, weight=1)
ventana.rowconfigure(11, weight=1)
ventana.rowconfigure(12, weight=1)

ventana.columnconfigure(0, weight=1)


connectBtn = tk.Button(ventana, text="Conectar", bg="dark orange", command = lambda: dron.connect('tcp:127.0.0.1:5763', 115200))
connectBtn.grid(row=0, column=0, padx=3, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

armBtn = tk.Button(ventana, text="Armar", bg="dark orange", command=lambda: dron.arm())
armBtn.grid(row=1, column=0, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

takeOffBtn = tk.Button(ventana, text="Despegar", bg="dark orange", command=lambda: dron.takeOff(3))
takeOffBtn.grid(row=2, column=0,  padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

NorthBtn = tk.Button(ventana, text="Norte", bg="dark orange", command=lambda: dron.go('North'))
NorthBtn.grid(row=3, column=0, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

SouthBtn = tk.Button(ventana, text="Sur", bg="dark orange", command=lambda: dron.go('South'))
SouthBtn.grid(row=4, column=0, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

EastBtn = tk.Button(ventana, text="Este", bg="dark orange", command=lambda: dron.go('East'))
EastBtn.grid(row=5, column=0, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

WestBtn = tk.Button(ventana, text="Oeste", bg="dark orange", command=lambda: dron.go('West'))
WestBtn.grid(row=6, column=0, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

StopBtn = tk.Button(ventana, text="Para", bg="dark orange", command=lambda: dron.go('Stop'))
StopBtn.grid(row=7, column=0, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

RTLBtn = tk.Button(ventana, text="RTL", bg="dark orange", command=lambda: dron.RTL())
RTLBtn.grid(row=8, column=0, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

disconnectBtn = tk.Button(ventana, text="Desconectar", bg="dark orange", command=lambda: dron.disconnect())
disconnectBtn.grid(row=9, column=0, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

allowExternalBtn = tk.Button(ventana, text="Permitir peticiones externas", bg="dark orange", command= allowExternal)
allowExternalBtn.grid(row=10, column=0, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)


videoMQTTBtn = tk.Button(ventana, text="Enviar video por MQTT", bg="dark orange", command=videoMQTT)
videoMQTTBtn.grid(row=11, column=0, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

videoWebsocketBtn = tk.Button(ventana, text="Enviar video por websockets", bg="dark orange", command=videoWebsockets)
videoWebsocketBtn.grid(row=12, column=0, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

videoStreamControlFrame = tk.LabelFrame(ventana, text="Video stream control", padx=5, pady=5)
videoStreamControlFrame.grid(row=13, column=0, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)
videoStreamControlFrame.columnconfigure(0, weight=1)
videoStreamControlFrame.columnconfigure(1, weight=1)
videoStreamControlFrame.rowconfigure(0, weight=1)
videoStreamControlFrame.rowconfigure(1, weight=1)

tk.Label(videoStreamControlFrame, text="Quality").grid(row=0, column=0, pady=4, padx=0)
qualitySlider = tk.Scale(
    videoStreamControlFrame,
    from_=0,
    to=100,
    length=100,
    orient="horizontal",
    activebackground="green",
    tickinterval=20,
    resolution=10
)
qualitySlider.grid(row=0, column=1, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)
qualitySlider.set(50)



tk.Label(videoStreamControlFrame, text="Frames/s").grid(row=1, column=0, pady=4, padx=0)
frequencySlider = tk.Scale(
    videoStreamControlFrame,
    from_=0,
    to=30,
    length=100,
    orient="horizontal",
    activebackground="green",
    tickinterval=5,
    resolution=1
)
frequencySlider.set(5)
frequencySlider.grid(row=1, column=1, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)


ventana.mainloop()