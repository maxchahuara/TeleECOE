import sqlite3
import os

db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'evaluaciones.db')

def migrate():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE evaluacion ADD COLUMN video_camara1 VARCHAR(255);")
        cursor.execute("ALTER TABLE evaluacion ADD COLUMN video_camara2 VARCHAR(255);")
        conn.commit()
        print("Migracion completada con exito.")
    except Exception as e:
        if "duplicate column name" in str(e).lower():
            print("Las columnas ya existen.")
        else:
            print(f"Error migrando base de datos: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    migrate()
