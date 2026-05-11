from flask import Blueprint, render_template, request, redirect, flash, url_for, jsonify
from app.models.models import Alumno, Estacion, Categoria, Criterio, Evaluacion, EvaluacionDetalle
from extensions import db
import json
import os
import time
import subprocess

tablet_bp = Blueprint('tablet', __name__, url_prefix='/tablet')

RECORDING_PROCESSES = {}

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
FFMPEG_BIN = os.environ.get('FFMPEG_BIN') or os.path.join(BASE_DIR, 'tools', 'ffmpeg-static', 'ffmpeg')
RECORDING_STREAM_URL = os.environ.get('RECORDING_STREAM_URL', 'rtsp://127.0.0.1:8554/camara1')
MAX_RECORDING_SECONDS = os.environ.get('MAX_RECORDING_SECONDS', '3600')
WARMUP_SECONDS = int(os.environ.get('WARMUP_SECONDS', '5'))

def recording_file_size(path):
    try:
        return os.path.getsize(path)
    except OSError:
        return 0

@tablet_bp.route('/api/record/start/<estacion_id>/<alumno_id>', methods=['POST'])
def start_record(estacion_id, alumno_id):
    key = f"{estacion_id}_{alumno_id}"
    if key in RECORDING_PROCESSES:
        procs = RECORDING_PROCESSES[key]
        proc = procs.get('p1')
        return jsonify({
            "status": "already_recording",
            "bytes_written": recording_file_size(procs.get('path1')),
            "returncode": proc.poll() if proc else None
        })
        
    app_dir = os.path.dirname(os.path.dirname(__file__))
    recordings_dir = os.path.join(app_dir, 'static', 'grabaciones')
    logs_dir = os.path.join(app_dir, 'static', 'grabaciones', 'logs')
    os.makedirs(recordings_dir, exist_ok=True)
    os.makedirs(logs_dir, exist_ok=True)
    
    timestamp = int(time.time())
    file1 = f"A{alumno_id}_E{estacion_id}_C1_{timestamp}.mp4"
    path1 = os.path.join(recordings_dir, file1)
    log1 = os.path.join(logs_dir, f"{os.path.splitext(file1)[0]}.ffmpeg.log")
    
    if not os.path.exists(FFMPEG_BIN):
        return jsonify({"status": "error", "error": "ffmpeg_not_found", "path": FFMPEG_BIN}), 500

    # La salida MP4/HTTP de go2rtc puede contener H.264 corrupto desde Tuya.
    # La ruta más estable encontrada fue tomar el restream RTSP de go2rtc y
    # transcodificar a H.264 limpio. Además descartamos los primeros segundos
    # del stream: Tuya/go2rtc suele necesitar un breve warm-up y esos frames
    # iniciales pueden venir con tearing/artefactos aunque el MP4 decodifique.
    cmd1 = [
        FFMPEG_BIN,
        "-hide_banner",
        "-loglevel", "warning",
        "-y",
        "-rtsp_transport", "tcp",
        "-fflags", "+genpts+discardcorrupt",
        "-err_detect", "ignore_err",
        "-i", RECORDING_STREAM_URL,
        "-t", MAX_RECORDING_SECONDS,
        "-an",
        "-vf", f"select=gte(t\\,{WARMUP_SECONDS}),setpts=PTS-STARTPTS,fps=15,scale=640:-2",
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-tune", "zerolatency",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        path1
    ]
    log_handle = open(log1, 'ab')
    p1 = subprocess.Popen(cmd1, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=log_handle)
    
    RECORDING_PROCESSES[key] = {
        'p1': p1,
        'file1': file1,
        'path1': path1,
        'log1': log1,
        'log_handle': log_handle,
        'started_at': time.time()
    }
    return jsonify({
        "status": "recording_started",
        "method": "ffmpeg_rtsp_transcode",
        "file": file1,
        "stream": "camara1"
    })

@tablet_bp.route('/api/record/status/<estacion_id>/<alumno_id>')
def record_status(estacion_id, alumno_id):
    key = f"{estacion_id}_{alumno_id}"
    procs = RECORDING_PROCESSES.get(key)
    if not procs:
        return jsonify({"status": "not_recording"})
    proc = procs.get('p1')
    return jsonify({
        "status": "recording" if proc and proc.poll() is None else "process_finished",
        "file": procs.get('file1'),
        "bytes_written": recording_file_size(procs.get('path1')),
        "elapsed_seconds": round(time.time() - procs.get('started_at', time.time()), 1),
        "returncode": proc.poll() if proc else None,
        "started_at": procs.get('started_at')
    })

def close_recording_handles(procs):
    handle = procs.get('log_handle')
    if handle:
        try:
            handle.close()
        except Exception:
            pass

@tablet_bp.route('/api/record/stop/<estacion_id>/<alumno_id>', methods=['POST'])
def stop_record(estacion_id, alumno_id):
    key = f"{estacion_id}_{alumno_id}"
    procs = RECORDING_PROCESSES.get(key)
    if not procs:
        return jsonify({"status": "not_recording"})
    proc = procs.get('p1')
    stopped = True
    if proc and proc.poll() is None:
        try:
            proc.communicate(b'q\n', timeout=10)
        except Exception:
            stopped = False
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except Exception:
                proc.kill()
    close_recording_handles(procs)
    del RECORDING_PROCESSES[key]
    return jsonify({
        "status": "recording_stopped" if stopped else "stop_timeout",
        "file": procs.get('file1'),
        "bytes_written": recording_file_size(procs.get('path1')),
        "returncode": proc.poll() if proc else None
    })

@tablet_bp.route('/')
def seleccionar_estacion():
    estaciones = Estacion.query.order_by(Estacion.orden).all()
    return render_template('tablet_index.html', estaciones=estaciones)

@tablet_bp.route('/camera/auto-reload')
def camera_auto_reload():
    return render_template('camera_auto_reload.html')

@tablet_bp.route('/<estacion_id>/seleccionar')
def seleccionar_alumno(estacion_id):
    estacion = Estacion.query.get_or_404(estacion_id)
    alumnos = Alumno.query.all()
    evaluados_ids = { e.alumno_id: True for e in Evaluacion.query.filter_by(estacion_id=estacion_id).all() }
    return render_template('tablet_seleccionar.html', estacion=estacion, alumnos=alumnos, evaluados_ids=evaluados_ids)

@tablet_bp.route('/<estacion_id>/evaluar/<alumno_id>', methods=['GET', 'POST'])
def evaluar(estacion_id, alumno_id):
    estacion = Estacion.query.get_or_404(estacion_id)
    alumno = Alumno.query.get_or_404(alumno_id)
    
    evaluacion = Evaluacion.query.filter_by(estacion_id=estacion_id, alumno_id=alumno_id).first()
    valores_previos = {}
    if evaluacion:
        for det in evaluacion.detalles:
            valores_previos[det.criterio_id] = det.valor_registrado

    if request.method == 'POST':
        if not evaluacion:
            evaluacion = Evaluacion(estacion_id=estacion_id, alumno_id=alumno_id, puntaje_total=0)
            db.session.add(evaluacion)
            db.session.commit() # commit so evaluation gets an ID 
        else:
            EvaluacionDetalle.query.filter_by(evaluacion_id=evaluacion.id).delete()
            
        key = f"{estacion_id}_{alumno_id}"
        if key in RECORDING_PROCESSES:
            procs = RECORDING_PROCESSES[key]
            proc = procs.get('p1')
            if proc and proc.poll() is None:
                try:
                    proc.communicate(b'q\n', timeout=10)
                except Exception:
                    proc.terminate()
            
            evaluacion.video_camara1 = f"grabaciones/{procs['file1']}"
            evaluacion.video_camara2 = None
            close_recording_handles(procs)
            del RECORDING_PROCESSES[key]
            
        puntaje_total = 0.0
        
        for cat in estacion.categorias:
            if cat.tipo == 'seleccion_unica':
                val = request.form.get(f'cat_{cat.id}')
                if val:
                    crit = Criterio.query.get(val)
                    if crit:
                        det = EvaluacionDetalle(evaluacion_id=evaluacion.id, criterio_id=crit.id, valor_registrado='True')
                        db.session.add(det)
                        try:
                            puntaje_total += float(getattr(crit, 'puntos', 0) or 0)
                        except Exception:
                            pass
            else:
                for crit in cat.criterios:
                    val = request.form.get(f'crit_{crit.id}')
                    if val:
                        det = EvaluacionDetalle(evaluacion_id=evaluacion.id, criterio_id=crit.id, valor_registrado=str(val))
                        db.session.add(det)
                        try:
                            # if rango, val is numeric points. If checkbox, we add crit.puntos. Wait, if it's "on" (checkbox), then add puntos
                            if crit.tipo == 'rango':
                                puntaje_total += float(val) 
                            else:
                                puntaje_total += float(getattr(crit, 'puntos', 1.0))
                        except Exception:
                            pass
                        
        evaluacion.puntaje_total = puntaje_total
        db.session.commit()
        return redirect(url_for('tablet.exito', estacion_id=estacion_id))
        
    def parse_opciones(opc_str):
        try:
            return json.loads(opc_str)
        except:
            return [0, 1, 2]
            
    # Traemos la url a los MP4 guardados, si hubiese
    video_c1 = evaluacion.video_camara1 if evaluacion else None
    video_c2 = evaluacion.video_camara2 if evaluacion else None
            
    return render_template('tablet_evaluar.html', estacion=estacion, alumno=alumno, valores_previos=valores_previos, parse_opciones=parse_opciones, video_c1=video_c1, video_c2=video_c2)

@tablet_bp.route('/<estacion_id>/reset/<alumno_id>', methods=['POST'])
def reset_evaluacion(estacion_id, alumno_id):
    evaluacion = Evaluacion.query.filter_by(estacion_id=estacion_id, alumno_id=alumno_id).first()
    if evaluacion:
        db.session.delete(evaluacion)
        db.session.commit()
    flash('Evaluación reiniciada.', 'success')
    return redirect(url_for('tablet.seleccionar_alumno', estacion_id=estacion_id))

@tablet_bp.route('/exito/<estacion_id>', strict_slashes=False)
def exito(estacion_id):
    estacion = Estacion.query.get_or_404(estacion_id)
    return render_template('tablet_exito.html', estacion=estacion)
