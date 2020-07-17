from PIL import Image, ImageDraw, ImageFont
import click
import pandas as pd
from sklearn.cluster import KMeans

from scipy import cluster


def get_hex_color(color):
	return "#%02x%02x%02x" % color


def get_luminosity(pixel):
	return 0.5 * (max(pixel) + min(pixel))


def get_saturation(pixel):
	luminosity = get_luminosity(pixel)
	if luminosity < 1:
		return (max(pixel) - min(pixel)) / (1 - abs(2 * luminosity - 1))
	else:
		return 0


def get_best_pixel(pixels):
	METHOD = "MAX COLOR"

	best_pixel = pixels[0]
	for pixel in pixels:
		if METHOD == "SATURATION":
			if get_saturation(pixel) > get_saturation(best_pixel):
				best_pixel = pixel
		elif METHOD == "MAX COLOR":
			if (max(pixel) - min(pixel)) > (max(best_pixel) - min(best_pixel)):
				best_pixel = pixel

	return best_pixel


def get_centroids(source_file, num_colors, whiten, full):
	pixel_data = list(Image.open(source_file).getdata())

	if not full:
		TARGET_POINTS = 600
		if len(pixel_data) > TARGET_POINTS:
			clump_size = int(len(pixel_data) / TARGET_POINTS)
			small_data = []
			for i in range(0, len(pixel_data), clump_size):
				if i + clump_size < len(pixel_data):
					offset = i + clump_size
				else:
					offset = len(pixel_data) - 1
				clump = pixel_data[i:offset]
				small_data.append(get_best_pixel(clump))
		pixel_data = small_data

	df = pd.DataFrame(pixel_data, columns=["red", "green", "blue"])

	if whiten:
		df["std_red"] = cluster.vq.whiten(df["red"])
		df["std_green"] = cluster.vq.whiten(df["green"])
		df["std_blue"] = cluster.vq.whiten(df["blue"])

	kmeans = KMeans(n_clusters=num_colors)

	if whiten:
		kmeans.fit(df[["std_red", "std_green", "std_blue"]])
	else:
		kmeans.fit(df[["red", "green", "blue"]])

	centroids = kmeans.cluster_centers_
	centroids = list(centroids)

	if whiten:
		centroids = [tuple(i) for i in centroids]
	else:
		centroids = [tuple(map(round, i)) for i in centroids]

	if whiten:
		red_dev, green_dev, blue_dev = df[["red", "green", "blue"]].std()
		for i in range(len(centroids)):
			centroids[i] = round(centroids[i][0] * red_dev), round(centroids[i][1] * green_dev), round(centroids[i][2] * blue_dev)

	return centroids


def get_footer(footer_width, footer_height, centroids, text):
	VERTICAL_PADDING = 0

	footer_img = Image.new("RGB", (footer_width, footer_height), (255, 255, 255))
	tile_width = round(footer_width / (len(centroids) + 0.3) + 0.5)
	spacing = round((footer_width - tile_width * len(centroids)) / (len(centroids) - 1) + tile_width)
	tile_height = footer_height - 2 * VERTICAL_PADDING

	font = ImageFont.truetype("fonts/Roboto-Light.ttf", round(footer_height / 5))

	for i, color in enumerate(centroids):
		x_pos = i * spacing
		y_pos = VERTICAL_PADDING
		tile = Image.new("RGB", (tile_width, tile_height), color)
		footer_img.paste(tile, (x_pos, y_pos))

		if text:
			text_color = round(((sum(color) / len(color)) + 127) % 255)
			draw = ImageDraw.Draw(footer_img)
			draw.text((x_pos + 3, VERTICAL_PADDING), get_hex_color(color), (text_color,) * 3, font=font)

	return footer_img


def make_image(source_file, out_file, centroids, text):
	source_img = Image.open(source_file)
	source_width, source_height = source_img.size
	out_height = round(source_height * 1.25)

	out_img = Image.new("RGB", (source_width, out_height), (255, 255, 255))
	out_img.paste(source_img)

	footer_img = get_footer(source_width, out_height - source_height, centroids, text)

	out_img.paste(footer_img, (0, source_height))

	out_img.save(out_file)


@click.command()
# TODO I would like to put the correct help and other options on these
@click.argument("source_file")
@click.argument("out_file")
@click.argument("num_colors")
@click.option("--text", "-t", default=False, is_flag=True, help="")
@click.option("--whiten", "-w", default=False, is_flag=True, help="")
@click.option("--full", "-f", default=False, is_flag=True, help="")
def main(source_file, out_file, num_colors, text, whiten, full):
	print(f"reading {source_file}...")

	num_colors = int(num_colors)

	centroids = get_centroids(source_file, num_colors, whiten, full)

	make_image(source_file, out_file, centroids, text)

	print(f"made {out_file}")


if __name__ == "__main__":
	main()
