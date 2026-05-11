from extensions import db

class Alumno(db.Model):
    __tablename__ = 'alumno'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)
    cmp = db.Column(db.String(50), nullable=True)
    grupo = db.Column(db.Integer, nullable=False)

    evaluaciones = db.relationship('Evaluacion', backref='alumno', lazy=True)

class Estacion(db.Model):
    __tablename__ = 'estacion'
    id = db.Column(db.String(50), primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    orden = db.Column(db.Integer, nullable=False)

    categorias = db.relationship('Categoria', backref='estacion', lazy=True)
    evaluaciones = db.relationship('Evaluacion', backref='estacion', lazy=True)

class Categoria(db.Model):
    __tablename__ = 'categoria'
    id = db.Column(db.Integer, primary_key=True)
    estacion_id = db.Column(db.String(50), db.ForeignKey('estacion.id'), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    orden = db.Column(db.Integer, nullable=True)
    tipo = db.Column(db.String(50), nullable=True)
    
    criterios = db.relationship('Criterio', backref='categoria', lazy=True)

class Criterio(db.Model):
    __tablename__ = 'criterio'
    id = db.Column(db.String(50), primary_key=True)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categoria.id'), nullable=False)
    texto = db.Column(db.Text, nullable=False)
    puntos = db.Column(db.Float, default=1.0)
    tipo = db.Column(db.String(50), default='checkbox') 
    opciones = db.Column(db.Text, nullable=True)

class Evaluacion(db.Model):
    __tablename__ = 'evaluacion'
    id = db.Column(db.Integer, primary_key=True)
    alumno_id = db.Column(db.Integer, db.ForeignKey('alumno.id'), nullable=False)
    estacion_id = db.Column(db.String(50), db.ForeignKey('estacion.id'), nullable=False)
    puntaje_total = db.Column(db.Float, default=0.0)
    video_camara1 = db.Column(db.String(255), nullable=True)
    video_camara2 = db.Column(db.String(255), nullable=True)

    detalles = db.relationship('EvaluacionDetalle', backref='evaluacion', lazy=True, cascade='all, delete-orphan')

class EvaluacionDetalle(db.Model):
    __tablename__ = 'evaluacion_detalle'
    id = db.Column(db.Integer, primary_key=True)
    evaluacion_id = db.Column(db.Integer, db.ForeignKey('evaluacion.id'), nullable=False)
    criterio_id = db.Column(db.String(50), db.ForeignKey('criterio.id'), nullable=False)
    valor_registrado = db.Column(db.String(50), nullable=False)
