# importar Flask, FlaskSocketIO, opencv-python (version 1.6.1)
import base64

from flask import Flask, render_template
from flask_socketio import SocketIO

import cv2
import numpy as np

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")


@app.route('/')
def index():
    # la web app solo va a recibir una petición HTTP para cargar el indice.html
    return render_template('indexCamara.html')

@socketio.on('frame_Websocket')
def handle_video_frame(data):
    # aqui recibimmos los frames que nos envía la estación de tierra por el websocket
    # enviamos el frame al navegador
    print ("recibo por websocket")
    socketio.emit('frame_Websocket_from_ground', data)


@socketio.on("frame_from_camera")
def handle_video(data):
    processed_frame = process_frame (data)
    # Enviar frame  al navegador y a la estación de tierra
    socketio.emit("processed_frame", f"data:image/jpeg;base64,{processed_frame}")


def process_frame(data):
    # el procesado del frame consiste en añadirle una frase
    try:

        img_data = base64.b64decode(data.split(",")[1])
        np_arr = np.frombuffer(img_data, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        frase = "Hola"
        cv2.putText(frame, frase, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Convertir frame procesado a base64
        _, buffer = cv2.imencode(".jpg", frame)
        processed_frame = base64.b64encode(buffer).decode("utf-8")
        return processed_frame

    except Exception as e:
        print(f"Error al procesar el frame: {e}")
        return None



if __name__ == '__main__':
    # hay que poner en marcha el servidor flask, al que se conectarán el navegador, y el websocket al que
    # se conectará la estación de tierra
    from threading import Thread
    # Pongo en marcha el servidor flask en un hilo separado
    # Uso el el puerto 5000 para el servidor en desarrollo
    # y el puerto 8104 para el servidor en producción (que es uno de los puertos abiertos en dronseetac.upc.edu)
    #flask_thread = Thread(target=lambda: app.run(host='0.0.0.0', port=5002, debug=True, use_reloader=False))

    flask_thread = Thread(target=lambda: app.run(host='0.0.0.0', port=5004, debug=True,ssl_context=("cert.pem", "key.pem"), use_reloader=False))

    flask_thread.start()
    # Pongo en marcha el websocket
    # Uso  el puerto 8766 para el servidor en desarrollo
    # y el puerto 8106 para el servidor en producción (que es uno de los puertos abiertos en dronseetac.upc.edu9
    socketio.run(app, host='0.0.0.0', port=8767, allow_unsafe_werkzeug=True)