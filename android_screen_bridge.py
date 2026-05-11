import subprocess
import time
from flask import Flask, Response

app = Flask(__name__)

def capture_png():
    return subprocess.check_output(['adb', 'exec-out', 'screencap', '-p'], timeout=8)

@app.route('/')
def index():
    return '<html><body style="margin:0;background:#000"><img src="/screen.mjpg" style="width:100vw;height:100vh;object-fit:contain;background:#000"></body></html>'

@app.route('/screen.mjpg')
def screen_mjpg():
    def gen():
        while True:
            try:
                frame = capture_png()
                yield (b'--frame\r\nContent-Type: image/png\r\nContent-Length: ' + str(len(frame)).encode() + b'\r\n\r\n' + frame + b'\r\n')
            except Exception as e:
                msg = (f'capture error: {e}').encode()
                yield b'--frame\r\nContent-Type: text/plain\r\n\r\n' + msg + b'\r\n'
                time.sleep(1)
            time.sleep(0.25)
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5090, threaded=True)
