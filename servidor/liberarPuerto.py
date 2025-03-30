import os
import sys
import subprocess


def kill_process_using_port(port: int):
    """Mata todos los procesos que están usando un puerto específico."""
    try:
        if sys.platform.startswith("win"):  # Windows
            result = subprocess.run(["netstat", "-ano"], capture_output=True, text=True)
            for line in result.stdout.splitlines():
                if f":{port} " in line:
                    pid = line.strip().split()[-1]
                    subprocess.run(["taskkill", "/PID", pid, "/F"], capture_output=True, text=True)
                    print(f"Proceso con PID {pid} terminado.")
        else:  # Linux / Mac
            result = subprocess.run(["lsof", "-i", f":{port}"], capture_output=True, text=True)
            for line in result.stdout.splitlines():
                if "LISTEN" in line:
                    pid = line.split()[1]
                    subprocess.run(["kill", "-9", pid], capture_output=True, text=True)
                    print(f"Proceso con PID {pid} terminado.")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    port = 8766
    kill_process_using_port(port)
    print ("Listo")
