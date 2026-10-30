import sys, soundfile as sf
from kokoro_onnx import Kokoro
k = Kokoro("models/kokoro-v1.0.onnx", "models/voices-v1.0.bin")
text = open(sys.argv[1]).read()
s, sr = k.create(text, voice=sys.argv[3] if len(sys.argv)>3 else "am_michael", speed=1.0, lang="en-us")
sf.write(sys.argv[2], s, sr); print("seconds:", round(len(s)/sr,1))
