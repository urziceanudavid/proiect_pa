import re
import pytesseract
from PIL import Image, ImageFilter, ExifTags
import os
import cv2
import numpy as np

def preprocesare(img):
    img = img.convert("L")
    img = img.point(lambda x: 0 if x < 140 else 255, '1')
    img = img.filter(ImageFilter.SHARPEN)
    return img

def crop_automat_cu_opencv(cale_imagine, debug=False):
    print(f"Incearca sa incarce: {cale_imagine}")
    img = cv2.imread(cale_imagine)
    if img is None:
        print(f"Eroare: nu s-a putut încarca imaginea {cale_imagine}")
        return None

    if img.shape[0] > img.shape[1] * 1.5:
        img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)

    orig = img.copy()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY_INV, 11, 2)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    edges = cv2.Canny(closed, 50, 150)

    if debug:
        cv2.imshow("Gray", gray)
        cv2.imshow("Thresh", thresh)
        cv2.imshow("Closed", closed)
        cv2.imshow("Edges", edges)
        cv2.waitKey(0)

    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    doc_cnt = None
    for c in contours:
        area = cv2.contourArea(c)
        if area < 10000:
            continue
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)

        if len(approx) == 4:
            # Verifică raportul de aspect
            rect = cv2.boundingRect(approx)
            ar = rect[2] / float(rect[3])
            if 1.3 < ar < 1.9:
                doc_cnt = approx
                break

    if doc_cnt is None:
        print("Nu s-a detectat automat conturul certificatului.")
        return None

    def ordoneaza_puncte(pts):
        pts = pts.reshape(4, 2)
        rect = np.zeros((4, 2), dtype="float32")
        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]
        rect[2] = pts[np.argmax(s)]
        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]
        rect[3] = pts[np.argmax(diff)]
        return rect

    rect = ordoneaza_puncte(doc_cnt)
    (tl, tr, br, bl) = rect

    widthA = np.linalg.norm(br - bl)
    widthB = np.linalg.norm(tr - tl)
    maxWidth = max(int(widthA), int(widthB))

    heightA = np.linalg.norm(tr - br)
    heightB = np.linalg.norm(tl - bl)
    maxHeight = max(int(heightA), int(heightB))

    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]], dtype="float32")

    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(orig, M, (maxWidth, maxHeight))

    base = "uploads/cropped"
    idx = 1
    while os.path.exists(f"{base}_{idx}.jpg"):
        idx += 1
    output_path = f"{base}_{idx}.jpg"
    cv2.imwrite(output_path, warped)

    if debug:
        cv2.imshow("Cropped", warped)
        cv2.waitKey(0)

    return output_path


corecturi = {
    "DS": "D.3", "D5": "D.3", "D-3": "D.3", "D,3": "D.3", "D..3": "D.3", "D .3": "D.3",
    "D1": "D.1", "D2": "D.2", "D3": "D.3",
    "=": "E", "= ": "E", " =": "E", " = ": "E",
    "|": "I", " |": "I", "| ": "I",
    "p1": "P.1", "p2": "P.2", ")P2": "P.2", "P1": "P.1", "P2": "P.2",
    "C2": "C.2", "C21": "C.2.1", "C22": "C.2.2", "C23": "C.2.3",
    "c2": "C.2", "c21": "C.2.1", "c22": "C.2.2", "c23": "C.2.3",
    "C 2 1": "C.2.1", "C 2 2": "C.2.2", "C 2 3": "C.2.3",
    "C. 2.1": "C.2.1", "C. 2.2": "C.2.2", "C. 2.3": "C.2.3"
}

def aplica_corecturi(text):
    for gresit, corect in corecturi.items():
        text = text.replace(gresit, corect)
    return text

def extrage_din_ultima_imagine(cale_imagine=None):
    if not cale_imagine:
        uploads_path = "uploads"
        fisiere = [f for f in os.listdir(uploads_path) if f.lower().endswith((".png", ".jpg", ".jpeg"))]
        fisiere.sort(reverse=True)
        cale_imagine = os.path.join(uploads_path, fisiere[0])

    img = Image.open(cale_imagine)
    img = preprocesare(img)
    custom_config = r'--oem 3 --psm 6'
    text = pytesseract.image_to_string(img, config=custom_config, lang="ron")
    text = aplica_corecturi(text)

    print("\n=== TEXT OCR ===\n", text)

    date = {
        "numar": None, "marca": None, "model": None, "categorie": None, "vin": None,
        "capacitate": None, "putere": None, "combustibil": None,
        "proprietar": None, "adresa": None, "data_inm": None, "data_prim": None
    }
    return date

    match = re.search(r"\b([A-Z]{1,2}[\s\-]?\d{2,3}[\s\-]?[A-Z]{2,3})\b", text)
    if match:
        date["numar"] = match.group(1).replace(" ", "").replace("-", "").upper()

    match = re.search(r"E[\s:=\-]*([A-Z0-9]{17})", text, re.IGNORECASE)
    if match:
        date["vin"] = match.group(1)

    match = re.search(r"D\.1\s*[:\-]?\s*([A-Z0-9\- ]{2,})", text)
    if match:
        date["marca"] = match.group(1).strip().upper()

    match = re.search(r"D\.3\s*[:\-]?\s*([A-Z0-9\- ]+)", text)
    if match:
        date["model"] = match.group(1).strip().upper()
    else:
        match = re.search(r"D\.2\s*[:\-]?[A-Z0-9\- ]+\s*\n(.+)", text)
        if match:
            date["model"] = match.group(1).strip().upper()

    combustibili = ["BENZINA", "MOTORINA", "ELECTRIC", "HIBRID"]
    for combustibil in combustibili:
        if combustibil in text.upper():
            date["combustibil"] = combustibil.capitalize()
            break

    match = re.search(r"P\.1\s*[:\-]?\s*(\d{3,5})", text)
    if match:
        date["capacitate"] = match.group(1)

    match = re.search(r"P\.2\s*[:\-]?\s*(\d{2,4})", text)
    if match:
        date["putere"] = match.group(1)

    match = re.search(r"J\s*[:\-]?\s*(AUTOTURISM|MOTOCICLU|AUTOUTILITARA|TR|ATV|M1|N1)", text.upper())
    if match:
        val = match.group(1).strip().upper()
        date["categorie"] = "Autoturism" if val in ["M1", "AUTOTURISM"] else val.title()

    match = re.search(r"\bB\s*[:\-]?\s*(\d{2}\.\d{2}\.\d{4})", text)
    if match:
        date["data_prim"] = match.group(1)

    match = re.search(r"\bI\s*[:\-]?\s*(\d{2}\.\d{2}\.\d{4})", text)
    if match:
        date["data_inm"] = match.group(1)

    match = re.search(r"C\.2\.1.*?([A-ZĂÂÎȘȚ \-']{3,})", text)
    nume = match.group(1).title() if match else ""
    match = re.search(r"C\.2\.2.*?([A-ZĂÂÎȘȚ \-']{3,})", text)
    prenume = match.group(1).title() if match else ""
    if nume or prenume:
        date["proprietar"] = f"{nume} {prenume}".strip()

    match = re.search(r"C\.2\.3\s*[:\-]?\s*(.+?)(?:\n|$)", text)
    if match:
        adresa = match.group(1).strip()
        lines = text.splitlines()
        for i, line in enumerate(lines):
            if "C.2.3" in line and i + 1 < len(lines):
                adresa += " " + lines[i + 1].strip()
                break
        date["adresa"] = adresa

    print("\n=== DATE EXTRASE ===")
    for k, v in date.items():
        print(f"{k}: {v}")

    return date

def ocr_pe_crop(cale_imagine):
    img = Image.open(cale_imagine)
    img = preprocesare(img)
    custom_config = r'--oem 3 --psm 6'
    text = pytesseract.image_to_string(img, config=custom_config, lang="ron")
    print("\n=== text extras ===\n", text)
    return text
