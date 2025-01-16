import base64
import json
import os
import time

def get_bsky_client():
	try:
		from config import password, login
	except ImportError:
		login = os.getenv('login')
		password = os.getenv('password')
	try:
		client = Client()
		client.login(login, password)
		print("Logged in successfully.")
	except Exception as e:
		print(f"An error occurred while logging in: {e}")
	return client

def read_data():
	try:
		with open('processed_tractatus.json') as f:
			data = json.load(f)
	except Exception as e:
		print(f"An error occurred while reading the processed tractatus: {e}")
		return 0,0
	try:
		with open('images.json') as f:
			img_data = json.load(f)
	except Exception as e:
		print(f"An error occurred while reading the images: {e}")
		return 0,0
	return data, img_data

def format_num(num):
	nums = num.split('.')
	#first num dot the rest of nums
	if len(nums) == 1:
		num = nums[0]
	else:
		num = nums[0] + '.' + ''.join(nums[1:])
	return num

def prepare_images(prop, num, img_data):
	# 	#cases with multiple images
	if num == "6.1203 (2/5)":
		images = img_data.get('6.1.2.0.3')[:2]
		# base64 decode the images
		images = [base64.b64decode(img) for img in images]
		print("images", len(images))

	elif num == "6.1203 (4/5)":
		images = img_data.get('6.1.2.0.3')[2:]
		# base64 decode the images
		images = [base64.b64decode(img) for img in images]
		print("images", len(images))
	else:
		pure_num = prop['num'].split(' ')[0]
		img = img_data.get(pure_num)[0]
		# base64 decode the images
		images = [base64.b64decode(img)]
		print("images", len(images))
	return images

if __name__ == '__main__':
	from atproto import Client
	from atproto import models

	client = get_bsky_client()
	data, img_data = read_data()

	def post_nested(data, depth=0, parent=None, root=None):
		if depth > 100:
			print("Max depth reached, stopping recursion.")
			return

		for prop in data:
			num = format_num(prop['num'])
			clause = f"{num} {prop['text']}"

			if len(clause)>300:
				print("WARNING: Text is longer than 300 characters:", clause)
				clause = clause[:300]

			try:
				if depth == 0:  # root posts
					res = client.send_post(text=clause)
					root = models.create_strong_ref(res)
					parent = models.create_strong_ref(res)
				else:
					#cases with images
					if "IMAGE-" in clause:
						images = prepare_images(prop, num, img_data)
						client.send_images(
							text=clause,
							images=images,
							reply_to=models.AppBskyFeedPost.ReplyRef(parent=parent, root=root)
						)
						parent = models.create_strong_ref(res)
					#cases without images
					else:
						res = client.send_post(
							text=clause,
							reply_to=models.AppBskyFeedPost.ReplyRef(parent=parent, root=root)
						)
						parent = models.create_strong_ref(res)
			except Exception as e:
				print(f"Error posting: {e}")
				continue

			if 'children' in prop and prop['children']:
				#add a pause between posts
				print("Sleeping for 10 seconds...") #to avoid rate limiting and allow images to post
				time.sleep(10)
				post_nested(prop['children'], depth+1, parent, root)

	post_nested(data)
	print("All posts have been sent.")
	print("Wovon man nicht sprechen kann, darüber muss man schweigen")
	# Wovon man nicht sprechen kann, darüber muss man schweigen
