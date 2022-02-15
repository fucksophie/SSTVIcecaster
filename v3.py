import shout, io, configparser, os, random, praw, metovlogs

from PIL import Image
from pysstv import color
from pydub import AudioSegment
from itertools import chain
from array import array
from urllib.request import urlopen

config = configparser.ConfigParser()
log = metovlogs.get_log("sstv and music icecaster")

config.read('config.ini')

icecast = shout.Shout()

musicCount = 0

files = os.listdir("./music/")

reddit = praw.Reddit(
	client_id = config["praw"]["client_id"], 
	client_secret = config["praw"]["client_secret"],
	user_agent = "sstv and music icecaster/3.0.0"
)

posts = []

log.debug("Started fetching subreddit posts..")

posts += list(reddit.subreddit("schizopostingmemes").hot(limit=500))
posts += list(reddit.subreddit("offensivejokes").hot(limit=500))

log.debug("Finished fetching subreddit!!")

def randomPost():
    post = random.choice(posts).url

    while "i.redd.it" not in post and ".gif" not in post:
        post = random.choice(posts).url

    return post

def sendToIcecast(song):
	f = io.BytesIO()

	song.export(f, format="ogg")

	nbuf = f.read(4096)

	log.debug("Started sending bytes to Icecast.")

	while(True):

		buf = nbuf
		nbuf = f.read(4096)

		icecast.send(buf)
		icecast.sync()
		
		if len(buf) == 0:
			log.debug("Finished sending bytes to Icecast.")
			break

	f.close()

def sendSSTV():
	image = Image.open(urlopen(randomPost()))
	image = image.resize((320, 240), Image.ANTIALIAS)

	sstv = color.Robot36(image, 44100, 16)
	sstv.nchannels = 2	

	# generate wav samples
	data = array("h", sstv.gen_samples())
	if sstv.nchannels != 1:
		data = array("h", chain.from_iterable(
			zip(*([data] * sstv.nchannels))))

	# load wav samples into pydub
	song = AudioSegment(
        data=data,
        sample_width=sstv.bits // 8,
        frame_rate=sstv.samples_per_sec,
        channels=sstv.nchannels,
    )

	sendToIcecast(song)

def sendMusic(path):
	seg = AudioSegment.from_file(path)

	sendToIcecast(seg)

icecast.host = config["icecast"]["url"].split(":")[0]
icecast.port = int(config["icecast"]["url"].split(":")[1])
icecast.password = config["icecast"]["password"]
icecast.mount = "/yf-sstv-and-music"
icecast.name = "Yourfriend's SSTV and Music"
icecast.description = "Music, mixed with random SSTV's from time to time. They are .. somewhat rare. Images range from memes to interdimensional connections." 

icecast.open()

while(True):
	if musicCount >= 4:
		sendSSTV()
		log.info("Started playing SSTV!")

		musicCount = 0
	else:
		musicCount+=1
		file = random.choice(files)

		log.info("Started playing audio " + file + ". It is count " + str(musicCount) + "!")

		sendMusic("music/"+random.choice(files))