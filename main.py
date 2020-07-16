from PIL import Image, ImageDraw, ImageFont
import click
import pandas as pd
from sklearn.cluster import KMeans


def get_hex_color(color):
	return "#%02x%02x%02x" % color


def get_centroids(source_file, num_colors):
	pixel_data = list(Image.open(source_file).getdata())
	df = pd.DataFrame(pixel_data, columns=["red", "green", "blue"])
	kmeans = KMeans(n_clusters=num_colors)
	kmeans.fit(df)
	centroids = kmeans.cluster_centers_
	centroids = list(centroids)
	centroids = [tuple(map(round, i)) for i in centroids]

	return centroids


def get_footer(footer_width, footer_height, centroids, text):
	VERTICAL_PADDING = 3

	footer_img = Image.new("RGB", (footer_width, footer_height), (255, 255, 255))
	tile_width = round(footer_width / (len(centroids) + 0.3))
	tile_height = footer_height - 2 * VERTICAL_PADDING

	font = ImageFont.truetype("fonts/Roboto-Light.ttf", round(footer_height / 5))

	for i, color in enumerate(centroids):
		x_pos = round(i * (tile_width + (0.5 * tile_width) / (len(centroids) - 1)))
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
@click.argument("source_file")
@click.argument("out_file")
@click.argument("num_colors")
@click.option("--text", "-t", default=False, is_flag=True, help="")
def main(source_file, out_file, num_colors, text):
	num_colors = int(num_colors)

	centroids = get_centroids(source_file, num_colors)

	make_image(source_file, out_file, centroids, text)


if __name__ == "__main__":
	main()
