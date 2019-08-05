import argparse
import requests

def analyze_post_comments(post_data):
	print("Post title - {}".format(post_data['title']))
	print("Number of comments - {}".format(post_data['num_comments']))

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument('subreddit', help='subreddit to analyze')
	args_dict = vars(parser.parse_args())

	subreddit = args_dict['subreddit']
	url = 'https://www.reddit.com/r/{}.json'.format(subreddit)
	print("Collecting posts from {} (url = {})".format(subreddit, url))

	headers = {'user-agent': 'linux:reddiment:v1.0 (by /u/relativeabsolute)'}
	response = requests.get(url, headers=headers)
	if response.status_code == requests.codes.ok:
		response_json = response.json()
		print("Number of posts = {}".format(response_json['data']['dist']))
		for post in response_json['data']['children']:
			analyze_post_comments(post['data'])
	else:
		response.raise_for_status()
