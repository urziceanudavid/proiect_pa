import subprocess
import time
import requests

def porneste_ngrok(port=5000):
    subprocess.Popen(["ngrok", "http", str(port)], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    time.sleep(3)
    try:
        response = requests.get("http://localhost:4040/api/tunnels")
        tunnels = response.json()["tunnels"]
        for tunnel in tunnels:
            if tunnel["proto"] == "https":
                return tunnel["public_url"]
    except Exception as e:
        print("Eroare la obținerea URL-ului ngrok:", e)
        return None
