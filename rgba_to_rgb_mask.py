from PIL import Image
import argparse
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--input_file', required=True, type=str, help='input rgba image')
parser.add_argument('--output_dir', required=True, type=str, help='output directory')
args = parser.parse_args()

rgba = Image.open(args.input_file)
mask = rgba.split()[-1]
bg = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
new_rgb = Image.alpha_composite(bg, rgba).convert('RGB')

new_rgb.save(str(Path(args.output_dir) / 'image.png'))
mask.save(str(Path(args.output_dir) / 'image_mask.png'))