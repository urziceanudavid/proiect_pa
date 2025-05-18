import sqlite3

def create_database():
    # Conectare (sau creare) baza de date
    conn = sqlite3.connect("autoturisme.db")
    cursor = conn.cursor()

    # Creăm tabela dacă nu există
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS autoturisme (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            marca TEXT NOT NULL,
            model TEXT NOT NULL,
            capacitate INTEGER NOT NULL,
            numar_inmatriculare TEXT UNIQUE NOT NULL,
            proprietar TEXT NOT NULL,
            data_inmatricularii TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()
    print("Baza de date și tabela 'autoturisme' au fost create cu succes.")

# Executăm direct dacă rulăm acest fișier individual
if __name__ == "__main__":
    create_database()
