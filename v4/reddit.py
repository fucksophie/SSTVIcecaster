import praw, random, os

class Reddit:
	def __init__(self, client_id, client_secret, user_agent, subreddits):
		self.praw = praw.Reddit(
			client_id = client_id, 
			client_secret = client_secret,
			user_agent = user_agent
		)

		self.posts = []

		for subreddit in subreddits:
			if os.path.exists(subreddit + ".txt"):
				print("[REDDIT] Cache exists for " + subreddit + "!")
				self.posts += map(lambda e: e.strip(), list(open(subreddit + ".txt", 'r')))
			else:
				print("[REDDIT] 500 hottest posts from " + subreddit + " loading..")

				posts = map(lambda b: b.url, filter(lambda s: "i.redd.it" in s.url and ".gif" not in s.url, list(self.praw.subreddit(subreddit).hot(limit=1000))))

				subbreditFile = open(subreddit + ".txt", "w")

				for element in posts:
					subbreditFile.write(element + "\n")
				
				subbreditFile.close()
				
				self.posts += posts
				print("[REDDIT] 500 hottest posts from " + subreddit + " LOADED!!!")
	
	def randomPost(self):
		return random.choice(self.posts)
