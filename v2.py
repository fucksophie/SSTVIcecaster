import pysstv, shout, PIL, soundfile
icecast = shout.Shout()
sstv = pysstv.color.Robot36(PIL.Image.open("267-320x240.jpg"), 48000, 16)
sstv.write_wav("temp.wav")
data, samplerate = soundfile.read('temp.wav')
soundfile.write('temp.ogg', data, samplerate)
icecast.host = ""
icecast.port = 0
icecast.password = ""
icecast.mount = "/yf-testing"
def load(path):
	f = open(path, "rb")
	nbuf = f.read(4096)
	while(True):
		buf = nbuf
		nbuf = f.read(4096)
		if len(buf) == 0:
			print('finished')
			load("temp.ogg")
			break
		icecast.send(buf)
		icecast.sync()
	f.close()
icecast.open()
load("temp.ogg")