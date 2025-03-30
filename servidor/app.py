# importar Flask, FlaskSocketIO
from flask import Flask, render_template
from flask_socketio import SocketIO
import sys, subprocess
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def index():
    # la web app solo va a recibir una petición HTTP para cargar el indice.html
    return render_template('index.html')

@socketio.on('frame_Websocket')
def handle_video_frame(data):
    # aqui recibimmos los frames que nos envía la estación de tierra por el websocket
    # enviamos el frame al navegador
    print ("recibo frame de la estacion de tierra")
    socketio.emit('frame_Websocket_from_ground', data)

if __name__ == '__main__':
    # hay que poner en marcha el servidor flask, al que se conectarán el navegador, y el websocket al que
    # se conectará la estación de tierra
    from threading import Thread
    # Pongo en marcha el servidor flask en un hilo separado
    # Uso el el puerto 5000 para el servidor en desarrollo
    # y el puerto 8104 para el servidor en producción (que es uno de los puertos abiertos en dronseetac.upc.edu)
    flask_thread = Thread(target=lambda: app.run(host='0.0.0.0', port=5002, debug=True, use_reloader=False))
    flask_thread.start()
    # liberamos el puerto que usaré el websocket

    print ("Puerto liberado")
    # Pongo en marcha el websocket
    # Uso  el puerto 8766 para el servidor en desarrollo
    # y el puerto 8106 para el servidor en producción (que es uno de los puertos abiertos en dronseetac.upc.edu9
    socketio.run(app, host='0.0.0.0', port=8767, allow_unsafe_werkzeug=True)