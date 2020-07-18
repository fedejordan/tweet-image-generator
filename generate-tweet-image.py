from PIL import Image, ImageDraw, ImageFont
import textwrap
import urllib.request
import os
import numpy as np
import argparse

# Numbers
margin_x = 32
margin_y = 28
final_size = (1200, 606)
twitter_name_x = 150
twitter_name_y = margin_y + 8


# Fonts
font_file = "./fonts/SF-Pro-Display-Medium.otf"
font_bold = "./fonts/SF-Pro-Display-Bold.otf"
header_font_size = 32

#Colors
first_text_color = "white"
secondary_text_color = (136, 153, 166);
background_color = (21, 32, 43)
links_color = (27, 149, 224)

def get_width_for_text(text: str):
	text_font = ImageFont.truetype(font_file, 46)
	part_canvas = Image.new('RGB', (500, 100))
	part_draw = ImageDraw.Draw(part_canvas)
	part_draw.text((0, 0), text, font=text_font, fill='white')
	part_box = part_canvas.getbbox()
	return part_box[2]

def get_space_width():
	width_text_without_space = get_width_for_text('ab')
	width_text_with_space = get_width_for_text('a b')
	return width_text_with_space - width_text_without_space

space_width = get_space_width()

def generate_white_image(source, destination):
	im = Image.open(source)
	im = im.convert('RGBA')

	data = np.array(im)   # "data" is a height x width x 4 numpy array
	red, green, blue, alpha = data.T # Temporarily unpack the bands for readability

	# Replace white with red... (leaves alpha values alone...)
	black_areas = (red == 0) & (blue == 0) & (green == 0) & (alpha == 255)
	data[..., :-1][black_areas.T] = (255, 255, 255) # Transpose back needed

	im2 = Image.fromarray(data)
	im2.save(destination)

def get_drawer_with_background():
	final_image = Image.new('RGB', final_size, color = background_color)
	return (ImageDraw.Draw(final_image), final_image)

def generate_twitter_name_and_get_width(drawer, twitter_name):
	text_font = ImageFont.truetype(font_bold, header_font_size)
	drawer.text((twitter_name_x, twitter_name_y), twitter_name, font=text_font, fill=first_text_color)
	return text_font.getsize(twitter_name)[0]

def generate_verified_image(final_image, is_verified, twitter_name_width):	
	if is_verified:
		verified_image_x = twitter_name_x + twitter_name_width + 5
		verified_image_y = twitter_name_y
		verified_image_white_file = 'verified-white.png'
		generate_white_image('images/verified.png', verified_image_white_file)
		verified_image = Image.open(verified_image_white_file, 'r')
		verified_image_width = 40
		verified_image = verified_image.resize([verified_image_width, verified_image_width], Image.ANTIALIAS)
		final_image.paste(verified_image, (verified_image_x, verified_image_y), verified_image)
		os.remove('verified-white.png')

def generate_twitter_account(drawer, twitter_account):
	twitter_account_y = twitter_name_y + 38
	text_font = ImageFont.truetype(font_file, header_font_size)
	drawer.text((150, twitter_account_y), twitter_account, font=text_font, fill=secondary_text_color)

def is_valid_url(url):
    import re
    regex = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url is not None and regex.search(url)

def contains_url(text):
	for part in text.split(' '):
		if is_valid_url(part):
			return True
	return False

def generate_main_text_and_get_final_y(drawer, text):
	y_text_position = 151
	x_text_margin = margin_x
	text_lines_spacing = 10
	text_font = ImageFont.truetype(font_file, 46)
	for line in textwrap.wrap(text, width=54):
		if '@' in line or '#' in line or contains_url(line):
			print('Blue text: ' + line)
			string_parts = line.split(' ')
			next_x = 0
			for index, part in enumerate(string_parts):
				if '@' in part or '#' in part or is_valid_url(part):
					color = links_color
				else:
					color = 'white'
				part_width = get_width_for_text(text=part)
				drawer.text((x_text_margin + next_x, y_text_position), part, font=text_font, fill=color)
				next_x += part_width + space_width
		else:
			drawer.text((x_text_margin, y_text_position), line, font=text_font, fill="white")
		y_text_position += text_font.getsize(line)[1] + text_lines_spacing
	return y_text_position

def generate_date_and_get_final_y(drawer, date_text, y_text_position):
	date_y = y_text_position + 22
	text_font = ImageFont.truetype(font_file, 32)
	drawer.text((30, date_y), date_text, font=text_font, fill=secondary_text_color)
	return date_y

def download_and_insert_image(final_image, image_url):
	image_file = 'tweet-image.jpg'
	urllib.request.urlretrieve(image_url, image_file)
	tweet_image = Image.open(image_file, 'r')
	tweet_imageSize = 96
	tweet_image = tweet_image.resize((tweet_imageSize, tweet_imageSize), Image.ANTIALIAS)
	h,w = tweet_image.size
	mask_im = Image.new("L", tweet_image.size, 0)
	mask_draw = ImageDraw.Draw(mask_im)
	mask_draw.ellipse((0, 0, w, h), fill=255)
	final_image.paste(tweet_image, (margin_x, margin_y), mask_im)
	os.remove(image_file)

def crop_final_image(final_image, date_y):
	final_height = date_y + 50
	w, h = final_image.size
	return final_image.crop((0, 0, w, final_height))

def save_image(final_image, destination):
	final_image.save(destination)

def generate_tweet_image(twitter_name, twitter_account, text, date_text, image_url, is_verified, destination):
	drawer, final_image = get_drawer_with_background()
	twitter_name_width = generate_twitter_name_and_get_width(drawer, twitter_name)
	generate_verified_image(final_image, is_verified, twitter_name_width)
	generate_twitter_account(drawer, twitter_account)
	y_text_position = generate_main_text_and_get_final_y(drawer, text)

	date_y = generate_date_and_get_final_y(drawer, date_text, y_text_position)
	download_and_insert_image(final_image, image_url)
	final_image = crop_final_image(final_image, date_y)
	save_image(final_image, destination)

def capture_args():
	parser = argparse.ArgumentParser(description='Generates a tweeet image based on parameters')
	parser.add_argument('--twitter-name', dest='twitter_name', type=str, 
	                   help='Name of account (title)', required=True)
	parser.add_argument('--twitter-account', dest='twitter_account', type=str, 
	                   help='Account (username on twitter)', required=True)
	parser.add_argument('--text', dest='text', type=str, 
	                   help='Tweet text', required=True)
	parser.add_argument('--date-text', dest='date_text', type=str, 
	                   help='Date in text format, for instance: "6:09 p.m. · 30 may. 2020"', required=True)
	parser.add_argument('--image-url', dest='image_url', type=str, 
	                   help='URL of twitter image', required=True)
	parser.add_argument('--is-verified', dest='is_verified', type=str, 
	                   help='Boolean value, tells if image should show verified icon', required=True)
	parser.add_argument('--destination', dest='destination', type=str, default='generated-image.png',
	                   help='output file to export list (default generated-image.png)')
	return parser.parse_args()

# args = capture_args()
# print(args)
class ArgsClass:
	twitter_name = "Alberto Fernández"
	twitter_account = "alferdez"
	text = 'Anabel Fernández Sagasti (@anabelfsagasti),senadora por Mendoza, en #HabraConsecuencias @eldestape_radio: "Ayer varios de la oposición hicieron comentarios sobre Vicentin con liviandad y el @alferdez ratificó que la expropiación es un instrumento para que la empresa no colapse'
	image_url = "https://pbs.twimg.com/profile_images/1192149786503327744/l232oveZ_bigger.jpg"
	date_text = "7:03 p. m. · 15 jul. 2020"
	is_verified = True
	destination = 'generated-image.png'
args = ArgsClass()
generate_tweet_image(args.twitter_name, args.twitter_account, args.text, args.date_text, args.image_url, args.is_verified, args.destination)