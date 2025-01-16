import json
from bs4 import BeautifulSoup
import base64

image_refs = ['427', '431','442', '4442' ,'5101','55423', '56331','602', '61203','6241', '636111']
images = {}

def get_image_bytes(file_path):
	try:
		with open(file_path, "rb") as f:
			image_bytes = f.read()
		return image_bytes
	except FileNotFoundError:
		raise FileNotFoundError(f"File not found: {file_path}")
	except IOError as e:
		raise IOError(f"An error occurred while reading the file: {e}")

def format_text(soup):
	for span in soup.find_all('span', class_='overlined'):
		# Extract the text inside the <var> tag
		var_tag = span.find('var', class_='pushvar')
		if var_tag and var_tag.string:
			# Add overline
			var_tag.string = ''.join(char + '\u0305' for char in var_tag.string)

	#find <em> tags and replace with italicized text
	for em in soup.find_all('em'):
		em.replace_with(f"_{em.get_text()}_")

	# find p block and add space after each p block
	for p in soup.find_all('p'):
		p.insert_after(" ")
	return soup

def handle_images(s, num):
	num = num.replace(".", "")
	if num not in image_refs:
		return s,[]

	image_files =[]
	image_data = []

	# svg cases
	svg_tags = s.find_all('svg')
	total_svg = len(svg_tags)

	for i, svg_tag in enumerate(svg_tags):
		if total_svg == 1:
			svg_placeholder = f"[IMAGE-{num}] "
			image_files.append(f'{num}.png')
		else:
			svg_placeholder = f"[IMAGE-{num}-{chr(97 + i)}] "
			image_files.append(f'{num}-{chr(97 + i)}.png')

		svg_tag.replace_with(svg_placeholder)
	# table cases
	table_tags = s.find_all('table')

	for table_tag in table_tags:
		if 'possibilities' in table_tag['class']:
			if num == '427':
				table_placeholder = f"[IMAGE-427] "
				image_files.append('427.png')
				table_tag.replace_with("[Kn = sum from nu = 0 to n of (n choose nu)] " + table_placeholder)
				break
			elif num == '442':
				table_placeholder = f"[IMAGE-442] "
				image_files.append('442.png')
				table_tag.replace_with("[sum from kappa = 0 to Kn of (Kn choose kappa) = Ln]" + table_placeholder)
				break
		elif 'truthtable' in table_tag['class']:
			table_placeholder = f"[IMAGE-431] "
			image_files.append('431.png')
			table_tag.replace_with(table_placeholder)
			break
		elif 'fnlist' in table_tag['class']:
			table_placeholder = f"[IMAGE-5101] "
			image_files.append('5101.png')
			table_tag.replace_with(table_placeholder)
			break
		elif 'alignedmath' in table_tag['class']:
			table_placeholder = f"[IMAGE-602] "
			image_files.append('602.png')
			table_tag.replace_with(table_placeholder)
			break

	# div cases
	div_tags = s.find_all('div')

	for div_tag in div_tags:
		if num == '6241':
			div_placeholder = f"[IMAGE-6241] "
			image_files.append('6241.png')
			div_tag.replace_with(div_placeholder)
			break
		elif 'centeredsqueeze' in div_tag['class']:
			div_placeholder = f"[IMAGE-636111] "
			image_files.append('636111.png')
			div_tag.replace_with(div_placeholder)
			break

	# special case (4442 missing from original json)
	if num == '4442':
		image_files.append('4442.png')

	for file in image_files:
		image_bytes = get_image_bytes(f"images/{file}")
		# image_data.append(image_bytes)
		img_base64 = base64.b64encode(image_bytes).decode('utf-8')  # Convert bytes to string

		# Store Base64-encoded image data
		image_data.append(img_base64)
	return s, image_data

def clean_text(text):
	cleaned = text.replace("\n", " ").replace("\xa0", " ")
	return cleaned.strip()

def split_text_into_chunks(cleaned_text, max_length=285):
	delimiters = [". ", "! ", "? ", ".)", "; ", ": ", ", "]
	chunks = []
	while len(cleaned_text) > max_length:
		split_index = -1
		for delimiter in delimiters:
			split_index = cleaned_text[:max_length].rfind(delimiter)
			if split_index != -1:
				break
		if split_index == -1:
			print("No sentence boundary found, splitting at max length")
			split_index = max_length
		else:
			split_index += 2

		chunks.append(cleaned_text[:split_index].strip())
		cleaned_text = cleaned_text[split_index:].strip()

	# Add any remaining text
	if cleaned_text:
		chunks.append(cleaned_text)

	return chunks


def process_children(children):
	result = []

	for child in children:
		num = child['key']

		text = child['content']['en'] if child.get('content') else ''
		soup = BeautifulSoup(text, "html.parser")

		# handle text formatting
		soup = format_text(soup)

		# handle images
		soup,image_data = handle_images(soup, num)

		extracted_text = soup.get_text()
		cleaned_text = clean_text(extracted_text)

		if len(cleaned_text) > 290:
			chunks = split_text_into_chunks(cleaned_text)

			for i, chunk in enumerate(chunks, start=1):
				prop = {
					"num": f"{num}"+ f" ({i}/{len(chunks)})",
					"text": chunk,
					# "images": image_data
				}
				images[num] = image_data

				# put children on last chunk
				if i == len(chunks):
					if 'children' in child:
						prop['children'] = process_children(child['children'])

				# result.append(prop)
				result.append(prop)
		else:
			# Store the current child's processed information
			prop = {
				"num": num,
				"text": cleaned_text,
			}
			images[num] = image_data

			# If there are nested children, process them recursively
			if 'children' in child:
				prop['children'] = process_children(child['children'])

			# Add the current child with nested children (if any) to the result
			result.append(prop)
	return result

if __name__ == '__main__':

	with open('tractatus.json') as f:
		raw_tract = json.load(f)

	raw_tract['children'].pop(0) #remove the preface

	processed_tract = process_children(raw_tract['children'])
	images = {k : v for k,v in images.items() if v}

	with open('processed_tractatus.json', 'w') as f:
		json.dump(processed_tract, f, indent=4)
		print("Data written to processed_tractatus.json")
	with open('images.json', 'w') as f:
		json.dump(images, f, indent=4)
		print("Images written to images.json")
