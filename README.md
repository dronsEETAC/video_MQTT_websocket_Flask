# video_MQTT_websocket_Flask

## Presentación
En este repositorio tenemos el código de estación de tierra en Python y una webapp en Flask. Desde la estación de tierra se puede controlar el dron (dron real o simulador SITL) mediante una botonera pero también puede recibir peticiones de control del dron desde una WebApp. El control del dron se realiza utilizando la librería droneLink.      

El tema central de estos demostradores es el envío del stream de vídeo desde la estación de tierra (por ejemplo, el video que viene del dron) a la webapp para que se muestre en el movil del usuario, y también el envío del stream de video capturado por la cámara del movil hasta la estación de tierra, pasando por el servidor donde el stream puede ser procesado (por ejemplo, para detectar poses del cuerpo con las que controlar el dron).

Hay tres versiones del código, que se describen a continuación.   

## estacionTierra + app   
La estación de tierra puede enviar al movil el stream de video via MQTT y también via websocket. La calidad del stream se controla desde la estación de tierra, en términos de resolución de los frames y en términos de frecuencia de frames. Puede comprobarse que la transmisión via websocket es más fluida que via MQTT.   

En el movil se recibe el stream y se puede pedir que se haga una foto o que se grabe un video. Las fotos y videos quedan guardados en la estación de tierra, que ofrece al usuario opcion de visualizar las fotos y videos guardados.   

La webapp usa la template que hay en el fichero index.html.    

## estacionTierraCamara + appCamara   
A las funcionalidades de la versión anterios se añade la posibilidad de enviar a la estación de tierra el stream de video capturado por la cámara del movil, pero pasando primero por el servidor, donde el stream de video puede ser procesado. En esta versión símplemente se añade una frase los frames, pero se podrían implementar opciones de procesado de imagen, antes de enviar los frames a tierra.     

En envío se hace vía websockets.    

La webapp trabaja con el template que hay en el fichero indexCamara.html.    

Para poder enviar el vídeo de la cámara del movil es necesario que la webapp use HTTPS, y por tanto se requieren certificados. El código de la webapp asume que existen los ficheros cert.pem y key.pem con los certificados. Generar estos ficheros con certificados autofirmados en Windows es muy fácil usando usando openssl.

## estacionTierraSoloSockets + appSoloSockets   
Esta versión tiene las mismas funcionalidades que las anteriores pero utiliza únicamente websockets para todas las comunicaciones entre estación de tierra, servidor y dispositivo móvil. De esta forma nos ahorramos tener que usar un broker MQTT.  

La webapp trabaja con el template que hay en el fichero indexSoloSockets.html.   



