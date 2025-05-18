import sqlite3

DB_PATH = "autoturisme.db"
def get_connection():
    return sqlite3.connect(DB_PATH)

def initialize_database():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS autoturisme (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numar_inmatriculare TEXT UNIQUE NOT NULL,
            marca TEXT NOT NULL,
            model TEXT NOT NULL,
            categorie_vehicul TEXT,
            capacitate INTEGER,
            putere_kw INTEGER,
            combustibil TEXT,
            serie_vin TEXT UNIQUE,
            proprietar TEXT NOT NULL,
            adresa_proprietar TEXT,
            data_inmatricularii TEXT NOT NULL,
            data_primei_inmatriculari TEXT
        )
    """)

    conn.commit()
    conn.close()

initialize_database()
def adauga_autoturism(
    numar_inmatriculare, marca, model, categorie, capacitate,
    putere_kw, combustibil, serie_vin, proprietar,
    adresa, data_inmatricularii, data_primei_inmatriculari
):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO autoturisme (
                numar_inmatriculare, marca, model, categorie_vehicul,
                capacitate, putere_kw, combustibil, serie_vin,
                proprietar, adresa_proprietar,
                data_inmatricularii, data_primei_inmatriculari
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            numar_inmatriculare, marca, model, categorie, capacitate,
            putere_kw, combustibil, serie_vin, proprietar,
            adresa, data_inmatricularii, data_primei_inmatriculari
        ))
        conn.commit()
    except Exception as e:
        print("Eroare la inserare:", e)
    finally:
        conn.close()

def toate_autoturismele():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT numar_inmatriculare, marca, model, categorie_vehicul,
               capacitate, putere_kw, combustibil, serie_vin,
               proprietar, adresa_proprietar, data_inmatricularii, data_primei_inmatriculari
        FROM autoturisme
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows

def sterge_autoturism(nr_inmatriculare):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM autoturisme WHERE numar_inmatriculare = ?", (nr_inmatriculare,))
    conn.commit()
    conn.close()

def sortare_autoturisme(criteriu):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT numar_inmatriculare, marca, model, categorie_vehicul,
               capacitate, putere_kw, combustibil, serie_vin,
               proprietar, adresa_proprietar, data_inmatricularii, data_primei_inmatriculari
    """

    if criteriu == "Model (A-Z)":
        query += " FROM autoturisme ORDER BY model ASC"
    elif criteriu == "Model (Z-A)":
        query += " FROM autoturisme ORDER BY model DESC"
    elif criteriu == "Capacitate (mică → mare)":
        query += " FROM autoturisme ORDER BY capacitate ASC"
    elif criteriu == "Capacitate (mare → mică)":
        query += " FROM autoturisme ORDER BY capacitate DESC"
    elif criteriu == "Dată înmatriculare (recentă → veche)":
        query += " FROM autoturisme ORDER BY data_inmatricularii DESC"
    elif criteriu == "Dată înmatriculare (veche → recentă)":
        query += " FROM autoturisme ORDER BY data_inmatricularii ASC"
    else:
        query += " FROM autoturisme"

    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    return rows

def cautare_autoturisme(criteriu, valoare):
    conn = get_connection()
    cursor = conn.cursor()

    if criteriu == "Proprietar":
        query = """
            SELECT numar_inmatriculare, marca, model, categorie_vehicul,
                   capacitate, putere_kw, combustibil, serie_vin,
                   proprietar, adresa_proprietar, data_inmatricularii, data_primei_inmatriculari
            FROM autoturisme
            WHERE LOWER(proprietar) LIKE ?
        """
        cursor.execute(query, (f"%{valoare.lower()}%",))
    elif criteriu == "Numar inmatriculare":
        query = """
            SELECT numar_inmatriculare, marca, model, categorie_vehicul,
                   capacitate, putere_kw, combustibil, serie_vin,
                   proprietar, adresa_proprietar, data_inmatricularii, data_primei_inmatriculari
            FROM autoturisme
            WHERE LOWER(numar_inmatriculare) LIKE ?
        """
        cursor.execute(query, (f"%{valoare.lower()}%",))
    else:
        cursor.execute("""
            SELECT numar_inmatriculare, marca, model, categorie_vehicul,
                   capacitate, putere_kw, combustibil, serie_vin,
                   proprietar, adresa_proprietar, data_inmatricularii, data_primei_inmatriculari
            FROM autoturisme
        """)

    rows = cursor.fetchall()
    conn.close()
    return rows

def actualizeaza_camp(numar_inmatriculare, camp, valoare_noua):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        query = f"UPDATE autoturisme SET {camp} = ? WHERE numar_inmatriculare = ?"
        cursor.execute(query, (valoare_noua, numar_inmatriculare))
        conn.commit()
    except Exception as e:
        print("Eroare la actualizare:", e)
    finally:
        conn.close()

