import shout, io, urllib, PIL, pysstv, itertools, pydub

class Icecast:
	def __init__(self, host, port, password, mount, name, description):
		self.shout = shout.Shout()

		self.shout.host = host
		self.shout.port = port
		self.shout.password = password
		self.shout.mount = mount
		self.shout.name = name
		self.shout.description = description 

		self.shout.open()

	def send(self, song):
		f = io.BytesIO()

		song.export(f, format="ogg")

		nbuf = f.read(4096)

		while(True):
			buf = nbuf
			nbuf = f.read(4096)

			self.shout.send(buf)
			self.shout.sync()
			
			if len(buf) == 0:
				break

		f.close()

	def sendSSTV(self, image):
		image = PIL.Image.open(urllib.request.urlopen(image))
		image = image.resize((320, 240), PIL.Image.ANTIALIAS)

		sstv = pysstv.color.Robot36(image, 44100, 16)
		sstv.nchannels = 2	

		data = itertools.array("h", sstv.gen_samples())

		if sstv.nchannels != 1:
			data = itertools.array("h", itertools.chain.from_iterable(
				zip(*([data] * sstv.nchannels))))

		song = pydub.AudioSegment(
			data=data,
			sample_width=sstv.bits // 8,
			frame_rate=sstv.samples_per_sec,
			channels=sstv.nchannels,
		)

		self.send(song)

	def sendMusic(self, path):
		self.send(pydub.AudioSegment.from_file(path))
