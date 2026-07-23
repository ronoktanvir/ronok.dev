"""Print a mouth open/closed timeline (1 char per 1/25s) for an audio file.

Usage: python tools/mouth_envelope.py <audio-file> [threshold]
Requires macOS afconvert. Paste the printed string into a LINES entry in index.html.
"""

import math
import struct
import subprocess
import sys
import tempfile
import wave

FPS = 25
# fraction of peak RMS that counts as "mouth open"; lower catches quieter speech
THRESHOLD = float(sys.argv[2]) if len(sys.argv) > 2 else 0.18

src = sys.argv[1]
with tempfile.NamedTemporaryFile(suffix=".wav") as tmp:
    subprocess.run(["afconvert", "-f", "WAVE", "-d", "LEI16", src, tmp.name], check=True)
    w = wave.open(tmp.name, "rb")
    rate, nch = w.getframerate(), w.getnchannels()
    raw = w.readframes(w.getnframes())

samples = struct.unpack("<" + "h" * (len(raw) // 2), raw)
if nch > 1:
    samples = [sum(samples[i : i + nch]) / nch for i in range(0, len(samples), nch)]

win = rate // FPS
rms = []
for i in range(len(samples) // win):
    seg = samples[i * win : (i + 1) * win]
    rms.append(math.sqrt(sum(s * s for s in seg) / len(seg)))

peak = max(rms)
out = []
run = 0
for v in rms:
    if v > peak * THRESHOLD:
        run += 1
        out.append("0" if run % 4 == 0 else "1")  # brief closes so it flaps, not gapes
    else:
        run = 0
        out.append("0")

print(f"{len(samples) / rate:.2f}s -> {len(out)} frames")
print("".join(out))
