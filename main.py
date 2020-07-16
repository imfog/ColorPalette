from PIL import Image
import click
import pandas as pd
import sklearn as sk


def make_image(source_file, out_file, num_colors, add_text):
	test = list(Image.open(source_file).getdata())


@click.command()
@click.argument("source_file")
@click.argument("out_file")
@click.argument("num_colors")
@click.option("--text", "-t", default=False, is_flag=True, help="")
def main(source_file, out_file, num_colors, text):
	make_image(source_file, out_file, int(num_colors), text)


if __name__ == "__main__":
	main()
