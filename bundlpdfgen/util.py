from PIL import Image, ImageOps
import glob

def remove_exif():
    print('Preparing images for PDF')
    for file in glob.glob('images/*'):
        image = Image.open(file)
        image = ImageOps.exif_transpose(image)
        image.save(file)