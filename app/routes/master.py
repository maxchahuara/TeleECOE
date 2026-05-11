from flask import Blueprint, render_template, request, redirect, flash, url_for
from app.models.models import Alumno, Estacion, Categoria, Criterio, Evaluacion, EvaluacionDetalle
from extensions import db
import socket

master_bp = Blueprint('master', __name__)

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

@master_bp.route('/')
def dashboard():
    alumnos = Alumno.query.all()
    estaciones = Estacion.query.order_by(Estacion.orden).all()
    
    resultados = []
    for alu in alumnos:
        notas_estaciones = {}
        evaluaciones = {e.estacion_id: e for e in alu.evaluaciones}
        for est in estaciones:
            eval_record = evaluaciones.get(est.id)
            if eval_record:
                notas_estaciones[est.id] = {'estado': True, 'puntaje': eval_record.puntaje_total}
            else:
                notas_estaciones[est.id] = {'estado': False, 'puntaje': 0.0}
        
        resultados.append({
            'id': alu.id,
            'nombre': alu.nombre,
            'grupo': alu.grupo,
            'notas_estaciones': notas_estaciones
        })
        
    ip = get_local_ip()
    return render_template('master_dashboard.html', ip=ip, estaciones=estaciones, resultados=resultados)

@master_bp.route('/alumnos', methods=['GET', 'POST'])
def alumnos_admin():
    if request.method == 'POST':
        id_val = request.form.get('id')
        nombre = request.form.get('nombre')
        cmp = request.form.get('cmp')
        grupo = request.form.get('grupo')
            
        alumno = Alumno(nombre=nombre, cmp=cmp, grupo=int(grupo))
        if id_val and str(id_val).isdigit():
            alumno.id = int(id_val)
        db.session.add(alumno)
        db.session.commit()
        flash('Alumno agregado exitosamente.', 'success')
        return redirect(url_for('master.alumnos_admin'))
        
    alumnos = Alumno.query.all()
    return render_template('master_alumnos.html', alumnos=alumnos)

@master_bp.route('/alumnos/editar/<int:id>', methods=['GET', 'POST'])
def alumnos_editar(id):
    alumno = Alumno.query.get_or_404(id)
    if request.method == 'POST':
        alumno.nombre = request.form.get('nombre')
        alumno.grupo = int(request.form.get('grupo'))
        alumno.cmp = request.form.get('cmp')
            
        db.session.commit()
        flash('Alumno actualizado correctamente.', 'success')
        return redirect(url_for('master.alumnos_admin'))
        
    alumnos = Alumno.query.all()
    return render_template('master_alumnos.html', alumnos=alumnos, alumno_edit=alumno)

@master_bp.route('/alumnos/eliminar/<int:id>', methods=['POST'])
def alumnos_eliminar(id):
    alumno = Alumno.query.get_or_404(id)
    db.session.delete(alumno)
    db.session.commit()
    flash('Alumno eliminado.', 'success')
    return redirect(url_for('master.alumnos_admin'))

@master_bp.route('/estaciones', methods=['GET', 'POST'])
def estaciones_admin():
    if request.method == 'POST':
        id_val = request.form.get('id')
        nombre = request.form.get('nombre')
        orden = int(request.form.get('orden'))
        
        estacion = Estacion(id=id_val, nombre=nombre, orden=orden)
        db.session.add(estacion)
        db.session.commit()
        flash('Estación agregada.', 'success')
        return redirect(url_for('master.estaciones_admin'))
        
    estaciones = Estacion.query.order_by(Estacion.orden).all()
    return render_template('master_estaciones.html', estaciones=estaciones)

@master_bp.route('/estaciones/editar/<id>', methods=['GET', 'POST'])
def estaciones_editar(id):
    estacion = Estacion.query.get_or_404(id)
    if request.method == 'POST':
        estacion.nombre = request.form.get('nombre')
        estacion.orden = int(request.form.get('orden'))
        db.session.commit()
        flash('Estación actualizada.', 'success')
        return redirect(url_for('master.estaciones_admin'))
    estaciones = Estacion.query.order_by(Estacion.orden).all()
    return render_template('master_estaciones.html', estaciones=estaciones, estacion_edit=estacion)

@master_bp.route('/estaciones/eliminar/<id>', methods=['POST'])
def estaciones_eliminar(id):
    estacion = Estacion.query.get_or_404(id)
    db.session.delete(estacion)
    db.session.commit()
    flash('Estación eliminada.', 'success')
    return redirect(url_for('master.estaciones_admin'))

@master_bp.route('/estaciones/<id>/constructor', methods=['GET'])
def estaciones_constructor(id):
    estacion = Estacion.query.get_or_404(id)
    return render_template('master_constructor.html', estacion=estacion)

@master_bp.route('/categorias/nueva/<id_estacion>', methods=['POST'])
def categorias_nueva(id_estacion):
    estacion = Estacion.query.get_or_404(id_estacion)
    nombre = request.form.get('nombre')
    orden = request.form.get('orden', type=int, default=1)
    tipo = request.form.get('tipo', default='normal')
    
    categoria = Categoria(estacion_id=id_estacion, nombre=nombre, orden=orden, tipo=tipo)
    db.session.add(categoria)
    db.session.commit()
    flash('Categoría añadida exitosamente.', 'success')
    return redirect(url_for('master.estaciones_constructor', id=id_estacion))

@master_bp.route('/categorias/eliminar/<id>', methods=['POST'])
def categorias_eliminar(id):
    categoria = Categoria.query.get_or_404(id)
    id_estacion = categoria.estacion_id
    
    for criterio in categoria.criterios:
        db.session.delete(criterio)
        
    db.session.delete(categoria)
    db.session.commit()
    flash('Categoría eliminada.', 'success')
    return redirect(url_for('master.estaciones_constructor', id=id_estacion))

@master_bp.route('/criterios/nuevo/<id_categoria>', methods=['POST'])
def criterios_nuevo(id_categoria):
    categoria = Categoria.query.get_or_404(id_categoria)
    id_val = request.form.get('id')
    texto = request.form.get('texto')
    puntos = request.form.get('puntos', type=float, default=1.0)
    tipo = request.form.get('tipo', default='checkbox')
    opciones = request.form.get('opciones', default='') if tipo == 'rango' else None
    
    criterio = Criterio(id=id_val, categoria_id=id_categoria, texto=texto, puntos=puntos, tipo=tipo, opciones=opciones)
    db.session.add(criterio)
    db.session.commit()
    flash('Criterio añadido exitosamente.', 'success')
    return redirect(url_for('master.estaciones_constructor', id=categoria.estacion_id))

@master_bp.route('/criterios/eliminar/<id>', methods=['POST'])
def criterios_eliminar(id):
    criterio = Criterio.query.get_or_404(id)
    id_estacion = criterio.categoria.estacion_id
    db.session.delete(criterio)
    db.session.commit()
    flash('Criterio eliminado.', 'success')
    return redirect(url_for('master.estaciones_constructor', id=id_estacion))

@master_bp.route('/exportar')
def exportar_csv():
    # Placeholder redirect or actual csv export
    flash('Exportación iniciada.', 'info')
    return redirect(url_for('analytics.export_data'))
