from flask import Blueprint, jsonify, render_template, request
from app.models import Alumno, Estacion, Categoria, Criterio, Evaluacion, EvaluacionDetalle
from extensions import db
from sqlalchemy import func
import json

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/')
def dashboard_view():
    """
    Renderiza la vista principal del dashboard analítico.
    """
    estaciones = Estacion.query.order_by(Estacion.orden).all()
    return render_template('analytics_dashboard.html', estaciones=estaciones)


@analytics_bp.route('/api/summary')
def api_summary():
    """
    KPIs globales del sistema.
    """
    total_alumnos = Alumno.query.count()
    total_estaciones = Estacion.query.count()
    total_evaluaciones = Evaluacion.query.count()
    
    # Promedio global
    promedio_global = db.session.query(func.avg(Evaluacion.puntaje_total)).scalar() or 0.0

    return jsonify({
        'total_alumnos': total_alumnos,
        'total_estaciones': total_estaciones,
        'total_evaluaciones': total_evaluaciones,
        'promedio_global': round(promedio_global, 2)
    })

@analytics_bp.route('/api/items')
def api_items():
    """
    Devuelve la matriz de ítems con sus métricas calculadas (Tasa de fallo, acierto, etc).
    Soporta filtrado por ?estacion_id= y ?grupo=
    """
    estacion_filter = request.args.get('estacion_id')
    grupo_filter = request.args.get('grupo')

    query_evaluaciones = Evaluacion.query
    if estacion_filter:
        query_evaluaciones = query_evaluaciones.filter_by(estacion_id=estacion_filter)
    if grupo_filter:
        query_evaluaciones = query_evaluaciones.join(Alumno).filter(Alumno.grupo == int(grupo_filter))
        
    evaluaciones = query_evaluaciones.all()
    eval_ids = [e.id for e in evaluaciones]
    n_total_evaluaciones_base = len(eval_ids)

    # Si no hay evaluaciones que coincidan con los filtros, retornamos vacío temprano
    if n_total_evaluaciones_base == 0:
         return jsonify([])

    # Obtenemos TODOS los criterios de las estaciones filtradas (o todos)
    criterios_query = Criterio.query.join(Categoria).join(Estacion)
    if estacion_filter:
        criterios_query = criterios_query.filter(Estacion.id == estacion_filter)
    
    criterios = criterios_query.all()
    
    # Diccionario en memoria para búsquedas O(1)
    detalles = EvaluacionDetalle.query.filter(EvaluacionDetalle.evaluacion_id.in_(eval_ids)).all()
    detalles_por_criterio = {}
    for d in detalles:
        if d.criterio_id not in detalles_por_criterio:
            detalles_por_criterio[d.criterio_id] = []
        detalles_por_criterio[d.criterio_id].append(d)

    resultados = []

    for c in criterios:
        # Intentos totales por estándar es el número de evaluaciones válidas para ESA estación.
        # Filtramos cuantas evaluaciones de las seleccionadas pertenecen a la estación del criterio
        evals_esta_estacion = [e for e in evaluaciones if e.estacion_id == c.categoria.estacion_id]
        n_intentos = len(evals_esta_estacion)
        
        if n_intentos == 0:
            continue

        aciertos = 0
        fallos = 0
        
        d_list = detalles_por_criterio.get(c.id, [])
        # Para items binarios (checkbox, seleccion_unica)
        if c.tipo != 'rango':
            aciertos = len(d_list)
            fallos = n_intentos - aciertos
        else:
            # Para rangos
            for d in d_list:
                try:
                    valor_num = float(d.valor_registrado)
                    if valor_num > 0.0:
                        aciertos += 1
                    else:
                        fallos += 1
                except:
                    fallos += 1
            # Rellenar los faltantes hipotéticos (aunque rango debería guardar siempre)
            faltantes = n_intentos - len(d_list)
            fallos += faltantes

        acierto_rate = (aciertos / n_intentos) * 100 if n_intentos > 0 else 0
        fallo_rate = (fallos / n_intentos) * 100 if n_intentos > 0 else 0

        resultados.append({
            'criterio_id': c.id,
            'texto': c.texto,
            'categoria': c.categoria.nombre,
            'estacion': c.categoria.estacion.nombre,
            'estacion_id': c.categoria.estacion.id,
            'n_intentos': n_intentos,
            'aciertos': aciertos,
            'fallos': fallos,
            'acierto_rate': round(acierto_rate, 1),
            'fallo_rate': round(fallo_rate, 1)
        })

    # Ordenar por defecto por fallo_rate descendente (los más problemáticos primero)
    resultados = sorted(resultados, key=lambda x: x['fallo_rate'], reverse=True)

    return jsonify(resultados)


@analytics_bp.route('/api/stations')
def api_stations():
    """
    Retorna la distribución de puntajes e información global agrupada por estación.
    """
    estaciones = Estacion.query.order_by(Estacion.orden).all()
    grupo_filter = request.args.get('grupo')

    resultados = []
    
    for est in estaciones:
        query_eval = Evaluacion.query.filter_by(estacion_id=est.id)
        if grupo_filter:
            query_eval = query_eval.join(Alumno).filter(Alumno.grupo == int(grupo_filter))
            
        evals = query_eval.all()
        n_evals = len(evals)

        if n_evals == 0:
            resultados.append({
                'estacion_id': est.id,
                'nombre': est.nombre,
                'orden': est.orden,
                'n_evaluaciones': 0,
                'promedio': 0,
                'maximo': 0,
                'minimo': 0
            })
            continue
            
        puntajes = [e.puntaje_total for e in evals]
        promedio = sum(puntajes) / n_evals
        
        resultados.append({
            'estacion_id': est.id,
            'nombre': est.nombre,
            'orden': est.orden,
            'n_evaluaciones': n_evals,
            'promedio': round(promedio, 2),
            'maximo': round(max(puntajes), 2),
            'minimo': round(min(puntajes), 2)
        })

    return jsonify(resultados)


import csv
import io
from flask import Response

@analytics_bp.route('/export')
def export_csv():
    """
    Descarga reporte en CSV combinado de los ítems y sus métricas de éxito.
    """
    estacion_filter = request.args.get('estacion_id')
    grupo_filter = request.args.get('grupo')

    query_evaluaciones = Evaluacion.query
    if estacion_filter:
        query_evaluaciones = query_evaluaciones.filter_by(estacion_id=estacion_filter)
    if grupo_filter:
        query_evaluaciones = query_evaluaciones.join(Alumno).filter(Alumno.grupo == int(grupo_filter))
        
    evaluaciones = query_evaluaciones.all()
    eval_ids = [e.id for e in evaluaciones]
    n_total_evaluaciones_base = len(eval_ids)

    # Reutilizamos lógica de api_items() simplificada
    criterios_query = Criterio.query.join(Categoria).join(Estacion)
    if estacion_filter:
        criterios_query = criterios_query.filter(Estacion.id == estacion_filter)
    
    criterios = criterios_query.all()
    detalles = EvaluacionDetalle.query.filter(EvaluacionDetalle.evaluacion_id.in_(eval_ids)).all()
    detalles_por_criterio = {}
    for d in detalles:
        if d.criterio_id not in detalles_por_criterio:
            detalles_por_criterio[d.criterio_id] = []
        detalles_por_criterio[d.criterio_id].append(d)

    output = io.StringIO()
    # Emplear separador de coma estándar (,) para Excel en inglés / internacional, o (;) para hispano. 
    # Usaremos CSV estándar (,)
    writer = csv.writer(output, delimiter=',')
    
    # Header
    writer.writerow([
        'Estacion', 'Categoria', 'Criterio_ID', 'Texto', 
        'Intentos Totales', 'Aciertos', 'Fallos', 'Tasa Acierto (%)', 'Tasa Fallo (%)'
    ])

    for c in criterios:
        evals_esta_estacion = [e for e in evaluaciones if e.estacion_id == c.categoria.estacion_id]
        n_intentos = len(evals_esta_estacion)
        
        if n_intentos == 0:
            continue

        aciertos = 0
        fallos = 0
        d_list = detalles_por_criterio.get(c.id, [])
        if c.tipo != 'rango':
            aciertos = len(d_list)
            fallos = n_intentos - aciertos
        else:
            for d in d_list:
                try:
                    valor_num = float(d.valor_registrado)
                    if valor_num > 0.0: aciertos += 1
                    else: fallos += 1
                except:
                    fallos += 1
            fallos += (n_intentos - len(d_list))

        acierto_rate = round((aciertos / n_intentos) * 100, 1) if n_intentos > 0 else 0
        fallo_rate = round((fallos / n_intentos) * 100, 1) if n_intentos > 0 else 0

        writer.writerow([
            c.categoria.estacion.nombre,
            c.categoria.nombre,
            c.id,
            c.texto,
            n_intentos,
            aciertos,
            fallos,
            acierto_rate,
            fallo_rate
        ])

    # Devolver el stream
    output.seek(0)
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=reporte_analitico.csv"}
    )
