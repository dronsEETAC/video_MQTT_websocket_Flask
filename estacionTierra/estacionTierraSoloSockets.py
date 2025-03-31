# instalar pymavlink, paho-mqtt (version 1.6.1), opencv-python, requests
# websocket-client, python-socketio

import json
import os

import threading
import tkinter as tk

import numpy as np

from Dron import Dron

import time
import socketio
import cv2
import base64
from PIL import Image, ImageTk


def procesarTelemetria(telemetryInfo):
    # cada vez que recibo un paquete de telemetría del dron lo envio al broker
    sio.emit ('telemetryInfo', json.dumps(telemetryInfo))


def publish_event ( event):
    global sio
    # publico en el broker el evento, que en este caso será 'flying' porque es el único que se
    # considera en esta aplicación
    print ('en el aire')
    sio.emit ('event', event)


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
    global lastFrame


    sendingWebsockets= True
    # espero el tiempo establecido según la frecuencia seleccionada
    periodo = 1 / frequencySlider.get()
    while sendingWebsockets:
        if frequencySlider.get() > 0:
            ret, frame = cap.read()
            if not ret:
                break
            lastFrame = frame
            if grabando:
                out.write(frame)
            # genero el frame con el nivel de calidad seleccionado (entre 0 y 100)
            quality = qualitySlider.get()
            _, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
            frame_b64 = base64.b64encode(buffer).decode('utf-8')
            # envio el frame por el webbsocket
            print ("Envio")
            sio.emit('frame_Websocket', frame_b64)
            time.sleep(periodo)

def mostrar_imagen():
    global fotos, index, CARPETA_FOTOS , fotoLbl
    global imagen, imagen_tk
    ruta_imagen = os.path.join("fotos", fotos[index])
    imagen = Image.open(ruta_imagen)
    imagen = imagen.resize((640, 480))
    imagen_tk = ImageTk.PhotoImage(imagen)
    fotoLbl.config(image=imagen_tk)

def galeria ():
    global fotos, index, mostrandoVideos
    # deshabilito el evento de captura del raton porque no quiero hacer nada al clicar sobre la foto
    fotoLbl.unbind("<Button-1>")
    fotosFrame.grid(row=0, column=1, rowspan = 15, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)
    fotos = [f for f in os.listdir('fotos') if f.endswith((".png", ".jpg", ".jpeg", ".gif"))]
    index = 0
    mostrandoVideos = False
    mostrar_imagen()

def siguiente ():
    global fotos, videos, index
    global mostrandoVideos

    if mostrandoVideos:
        index = (index + 1) % len(videos)
        mostrar_video()
    else:
        index = (index + 1) % len(fotos)
        mostrar_imagen()
def anterior ():
    global fotos, videos, index
    global mostrandoVideos

    if mostrandoVideos:
        index = (index - 1) % len(videos)
        mostrar_video()
    else:
        index = (index - 1) % len(fotos)
        mostrar_imagen()

def mostrar_video ():
    global videos, index, imagen_tk, imagen, fotoLbl
    ruta_video = os.path.join("videos", videos[index])
    cap = cv2.VideoCapture(ruta_video)
    ret, frame = cap.read()
    cap.release()

    if ret:
        # muestro una imagen del video
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        imagen = Image.fromarray(frame)
        imagen = imagen.resize((640, 480))
        imagen_tk = ImageTk.PhotoImage(imagen)
        fotoLbl.config(image=imagen_tk)
    else:
        fotoLbl.config(text="No se pudo cargar la miniatura")

def reproducir_video (event):
    global videos, index, fotoLbl

    # extraigo del nombre del fichero el FPS
    nombreFichero = videos[index]
    FPS = nombreFichero.split('_')[1]
    FPS = int (FPS.split('.')[0])

    ruta_video = os.path.join('videos', videos[index])
    cap = cv2.VideoCapture(ruta_video)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        cv2.imshow("Reproduciendo", frame)
        # Espero el tiempo correspondiente a FPS para que el video se muestre correctamente
        if cv2.waitKey(1000//FPS) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def galeriaVideos ():
    global videos, index, mostrandoVideos
    fotosFrame.grid(row=0, column=1, rowspan=15, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

    videos = [f for f in os.listdir("videos") if f.endswith((".mp4", ".avi", ".mov", ".mkv"))]
    index = 0
    fotoLbl.bind("<Button-1>", reproducir_video)
    mostrandoVideos = True
    mostrar_video()



def recibirCamaraThread():
    global latest_frame
    global receivingCamera
    global contador
    # nombre de la ventana tiene que ser diferente cada vez que inicio el thread
    # para eso uno el contador
    while receivingCamera:
        if latest_frame is not None:
            cv2.imshow("Video camara " + str(contador), latest_frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

def recibirCamara ():
    global receivingCamera
    global cameraBtn
    global contador


    if receivingCamera:
        receivingCamera = False
        cameraBtn['text'] = "Recibir video del movil"
        cameraBtn['fg'] = 'black'
        cameraBtn['bg'] = 'dark orange'
    else:
        contador = contador + 1
        receivingCamera = True
        cameraBtn['text'] = "Detener video del movil"
        cameraBtn['fg'] = 'white'
        cameraBtn['bg'] = 'green'
        threading.Thread (target = recibirCamaraThread).start()


# Capturar video desde la cámara
cap = cv2.VideoCapture(0)

sendingWebsockets = False
sio = socketio.Client()
cont = 0
grabando = False
contVideos = 0

receivingCamera = False
contador = 0


# esto es para conectarme al websocket del servidor en desarrollo
sio.connect('http://localhost:8767')


# esto es para conectarme al websocket del servidor en producción
#sio.connect('http://dronseetac.upc.edu:8106')

# aquí atiendo todos los mensajes que me llegan del servidor via websocket

@sio.event
def processed_frame(data):
    # aqui entramos cada vez que recibimos un frame de la cámara del movil
    global latest_frame
    print ("recibo frame de camara")
    frame_bytes = base64.b64decode(data.split(",")[1])
    # Convertir los bytes en un array NumPy
    np_arr = np.frombuffer(frame_bytes, np.uint8)
    # Decodificar la imagen
    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    latest_frame = frame

@sio.event
def conectar():
    print ("recibo connect")
    # me conecto al simulador
    connection_string = 'tcp:127.0.0.1:5763'
    baud = 115200
    dron.connect(connection_string, baud)
    print('conectado')
    # le pido los datos de telemetria y le indico la función a ejecutar cada vez que tenga un nuevo
    # paquete de datos
    print('pido datos de telemetria')
    dron.send_telemetry_info(procesarTelemetria)


@sio.event
def arm_takeOff(altura):
    print ("recibo takeoff ", altura)
    if dron.state == 'connected':
        dron.arm()
        print ('armado')
        # operación no bloqueante. Cuando acabe publicará el evento correspondiente
        dron.takeOff(float(altura), blocking=False, callback=publish_event, params='flying')

@sio.event
def Land():
    print ("recibo Land")
    if dron.state == 'flying':
        print('voy a aterrizar')
        # operación no bloqueante
        dron.Land(blocking=False)

@sio.event
def go(direction):
    print ("recibo go: ", direction)
    if dron.state == 'flying':
        dron.go(direction)

@sio.event
def foto():
    global cont, lastFrame
    print ("recibo foto")
    cont = cont + 1
    nombreFichero = "fotos/foto" + str(cont) + ".jpg"
    cv2.imwrite(nombreFichero, lastFrame)


@sio.event
def startRecord():
    global contVideos, frequencySlider, out, grabando
    print ("recibo startRecord")
    grabando = True
    contVideos = contVideos + 1
    FPS = frequencySlider.get()
    # añado los FPS al nombre del fichero porque necesitaré ese número en el momento
    # de la reproducción del vídeo
    nombreFicheroVideo = "videos/video" + str(contVideos) + "_" + str(FPS) + ".mp4"
    # Obtener el ancho y alto del video
    ancho = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    alto = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Definir el codec y crear el objeto VideoWriter
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(nombreFicheroVideo, fourcc, 30.0, (ancho, alto))

@sio.event
def stopRecord():
    global grabando, out
    print ("recibo stopRecord")
    grabando = False
    out.release()


print("Conectado al websocket")
dron = Dron()

ventana = tk.Tk()
ventana.geometry ('900x600')
ventana.title("Pequeña estación de tierra")


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
ventana.rowconfigure(13, weight=1)
ventana.rowconfigure(14, weight=1)

ventana.columnconfigure(0, weight=1)
ventana.columnconfigure(1, weight=10)


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

videoWebsocketBtn = tk.Button(ventana, text="Enviar video por websockets", bg="dark orange", command=videoWebsockets)
videoWebsocketBtn.grid(row=10, column=0, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

videoStreamControlFrame = tk.LabelFrame(ventana, text="Video stream control", padx=5, pady=5)
videoStreamControlFrame.grid(row=11, column=0, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)
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
    tickinterval=100,
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
    tickinterval=30,
    resolution=1
)
frequencySlider.set(5)
frequencySlider.grid(row=1, column=1, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

galeriaBtn = tk.Button(ventana, text="Mostrar fotos", bg="dark orange", command=galeria)
galeriaBtn.grid(row=12, column=0, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)
galeriaVideosBtn = tk.Button(ventana, text="Mostrar videos", bg="dark orange", command=galeriaVideos)
galeriaVideosBtn.grid(row=13, column=0, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

fotosFrame = tk.LabelFrame (ventana, text = "Fotos")
#fotosFrame.grid(row=0, column=1, rowspan = 14, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)
fotosFrame.rowconfigure(0, weight=1)
fotosFrame.rowconfigure(1, weight=1)
fotosFrame.columnconfigure(0, weight=1)
fotosFrame.columnconfigure(1, weight=1)

fotoLbl = tk.Label(fotosFrame)
fotoLbl.grid(row=0, column=0, columnspan = 2, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)
siguienteBtn = tk.Button(fotosFrame, text="Siguiente", bg="dark orange", command=siguiente)
siguienteBtn.grid(row=1, column=1, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)
anteriorBtn = tk.Button(fotosFrame, text="Anterior", bg="dark orange", command=anterior)
anteriorBtn.grid(row=1, column=0, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)


cameraBtn = tk.Button(ventana, text="Recibir video del movil", bg="dark orange", command=recibirCamara)
cameraBtn.grid(row=14, column=0, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)


ventana.mainloop()