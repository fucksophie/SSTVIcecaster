import icecast, reddit, configparser, random, os

config = configparser.ConfigParser()
config.read("./config.ini")

amountOfMusicPlayed = 0

reddit = reddit.Reddit(
	config["praw"]["client_id"], 
	config["praw"]["client_secret"],
	"sstv and music icecaster/3.0.0",
	["schizopostingmemes", "offensivejokes"]
)

shout = icecast.Icecast(
    config["icecast"]["url"].split(":")[0],
    int(config["icecast"]["url"].split(":")[1]),
    config["icecast"]["password"],
    "/yf-sstv-and-music",
    "Yourfriend's SSTV and Music",
    "Music, mixed with random SSTV's from time to time. They are .. somewhat rare. Images range from memes to interdimensional connections.",
)

while(True):
	if amountOfMusicPlayed >= 4:
		print("Sending SSTV.")
		
		shout.sendSSTV(reddit.randomPost())

		amountOfMusicPlayed = 0
	else:
		amountOfMusicPlayed += 1
		file = random.choice(os.listdir("./music/"))

		print("Started playing audio " + file + ". It is count " + str(amountOfMusicPlayed) + "!")

		shout.sendMusic("./music/"+file)