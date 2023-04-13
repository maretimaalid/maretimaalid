import json
import openpyxl
from openpyxl_image_loader import SheetImageLoader
from PIL import Image
import hashlib

img_base_width = 1500


def write_image_to_file(image, file_name):
    wpercent = (img_base_width / float(image.size[0]))
    hsize = int((float(image.size[1]) * float(wpercent)))
    image = image.resize((img_base_width, hsize), Image.LANCZOS)
    image.save(file_name)


def get_image_sha1(image):
    sha1 = hashlib.sha1()
    sha1.update(image.tobytes())
    return sha1.hexdigest()


def main():
    data = openpyxl.load_workbook('export.xlsx')
    sheet = data['Sheet1']

    keys = None
    image_loader = SheetImageLoader(sheet)

    paintings_data = []
    for row in sheet:
        if not keys:
            keys = [cell.value for cell in row]
            continue

        painting_data = {}
        for key, cell in zip(keys, row):
            value = cell.value
            if image_loader.image_in(cell.coordinate):
                image = image_loader.get(cell.coordinate)
                file_name = f'{get_image_sha1(image)}.jpg'
                write_image_to_file(image, f'dist/img/{file_name}')
                value = file_name
            painting_data[key] = value
        paintings_data.append(painting_data)
    data = {'paintings': paintings_data}
    with open('data.json', 'w') as f:
        json.dump(data, f)


if __name__ == '__main__':
    main()