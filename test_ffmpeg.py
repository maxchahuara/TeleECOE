import subprocess
import time

print("Starting ffmpeg test...")
p = subprocess.Popen(
    ["ffmpeg", "-y", "-f", "lavfi", "-i", "testsrc=duration=5:size=1280x720:rate=30", "-c:v", "libx264", "-pix_fmt", "yuv420p", "test_video.mp4"],
    stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
)

time.sleep(2)
print("Sending 'q' to ffmpeg...")
p.communicate(b'q\n', timeout=5)
p.wait()

print("Checking video file size...")
try:
    import os
    print(f"Size: {os.path.getsize('test_video.mp4')} bytes")
except Exception as e:
    print(e)
