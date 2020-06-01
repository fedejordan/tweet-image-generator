from PIL import Image, ImageDraw, ImageFont
import textwrap
import urllib.request
import os
import numpy as np

# Numbers
margin_x = 32
margin_y = 28
final_size = (1200, 606)

# Fonts
font_file = "./fonts/SF-Pro-Display-Medium.otf"
font_bold = "./fonts/SF-Pro-Display-Bold.otf"

#Colors
secondary_text_color = (136, 153, 166);
background_color = (21, 32, 43)

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

def generate_tweet_image(twitter_name, twitter_account, text, date_text, image_url, is_verified, destination):
	drawer, final_image = get_drawer_with_background()

	# Twitter name
	header_font_size = 32
	twitter_name_x = 150
	twitter_name_y = margin_y + 8
	text_font = ImageFont.truetype(font_bold, header_font_size)
	twitter_name_width = text_font.getsize(twitter_name)[0]
	drawer.text((twitter_name_x, twitter_name_y), twitter_name, font=text_font, fill="white")

	# Verified image
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


	# Twitter account
	twitter_account_y = twitter_name_y + 38
	text_font = ImageFont.truetype(font_file, header_font_size)
	drawer.text((150, twitter_account_y), twitter_account, font=text_font, fill=secondary_text_color)

	# Main text
	y_text_position = 151
	x_text_margin = margin_x
	text_lines_spacing = 10
	text_font = ImageFont.truetype(font_file, 46)
	for line in textwrap.wrap(text, width=54):
	    drawer.text((x_text_margin, y_text_position), line, font=text_font, fill="white")
	    y_text_position += text_font.getsize(line)[1] + text_lines_spacing

	# Date
	date_y = y_text_position + 22
	text_font = ImageFont.truetype(font_file, 32)
	drawer.text((30, date_y), date_text, font=text_font, fill=secondary_text_color)

	# Download and insert image
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

	# Crop
	final_height = date_y + 50
	w, h = final_image.size
	final_image = final_image.crop((0, 0, w, final_height))

	# Save file
	final_image.save(destination)

generate_tweet_image(twitter_name, twitter_account, text, date_text, image_url, is_verified, destination)