
class Dron(object):
    def __init__(self):

        self.state = "disconnected"
        ''' los otros estados son:
                  connected
                  arming
                  armed
                  takingOff
                  flying
                  returning
                  landing
              '''
        self.lat = 0
        self.lon = 0
        self.alt = 0


        self.going = False # se usa en dron_nav
        self.navSpeed = 5 # se usa en dron_nav
        self.direction = 'Stop' # se usa en dron_nav
        self.id = None
        self.sendTelemetryInfo = False #usado en dron_telemetry

        self.sendLocalTelemetryInfo = False  # usado en dron_local_telemetry

        self.step = 1 # se usa en dron_mov. Son los metros que mueve en cada paso
        self.localGeofence = None # se usa en dron_mov para evitar que el dron se salga del espacio
        self.localGeofenceEnabled = False
        self.localGeofenceChecking = False
        self.localGeofenceBreachAction = 0
        # REVISAR ESTO
        #   0     Informar
        #   1     Informar y detener
        #   2     Informar y aterrizar inmediatamente
        self.localGeofenceBreachCallback = None # función que se activará cuando haya el breach
        self.localGeofenceBreachCallbackParams = None # parámetros para la función anterior
        self.position = [0,0,0] # se usa en dron_mov para identificar la posición del dron dentro del espacio
        self.heading = 0
        self.lastDirection = None

        self.lastPositionBeforeLocalGeofenceBreach = None
    # aqui se importan los métodos de la clase Dron, que están organizados en ficheros.
    # Así podría orgenizarse la aportación de futuros alumnos que necesitasen incorporar nuevos servicios
    # para sus aplicaciones. Crearían un fichero con sus nuevos métodos y lo importarían aquí
    # Lo que no me gusta mucho es que si esa contribución nueva requiere de algún nuevo atributo de clase
    # ese atributo hay que declararlo aqui y no en el fichero con los métodos nuevos.
    # Ese es el caso del atributo going, que lo tengo que declarar aqui y preferiría poder declararlo en el fichero dron_goto

    from modules.dron_connect import connect, _connect, disconnect, _handle_heartbeat
    from modules.dron_arm import arm, _arm
    from modules.dron_takeOff import takeOff, _takeOff
    from modules.dron_RTL_Land import  RTL, Land, _goDown
    from modules.dron_nav import _prepare_command, go, _startGo, _stopGo, _goingTread, changeHeading, fixHeading, unfixHeading, changeNavSpeed
    from modules.dron_goto import goto, _goto, _distanceToDestinationInMeters
    from modules.dron_flightPlan import executeFlightPlan, _executeFlightPlan
    from modules.dron_parameters import getParams, _getParams, setParams, _setParams
    from modules.dron_setGeofence import setGEOFence, _setGEOFence, getGEOFence, _getGEOFence
    from modules.dron_telemetry import send_telemetry_info, _send_telemetry_info, stop_sending_telemetry_info

    from modules.dron_local_telemetry import send_local_telemetry_info, _send_local_telemetry_info, stop_sending_local_telemetry_info
    from modules.dron_mov import move, _move, _prepare_command_mov, setStep, moveto, _moveto, _prepare_command_movto
    from modules.dron_mov import  _futurePosition, check, _distance, _destination,setNavSpeed, _recover
    from modules.dron_mission import executeMission, _executeMission
    from modules.dron_localGeofence import enableLocalGeofence, disableLocalGeofence, setLocalGeofenceBreachAction, setLocalGeofence, _inGeofence, _localGeofenceCheck, startLocalGeofenceChecking, stopLocalGeofenceChecking, _goToLastPositionBeforeLocalGeofenceBreach

    from modules.dron_RC_overrride import send_rc, status_loop, get_thruster_outputs, clear_motion