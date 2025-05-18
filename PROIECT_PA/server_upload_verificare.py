import os

def ultima_imagine_uploadata():
    uploads_path = "uploads"
    fisiere = [f for f in os.listdir(uploads_path) if f.lower().endswith((".png", ".jpg", ".jpeg"))]
    if not fisiere:
        return None
    fisiere.sort(reverse=True)
    return os.path.join(uploads_path, fisiere[0])
