import tkinter as tk
from tkinter import messagebox, ttk
from data.db import adauga_autoturism, sterge_autoturism, sortare_autoturisme, cautare_autoturisme, actualizeaza_camp
from data.db import toate_autoturismele
from tkinter import ttk
import qrcode
from PIL import Image, ImageTk, ExifTags
import socket
from pornire_ngrok import porneste_ngrok
import subprocess, sys, os
porneste_ngrok()
start_x = None
start_y = None
rect = None
cropped_image = None

def porneste_server_upload():
    path = os.path.join(os.path.dirname(__file__), "server_upload.py")
    subprocess.Popen([sys.executable, path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

porneste_server_upload()

root = tk.Tk()
root.title("Evidenta Autoturisme Inmatriculate")
root.geometry("900x600")
root.configure(bg="#f7f7f7")

FONT_TITLU = ("Euphemia", 24, "bold")
FONT_BUTON = ("Euphemia", 11)
CULOARE_FUNDAL = "#f7f7f7"
CULOARE_BUTON = "#e0e0e0"

titlu = tk.Label(root, text="Evidenta Autoturismelor Inmatriculate",
                 font=FONT_TITLU, bg=CULOARE_FUNDAL, fg="#333")
titlu.pack(pady=20)

main_frame = tk.Frame(root, bg=CULOARE_FUNDAL)
main_frame.pack(fill="both", expand=True, padx=20, pady=10)

meniu_frame = tk.Frame(main_frame, bg="#ffffff", bd=1, relief="solid", width=200)
meniu_frame.pack(side="left", fill="y", padx=(0, 10))

logo_label = tk.Label(meniu_frame, text="PROIECT PA", font=("Segoe UI", 16, "bold"),
                      bg="#ffffff", fg="#222")
logo_label.pack(pady=(30, 40))

wrapper = tk.Frame(meniu_frame, bg="#ffffff")
wrapper.pack(expand=True)

zona_dreapta = tk.Frame(main_frame, bg="#ffffff", bd=1, relief="solid")
zona_dreapta.pack(side="left", fill="both", expand=True)

def afisare_autoturisme():
    from data.db import toate_autoturismele, sterge_autoturism, cautare_autoturisme

    for widget in zona_dreapta.winfo_children():
        widget.destroy()


    tk.Label(zona_dreapta, text="Autoturisme Înmatriculate",
             font=("Segoe UI", 16, "bold"), bg="#ffffff")\
        .pack(pady=(10, 10))

    frame_cautare = tk.Frame(zona_dreapta, bg="#ffffff")
    frame_cautare.pack(pady=(0, 10), padx=20, anchor="w")

    tk.Label(frame_cautare, text="Caută după:", font=("Segoe UI", 11), bg="#ffffff")\
        .pack(side="left", padx=(0, 10))

    criterii = ["Proprietar", "Numar inmatriculare"]
    criteriu_var = tk.StringVar(value="Proprietar")
    combobox = ttk.Combobox(frame_cautare, values=criterii, textvariable=criteriu_var, state="readonly", width=20)
    combobox.pack(side="left")

    entry_var = tk.StringVar()
    entry = tk.Entry(frame_cautare, textvariable=entry_var, font=("Segoe UI", 11), width=30)
    entry.pack(side="left", padx=10)

    def cauta():
        nonlocal toate
        valoare = entry_var.get().strip()
        criteriu = criteriu_var.get()

        if not valoare:
            messagebox.showwarning("Camp gol", "Introdu un text pentru cautare.")
            return

        toate = cautare_autoturisme(criteriu, valoare)
        incarca_tabel()

    def reseteaza():
        nonlocal toate, sort_key, sort_reverse
        entry_var.set("")
        toate = toate_autoturismele()
        sort_key = None
        sort_reverse = False
        incarca_tabel()

    tk.Button(frame_cautare, text="Caută", font=("Segoe UI", 10), command=cauta)\
        .pack(side="left", padx=5)

    tk.Button(frame_cautare, text="Resetează", font=("Segoe UI", 10), command=reseteaza)\
        .pack(side="left", padx=5)

    frame_tabel = tk.Frame(zona_dreapta, bg="#ffffff")
    frame_tabel.pack(fill="both", expand=True, padx=20, pady=(5, 5))

    scrollbar_y = tk.Scrollbar(frame_tabel, orient="vertical")
    scrollbar_y.pack(side="right", fill="y")

    coloane = ["Numar", "Marca", "Model", "Combustibil", "Proprietar"]
    col_index_map = {
        "Numar": 0,
        "Marca": 1,
        "Model": 2,
        "Combustibil": 6,
        "Proprietar": 8
    }

    tree = ttk.Treeview(frame_tabel, columns=coloane, show="headings", yscrollcommand=scrollbar_y.set)
    scrollbar_y.config(command=tree.yview)
    tree.pack(fill="both", expand=True)

    for col in coloane:
        tree.heading(col, text=col, command=lambda c=col: sorteaza_dupa_coloana(c))
        tree.column(col, anchor="center", width=130)

    toate = toate_autoturismele()
    sort_key = None
    sort_reverse = False

    def incarca_tabel():
        tree.delete(*tree.get_children())
        date_afisare = sorted(toate, key=lambda x: x[col_index_map[sort_key]] if sort_key else 0,
                              reverse=sort_reverse) if sort_key else toate
        for auto in date_afisare:
            tree.insert("", "end", values=(auto[0], auto[1], auto[2], auto[6], auto[8]))

    def sorteaza_dupa_coloana(col):
        nonlocal sort_key, sort_reverse
        if sort_key == col:
            sort_reverse = not sort_reverse
        else:
            sort_key = col
            sort_reverse = False
        incarca_tabel()

    incarca_tabel()

    def sterge_selectat():
        selected = tree.focus()
        if not selected:
            messagebox.showwarning("Atentie", "Selecteaza un autoturism din lista.")
            return
        index = tree.index(selected)
        try:
            auto = toate[index]
        except IndexError:
            messagebox.showerror("Eroare", "Selectie invalida.")
            return
        confirm = messagebox.askyesno("Confirmare stergere",
                                      f"Esti sigur ca vrei sa stergi autoturismul cu nr: {auto[0]}?")
        if confirm:
            sterge_autoturism(auto[0])
            messagebox.showinfo("Sters", "Autoturismul a fost șters.")
            reseteaza()



    detalii_frame = tk.Frame(zona_dreapta, bg="#f3f3f3", bd=1, relief="solid")
    detalii_frame.pack(fill="x", padx=20, pady=10)

    tk.Label(detalii_frame, text="Detalii autoturism selectat",
             font=("Segoe UI", 13, "bold"), bg="#f3f3f3")\
        .pack(pady=(10, 0))

    detalii_text_frame = tk.Frame(detalii_frame, height=250, bg="#ffffff")
    detalii_text_frame.pack(padx=10, pady=10, fill="both", expand=True)

    detalii_text = tk.Text(detalii_text_frame, font=("Segoe UI", 10),
                           bg="#ffffff", wrap="word", state="disabled")
    detalii_text.pack(fill="both", expand=True)

    def afiseaza_detalii(event):
        selected = tree.focus()
        if not selected:
            return
        index = tree.index(selected)
        try:
            auto = toate[index]
        except IndexError:
            return

        text = f"""
Număr înmatriculare: {auto[0]}
Marca: {auto[1]}
Model: {auto[2]}
Categorie vehicul: {auto[3]}
Capacitate cilindrică: {auto[4]} cm³
Putere motor: {auto[5]} kW
Combustibil: {auto[6]}
Serie VIN: {auto[7]}
Proprietar: {auto[8]}
Adresă: {auto[9]}
Data înmatriculării: {auto[10]}
Data primei înmatriculări: {auto[11]}
""".strip()

        detalii_text.configure(state="normal")
        detalii_text.delete("1.0", tk.END)
        detalii_text.insert(tk.END, text)
        detalii_text.configure(state="disabled")

    tree.bind("<<TreeviewSelect>>", afiseaza_detalii)

    def editeaza_celula(event):
        region = tree.identify("region", event.x, event.y)
        if region != "cell":
            return

        row_id = tree.identify_row(event.y)
        col_id = tree.identify_column(event.x)

        if not row_id or not col_id:
            return

        col_index = int(col_id[1:]) - 1
        x, y, width, height = tree.bbox(row_id, col_id)

        valoare_veche = tree.set(row_id, column=coloane[col_index])
        entry = tk.Entry(tree)
        entry.insert(0, valoare_veche)
        entry.place(x=x, y=y, width=width, height=height)
        entry.focus()

        def salveaza_modificarea(event=None):
            noua_valoare = entry.get()
            tree.set(row_id, column=coloane[col_index], value=noua_valoare)
            entry.destroy()

            index = tree.index(row_id)
            try:
                auto = toate[index]
                numar_inm = auto[0]

                db_col_map = {
                    "Numar": "numar_inmatriculare",
                    "Marca": "marca",
                    "Model": "model",
                    "Combustibil": "combustibil",
                    "Proprietar": "proprietar"
                }

                camp = db_col_map.get(coloane[col_index])
                if camp:
                    actualizeaza_camp(numar_inm, camp, noua_valoare)
            except Exception as e:
                print("Eroare la salvare:", e)

        entry.bind("<Return>", salveaza_modificarea)
        entry.bind("<FocusOut>", salveaza_modificarea)

    tree.bind("<Double-1>", editeaza_celula)

    def sterge_selectat_din_tasta(event):
        selected = tree.focus()
        if not selected:
            return

        index = tree.index(selected)
        try:
            auto = toate[index]
        except IndexError:
            return

        confirm = messagebox.askyesno("Confirmare ștergere",
                                      f"Ești sigur că vrei să ștergi autoturismul cu nr: {auto[0]}?")
        if confirm:
            sterge_autoturism(auto[0])
            messagebox.showinfo("Șters", "Autoturismul a fost șters.")
            afisare_autoturisme()

    tree.bind("<Delete>", sterge_selectat_din_tasta)


def deschide_formular_inmatriculare():
    for widget in zona_dreapta.winfo_children():
        widget.destroy()

    tk.Label(zona_dreapta, text="Formular Înmatriculare Autoturism",
             font=("Segoe UI", 18, "bold"), bg="#ffffff").pack(pady=(10, 10))

    def incarca_din_certificat():
        try:
            from ocr_latest import extrage_din_ultima_imagine
            from PIL import ImageTk
            import qrcode

            url = porneste_ngrok(port=5000)
            if not url:
                messagebox.showerror("Eroare", "Nu s-a putut genera link-ul ngrok.")
                return
            url += "?ngrok-skip-browser-warning=true"
            qr_img = qrcode.make(url)

            qr_window = tk.Toplevel()
            qr_window.title("Scanează codul QR")
            qr_window.geometry("400x450")
            qr_window.configure(bg="#ffffff")

            tk.Label(qr_window, text="Scanează codul QR cu telefonul",
                     font=("Segoe UI", 12, "bold"), bg="#ffffff").pack(pady=(10, 5))

            qr_tk = ImageTk.PhotoImage(qr_img)
            qr_label = tk.Label(qr_window, image=qr_tk, bg="#ffffff")
            qr_label.image = qr_tk
            qr_label.pack(pady=10)

            tk.Label(qr_window, text=url, font=("Segoe UI", 10),
                     fg="gray", bg="#ffffff").pack(pady=(0, 10))

            def dupa_inchidere():
                try:
                    from server_upload_verificare import ultima_imagine_uploadata
                    from ocr_latest import crop_automat_cu_opencv, ocr_pe_crop
                    from PIL import ImageTk, Image

                    imagine_path = ultima_imagine_uploadata()
                    print(f"Imagine detectata: {imagine_path}")

                    if not imagine_path:
                        messagebox.showerror("Eroare", "Nu s-a gasit imagine încarcata.")
                        return

                    cale_crop = crop_automat_cu_opencv(imagine_path, debug=False)

                    # Dacă cropul a eșuat complet, treci la crop manual
                    if cale_crop is None or not os.path.exists(cale_crop):
                        messagebox.showwarning("Crop automat esuat",
                                               "Nu s-a detectat automat conturul certificatului.")
                        selecteaza_crop_si_OCR(imagine_path)
                        return

                    # Deschide oricum preview-ul, chiar dacă e fallback
                    confirm_window = tk.Toplevel()
                    confirm_window.title("Confirmare crop automat")
                    confirm_window.configure(bg="#ffffff")

                    img_crop = Image.open(cale_crop)
                    img_crop = img_crop.resize((600, 400), Image.LANCZOS)
                    tk_img = ImageTk.PhotoImage(img_crop)

                    label_img = tk.Label(confirm_window, image=tk_img, bg="#ffffff")
                    label_img.image = tk_img
                    label_img.pack(pady=10)

                    tk.Label(confirm_window, text="Este aceasta zona corectă a certificatului?",
                             font=("Segoe UI", 11), bg="#ffffff").pack(pady=(0, 10))

                    def accepta_crop():
                        confirm_window.destroy()
                        from ocr_latest import extrage_din_ultima_imagine
                        valori = extrage_din_ultima_imagine()
                        for camp, valoare in valori.items():
                            if camp in entry_vars and valoare:
                                entry_vars[camp].delete(0, tk.END)
                                entry_vars[camp].insert(0, valoare)

                    def respinge_crop():
                        confirm_window.destroy()
                        selecteaza_crop_si_OCR(imagine_path)

                    btn_frame = tk.Frame(confirm_window, bg="#ffffff")
                    btn_frame.pack(pady=10)

                    tk.Button(btn_frame, text="Da, e corect", command=accepta_crop,
                              font=("Segoe UI", 10), bg="#4CAF50", fg="white", padx=10) \
                        .pack(side="left", padx=10)

                    tk.Button(btn_frame, text="Nu, selectez manual", command=respinge_crop,
                              font=("Segoe UI", 10), bg="#F44336", fg="white", padx=10) \
                        .pack(side="left", padx=10)

                except Exception as e:
                    print(f"Fallback la crop manual: {e}")
                    try:
                        from server_upload_verificare import ultima_imagine_uploadata
                        imagine_path = ultima_imagine_uploadata()
                        selecteaza_crop_si_OCR(imagine_path)
                    except Exception as err:
                        print(f" Eroare la fallback OCR manual: {err}")

            qr_window.protocol("WM_DELETE_WINDOW", lambda: (qr_window.destroy(), dupa_inchidere()))
            initiale = set(os.listdir("uploads"))

            def verifica_upload_nou():
                curente = set(os.listdir("uploads"))
                noi = curente - initiale

                for f in noi:
                    nume = f.lower()
                    if nume.endswith((".jpg", ".jpeg", ".png")) and "cropped" not in nume:
                        print(f"Imagine nouă detectată: uploads\\{f}")
                        qr_window.destroy()
                        root.after(300, dupa_inchidere)  # rulează după închiderea ferestrei
                        return

                qr_window.after(1000, verifica_upload_nou)

            verifica_upload_nou()  # pornește verificarea periodică


        except ImportError as err:
            messagebox.showerror("Eroare Import", f"Modul lipsă: {err}")

    btn_ocr = tk.Button(zona_dreapta, text="Incarca certificat auto (OCR)",
                        font=("Segoe UI", 10, "bold"), bg="#1976D2", fg="white",
                        activebackground="#1565C0", padx=15, pady=8,
                        command=incarca_din_certificat)
    btn_ocr.pack(pady=(0, 10))


    canvas = tk.Canvas(zona_dreapta, bg="#ffffff", highlightthickness=0)
    scrollbar = tk.Scrollbar(zona_dreapta, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg="#ffffff")
    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True, padx=20, pady=10)
    scrollbar.pack(side="right", fill="y")

    def on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    canvas.bind_all("<MouseWheel>", on_mousewheel)

    sectiuni = {
        "Date vehicul": [
            ("Numar de inmatriculare", "numar"),
            ("Marca", "marca"),
            ("Model", "model"),
            ("Categorie vehicul", "categorie"),
            ("Serie VIN", "vin")
        ],
        "Date tehnice": [
            ("Capacitate cilindrica (cm³)", "capacitate"),
            ("Putere motor (kW)", "putere"),
            ("Combustibil", "combustibil")
        ],
        "Date proprietar": [
            ("Nume proprietar", "proprietar"),
            ("Adresa proprietar", "adresa")
        ],
        "Date inmatriculare": [
            ("Data inmatricularii (YYYY-MM-DD)", "data_inm"),
            ("Data primei inmatriculari (YYYY-MM-DD)", "data_prim")
        ]
    }

    global entry_vars
    entry_vars = {}
    row = 0
    for titlu, campuri in sectiuni.items():
        tk.Label(scrollable_frame, text=titlu, font=("Segoe UI", 14, "bold"),
                 bg="#ffffff", fg="#333").grid(row=row, column=0, columnspan=2, sticky="w", pady=(20, 10), padx=10)
        row += 1
        for label_text, var_name in campuri:
            tk.Label(scrollable_frame, text=label_text, font=("Segoe UI", 11), bg="#ffffff")\
                .grid(row=row, column=0, sticky="e", padx=(10, 5), pady=6)

            entry = tk.Entry(scrollable_frame, font=("Segoe UI", 11), width=50)
            entry.grid(row=row, column=1, sticky="w", padx=(0, 20), pady=6)

            entry_vars[var_name] = entry
            row += 1

    def submit():
        try:
            numar = entry_vars["numar"].get()
            marca = entry_vars["marca"].get()
            model = entry_vars["model"].get()
            categorie = entry_vars["categorie"].get()
            capacitate = int(entry_vars["capacitate"].get())
            putere = int(entry_vars["putere"].get())
            combustibil = entry_vars["combustibil"].get()
            vin = entry_vars["vin"].get()
            proprietar = entry_vars["proprietar"].get()
            adresa = entry_vars["adresa"].get()
            data_inm = entry_vars["data_inm"].get()
            data_prim = entry_vars["data_prim"].get()

            adauga_autoturism(
                numar, marca, model, categorie, capacitate,
                putere, combustibil, vin, proprietar,
                adresa, data_inm, data_prim
            )

            messagebox.showinfo("Succes", "Autoturismul a fost inmatriculat cu succes!")
            for entry in entry_vars.values():
                entry.delete(0, tk.END)

        except Exception as e:
            messagebox.showerror("Eroare", f"A aparut o eroare: {e}")

    tk.Button(scrollable_frame, text="Înmatriculează", font=("Segoe UI", 12, "bold"),
              bg="#4CAF50", fg="white", padx=30, pady=10, command=submit)\
        .grid(row=row + 1, column=0, columnspan=2, pady=30)



def radiere_autoturism():
    for widget in zona_dreapta.winfo_children():
        widget.destroy()
    tk.Label(zona_dreapta, text="Funcție de radiere (de implementat)", font=("Segoe UI", 12), bg="#ffffff").pack(pady=20)
def cautare_proprietar():
    for widget in zona_dreapta.winfo_children():
        widget.destroy()
    tk.Label(zona_dreapta, text="Căutare după proprietar (de implementat)", font=("Segoe UI", 12), bg="#ffffff").pack(pady=20)
def cautare_numar():
    for widget in zona_dreapta.winfo_children():
        widget.destroy()
    tk.Label(zona_dreapta, text="Căutare după nr. înmatriculare (de implementat)", font=("Segoe UI", 12), bg="#ffffff").pack(pady=20)
def sortare_dupa_data():
    for widget in zona_dreapta.winfo_children():
        widget.destroy()
    tk.Label(zona_dreapta, text="Sortare după dată (de implementat)", font=("Segoe UI", 12), bg="#ffffff").pack(pady=20)
def sortare_dupa_model():
    for widget in zona_dreapta.winfo_children():
        widget.destroy()
    tk.Label(zona_dreapta, text="Sortare după model (de implementat)", font=("Segoe UI", 12), bg="#ffffff").pack(pady=20)
def sortare_dupa_capacitate():
    for widget in zona_dreapta.winfo_children():
        widget.destroy()
    tk.Label(zona_dreapta, text="Sortare după capacitate (de implementat)", font=("Segoe UI", 12), bg="#ffffff").pack(pady=20)
def cautare_autoturisme_ui():
    for widget in zona_dreapta.winfo_children():
        widget.destroy()
    tk.Label(zona_dreapta, text="Căutare Autoturisme",
             font=("Segoe UI", 16, "bold"), bg="#ffffff")\
        .pack(pady=(10, 10))
    cautare_frame = tk.Frame(zona_dreapta, bg="#ffffff")
    cautare_frame.pack(pady=10, padx=20, anchor="w")
    tk.Label(cautare_frame, text="Cauta dupa:", font=("Segoe UI", 11), bg="#ffffff")\
        .pack(side="left", padx=(0, 10))
    criterii = ["Proprietar", "Numar inmatriculare"]
    criteriu_var = tk.StringVar(value="Proprietar")
    combobox = ttk.Combobox(cautare_frame, values=criterii, textvariable=criteriu_var, state="readonly")
    combobox.pack(side="left")
    entry_var = tk.StringVar()
    entry = tk.Entry(cautare_frame, textvariable=entry_var, font=("Segoe UI", 11), width=30)
    entry.pack(side="left", padx=10)
    frame_tabel = tk.Frame(zona_dreapta, bg="#ffffff")
    frame_tabel.pack(fill="both", expand=True, padx=20, pady=(5, 10))
    scrollbar_y = tk.Scrollbar(frame_tabel, orient="vertical")
    scrollbar_y.pack(side="right", fill="y")
    coloane = ["Numar", "Marca", "Model", "Combustibil", "Proprietar"]
    tree = ttk.Treeview(frame_tabel, columns=coloane, show="headings", yscrollcommand=scrollbar_y.set)
    scrollbar_y.config(command=tree.yview)
    tree.pack(fill="both", expand=True)
    for col in coloane:
        tree.heading(col, text=col)
        tree.column(col, anchor="center", width=130)
    detalii_frame = tk.Frame(zona_dreapta, bg="#f3f3f3", bd=1, relief="solid")
    detalii_frame.pack(fill="x", padx=20, pady=10)
    tk.Label(detalii_frame, text="Detalii autoturism selectat",
             font=("Segoe UI", 13, "bold"), bg="#f3f3f3")\
        .pack(pady=(10, 0))
    detalii_text = tk.Text(detalii_frame, font=("Segoe UI", 10),
                           height=12, bg="#ffffff", wrap="word", state="disabled")
    detalii_text.pack(padx=10, pady=10, fill="x")
    def afiseaza_detalii(event):
        selected = tree.focus()
        if not selected:
            return
        index = tree.index(selected)
        try:
            auto = rezultate[index]
        except IndexError:
            return

        text = f"""
Număr înmatriculare: {auto[0]}
Marca: {auto[1]}
Model: {auto[2]}
Categorie vehicul: {auto[3]}
Capacitate cilindrică: {auto[4]} cm³
Putere motor: {auto[5]} kW
Combustibil: {auto[6]}
Serie VIN: {auto[7]}
Proprietar: {auto[8]}
Adresă: {auto[9]}
Data înmatriculării: {auto[10]}
Data primei înmatriculări: {auto[11]}
""".strip()

        detalii_text.configure(state="normal")
        detalii_text.delete("1.0", tk.END)
        detalii_text.insert(tk.END, text)
        detalii_text.configure(state="disabled")

    tree.bind("<<TreeviewSelect>>", afiseaza_detalii)

    def cauta():
        nonlocal rezultate
        criteriu = criteriu_var.get()
        valoare = entry_var.get().strip()

        if not valoare:
            messagebox.showwarning("Camp gol", "Introdu un text pentru cautare.")
            return

        tree.delete(*tree.get_children())
        rezultate = cautare_autoturisme(criteriu, valoare)

        for auto in rezultate:
            tree.insert("", "end", values=(auto[0], auto[1], auto[2], auto[6], auto[8]))

        detalii_text.configure(state="normal")
        detalii_text.delete("1.0", tk.END)
        detalii_text.configure(state="disabled")

    rezultate = []
    tk.Button(cautare_frame, text="Cauta", font=("Segoe UI", 10), command=cauta)\
        .pack(side="left", padx=10)


butoane = [
    ("Afișare", lambda: afisare_autoturisme()),
    ("Inmatriculare", deschide_formular_inmatriculare),
]
for text, comanda in butoane:
    btn = tk.Button(wrapper, text=text, font=FONT_BUTON,
                    bg=CULOARE_BUTON, relief="flat", padx=10, pady=10,
                    anchor="w", width=20, command=comanda)
    btn.pack(fill="x", padx=20, pady=6)
footer = tk.Label(meniu_frame, text="urziceanu david.", font=("Segoe UI", 9),
                  bg="#ffffff", fg="#999")
footer.pack(side="bottom", pady=10)

def deschide_qr_ocr():
    url = porneste_ngrok(port=5000)
    if url:
        url += "?ngrok-skip-browser-warning=true"
    if not url:
        messagebox.showerror("Eroare", "Nu s-a putut obține URL-ul public de la ngrok.")
        return

    import qrcode
    from PIL import ImageTk

    qr = qrcode.make(url)

    qr_window = tk.Toplevel()
    qr_window.title("Scanare cu telefonul")
    qr_window.geometry("400x450")
    qr_window.configure(bg="#ffffff")

    tk.Label(qr_window, text="Scanează codul QR cu telefonul",
             font=("Segoe UI", 12, "bold"), bg="#ffffff").pack(pady=(10, 5))

    qr_image = ImageTk.PhotoImage(qr)
    qr_label = tk.Label(qr_window, image=qr_image, bg="#ffffff")
    qr_label.image = qr_image
    qr_label.pack(pady=10)

    tk.Label(qr_window, text=url, font=("Segoe UI", 10),
             fg="gray", bg="#ffffff").pack(pady=(0, 10))

def selecteaza_crop_si_OCR(imagine_path):
    rect = None
    start_x = start_y = None
    img_full = None
    img_tk = None
    canvas = None
    scale = 1.0

    def on_button_press(event):
        nonlocal start_x, start_y, rect
        start_x = canvas.canvasx(event.x)
        start_y = canvas.canvasy(event.y)
        if rect:
            canvas.delete(rect)
        rect = canvas.create_rectangle(start_x, start_y, start_x, start_y, outline='red', width=2)

    def on_move_press(event):
        nonlocal rect
        cur_x = canvas.canvasx(event.x)
        cur_y = canvas.canvasy(event.y)
        if rect:
            canvas.coords(rect, start_x, start_y, cur_x, cur_y)

    def on_button_release(event):
        x1, y1, x2, y2 = map(int, canvas.coords(rect))
        real_x1 = int(x1 / scale)
        real_y1 = int(y1 / scale)
        real_x2 = int(x2 / scale)
        real_y2 = int(y2 / scale)

        crop = img_full.crop((real_x1, real_y1, real_x2, real_y2))
        save_path = os.path.join('uploads', 'cropped_certificat.jpg')
        crop.save(save_path)

        from ocr_latest import ocr_pe_crop
        valori = ocr_pe_crop(save_path)
        top.destroy()

    top = tk.Toplevel()
    top.title("Selectează zona certificatului")

    top.geometry("1100x900")

    img_full = Image.open(imagine_path)

    try:
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break
        exif = img_full._getexif()
        if exif:
            orientation_value = exif.get(orientation, None)
            if orientation_value == 3:
                img_full = img_full.rotate(180, expand=True)
            elif orientation_value == 6:
                img_full = img_full.rotate(270, expand=True)
            elif orientation_value == 8:
                img_full = img_full.rotate(90, expand=True)
    except Exception as e:
        print(f"Nu am putut corecta rotația: {e}")


    top.update_idletasks()
    window_width = top.winfo_width()
    window_height = top.winfo_height() - 50

    img_width, img_height = img_full.size
    scale_w = window_width / img_width
    scale_h = window_height / img_height
    scale = min(scale_w, scale_h)

    new_width = int(img_width * scale)
    new_height = int(img_height * scale)

    img_preview = img_full.resize((new_width, new_height), Image.LANCZOS)
    img_tk = ImageTk.PhotoImage(img_preview)

    canvas = tk.Canvas(top, width=new_width, height=new_height, bg="gray")
    canvas.pack(pady=(10, 5))
    canvas.create_image(0, 0, anchor="nw", image=img_tk)

    canvas.bind("<ButtonPress-1>", on_button_press)
    canvas.bind("<B1-Motion>", on_move_press)
    canvas.bind("<ButtonRelease-1>", on_button_release)

    top.mainloop()

afisare_autoturisme()
root.mainloop()
