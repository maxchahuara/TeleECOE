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
FFPROBE_BIN = os.environ.get('FFPROBE_BIN') or os.path.join(BASE_DIR, 'tools', 'ffmpeg-static', 'ffprobe')
RECORDING_STREAM_URL = os.environ.get('RECORDING_STREAM_URL', 'rtsp://127.0.0.1:8554/camara1')
MAX_RECORDING_SECONDS = os.environ.get('MAX_RECORDING_SECONDS', '3600')
WARMUP_SECONDS = int(os.environ.get('WARMUP_SECONDS', '5'))
MIN_VALID_VIDEO_BYTES = int(os.environ.get('MIN_VALID_VIDEO_BYTES', '1024'))
MIN_VALID_VIDEO_DURATION = float(os.environ.get('MIN_VALID_VIDEO_DURATION', '0.5'))

def recording_file_size(path):
    try:
        return os.path.getsize(path)
    except OSError:
        return 0

def append_recording_log(procs, message):
    log_path = procs.get('log1') if procs else None
    if not log_path:
        return
    try:
        with open(log_path, 'ab') as log_file:
            log_file.write((f"\n[TeleECOE] {message}\n").encode('utf-8', errors='replace'))
    except Exception:
        pass

def validate_video_file(path):
    """Valida técnicamente el MP4 antes de asociarlo a una evaluación."""
    result = {
        "valid": False,
        "path": path,
        "bytes": recording_file_size(path),
        "duration": None,
        "errors": []
    }

    if not os.path.exists(path):
        result["errors"].append("file_missing")
        return result
    if result["bytes"] < MIN_VALID_VIDEO_BYTES:
        result["errors"].append("file_too_small")

    if not os.path.exists(FFPROBE_BIN):
        result["errors"].append("ffprobe_not_found")
        return result

    try:
        probe = subprocess.run(
            [
                FFPROBE_BIN,
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                path
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=20
        )
        if probe.returncode != 0:
            result["errors"].append("ffprobe_failed")
            if probe.stderr:
                result["ffprobe_error"] = probe.stderr.strip()[:500]
            return result
        duration_text = (probe.stdout or "").strip()
        result["duration"] = float(duration_text) if duration_text else 0.0
        if result["duration"] < MIN_VALID_VIDEO_DURATION:
            result["errors"].append("duration_too_short")
    except Exception as exc:
        result["errors"].append("ffprobe_exception")
        result["ffprobe_error"] = str(exc)[:500]
        return result

    try:
        decode = subprocess.run(
            [FFMPEG_BIN, "-v", "error", "-i", path, "-f", "null", "-"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=45
        )
        if decode.returncode != 0:
            result["errors"].append("decode_failed")
            if decode.stderr:
                result["decode_error"] = decode.stderr.strip()[:500]
    except Exception as exc:
        result["errors"].append("decode_exception")
        result["decode_error"] = str(exc)[:500]

    result["valid"] = not result["errors"]
    return result

def stop_and_validate_recording(procs):
    """Cierra FFmpeg, valida el MP4 temporal y solo entonces publica el archivo final."""
    proc = procs.get('p1')
    stopped = True
    if proc and proc.poll() is None:
        try:
            proc.communicate(b'q\n', timeout=15)
        except Exception as exc:
            stopped = False
            append_recording_log(procs, f"stop_timeout: {exc}")
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except Exception:
                proc.kill()
                try:
                    proc.wait(timeout=5)
                except Exception:
                    pass

    close_recording_handles(procs)

    temp_path = procs.get('temp_path1')
    final_path = procs.get('path1')
    validation = validate_video_file(temp_path)
    published = False

    if stopped and validation.get('valid'):
        try:
            if os.path.exists(final_path):
                os.remove(final_path)
            os.replace(temp_path, final_path)
            published = True
            validation = validate_video_file(final_path)
            append_recording_log(procs, f"video_validated: {validation}")
        except Exception as exc:
            validation["valid"] = False
            validation.setdefault("errors", []).append("publish_failed")
            validation["publish_error"] = str(exc)[:500]
            append_recording_log(procs, f"publish_failed: {exc}")
    else:
        append_recording_log(procs, f"video_invalid: stopped={stopped} validation={validation}")

    return {
        "stopped": stopped,
        "published": published,
        "file": procs.get('file1'),
        "temp_file": os.path.basename(temp_path) if temp_path else None,
        "bytes_written": recording_file_size(final_path if published else temp_path),
        "returncode": proc.poll() if proc else None,
        "video_valid": bool(published and validation.get('valid')),
        "validation": validation,
        "log": procs.get('log1')
    }

@tablet_bp.route('/api/record/start/<estacion_id>/<alumno_id>', methods=['POST'])
def start_record(estacion_id, alumno_id):
    key = f"{estacion_id}_{alumno_id}"
    if key in RECORDING_PROCESSES:
        procs = RECORDING_PROCESSES[key]
        proc = procs.get('p1')
        return jsonify({
            "status": "already_recording",
            "state": procs.get('state'),
            "bytes_written": recording_file_size(procs.get('temp_path1') or procs.get('path1')),
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
    temp_path1 = os.path.join(recordings_dir, f".{file1}.part.mp4")
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
        "-f", "mp4",
        temp_path1
    ]
    log_handle = open(log1, 'ab')
    p1 = subprocess.Popen(cmd1, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=log_handle)
    
    RECORDING_PROCESSES[key] = {
        'p1': p1,
        'file1': file1,
        'path1': path1,
        'temp_path1': temp_path1,
        'log1': log1,
        'log_handle': log_handle,
        'started_at': time.time(),
        'state': 'recording'
    }
    return jsonify({
        "status": "recording_started",
        "method": "ffmpeg_rtsp_transcode",
        "file": file1,
        "temp_file": os.path.basename(temp_path1),
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
        "state": procs.get('state'),
        "bytes_written": recording_file_size(procs.get('temp_path1') or procs.get('path1')),
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
    procs['state'] = 'stopping'
    result = stop_and_validate_recording(procs)
    del RECORDING_PROCESSES[key]
    return jsonify({
        "status": "recording_stopped" if result["video_valid"] else "video_invalid",
        **result
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
            procs['state'] = 'stopping'
            recording_result = stop_and_validate_recording(procs)

            if recording_result.get('video_valid'):
                evaluacion.video_camara1 = f"grabaciones/{procs['file1']}"
                flash('Video RCP validado y asociado correctamente.', 'success')
            else:
                evaluacion.video_camara1 = None
                flash('La evaluación se guardó, pero el video RCP no fue validado y no se asociará como evidencia.', 'warning')
            evaluacion.video_camara2 = None
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
