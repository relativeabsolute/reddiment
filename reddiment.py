import argparse
import requests
from textblob import TextBlob
import numpy as np
import matplotlib.pyplot as plt

is_verbose = False

def verbose_print(string):
	if is_verbose:
		print(string)


# Reddit expects this user agent string in all requests, so we make a session object
# that always includes the user-agent string in the request header
session = requests.Session()
session.headers.update({'user-agent': 'linux:reddiment:v1.0 (by /u/relativeabsolute)'})


# return a tuple containing (polarity, subjectivity, score)
def analyze_comment(comment):
	verbose_print("Comment author - {}".format(comment['data']['author']))
	body = comment['data']['body']
	score = comment['data']['score']
	verbose_print("Comment body - {}".format(body))
	verbose_print("Comment score - {}".format(score))
	blob = TextBlob(body)
	sentiment = blob.sentiment
	verbose_print("Comment analysis: polarity = {} and subjectivity = {}".format(sentiment[0], sentiment[1]))
	return (sentiment[0], sentiment[1], score)


# return a list of tuples containing (polarity, subjectivity, score) for each comment on the post
def analyze_post_comments(post_data):
	verbose_print("Post title - {}".format(post_data['title']))
	num_comments = post_data['num_comments']
	verbose_print("Number of comments - {}".format(num_comments))
	permalink = post_data["permalink"]
	verbose_print("Permalink - {}".format(permalink))
	url = "https://www.reddit.com{}.json".format(permalink)
	
	post_response = session.get(url)
	post_response.raise_for_status()
	response_json = post_response.json()
	post_scores = []
	for comment in response_json[1]['data']['children']:
		if comment['kind'] == 't1':
			post_scores.append(analyze_comment(comment))
		else:
			# last item in a comments listing is a 'more' item
			# TODO: figure out how to handle it
			pass
	return post_scores
	

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument('subreddit', help='subreddit to analyze')
	parser.add_argument('--verbose', help='print info as analysis is being performed.', action='store_true')
	args_dict = vars(parser.parse_args())

	is_verbose = args_dict['verbose']

	subreddit = args_dict['subreddit']
	url = 'https://www.reddit.com/r/{}.json'.format(subreddit)
	verbose_print("Collecting posts from {} (url = {})".format(subreddit, url))

	# Request pattern: get request to url, check for error, process response content
	response = session.get(url)
	response.raise_for_status()
	response_json = response.json()
	verbose_print("Number of posts = {}".format(response_json['data']['dist']))
	all_scores = []
	for post in response_json['data']['children']:
		 all_scores.extend(analyze_post_comments(post['data']))
	as_np = np.array(all_scores)
	plt.figure()
	plt.scatter(as_np[:,0], as_np[:,1])
	plt.xlabel('polarity')
	plt.ylabel('subjectivity')
	plt.savefig('polarityvssubjectivity.png')

	plt.figure()
	plt.scatter(as_np[:,0], as_np[:,2])
	plt.xlabel('polarity')
	plt.ylabel('score')
	plt.savefig('polarityvsscore.png')

	plt.figure()
	plt.scatter(as_np[:,1], as_np[:,2])
	plt.xlabel('subjectivity')
	plt.ylabel('score')
	plt.savefig('subjectivityvsscore.png')
