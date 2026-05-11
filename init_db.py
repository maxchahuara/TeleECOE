import os
from app import create_app
from extensions import db
from app.models import Alumno, Estacion, Categoria, Criterio, Evaluacion, EvaluacionDetalle

app = create_app()

def init_database():
    """Inicializa la base de datos creando todas las tablas."""
    
    with app.app_context():
        # Crear todas las tablas definidas en los modelos
        db.create_all()
        print("Tablas de la base de datos creadas satisfactoriamente en evaluaciones.db.")

if __name__ == '__main__':
    init_database()
