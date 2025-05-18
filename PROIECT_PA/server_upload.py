from flask import Flask, request, send_from_directory
import os
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def home():
    return send_from_directory("", "camera.html")

@app.route("/upload_capture", methods=["POST"])
def upload_capture():
    if "file" not in request.files:
        return "No file", 400
    f = request.files["file"]
    if f:
        filename = datetime.now().strftime("%Y%m%d_%H%M%S_") + secure_filename(f.filename)
        save_path = os.path.join(UPLOAD_FOLDER, filename)
        f.save(save_path)
        print(f"Imagine salvată la: {save_path}")
        return "Imagine salvată!"
    return "Fail", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
