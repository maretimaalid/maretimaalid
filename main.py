import json
import openpyxl
from openpyxl_image_loader import SheetImageLoader
from PIL import Image
import hashlib

img_base_width_medium = 1200
img_base_width_low = 600


class ImageDto:
    file_path: str
    file_name: str
    file_extension: str
    width: int
    height: int
    image: Image

    def __init__(self, file_path, file_name, file_extension, width, image):
        self.file_path = file_path
        self.file_name = file_name
        self.file_extension = file_extension
        self.width = width
        self.image = image
        self.height = int((float(self.image.height) * float(width / float(self.image.width))))

    def as_dict(self):
        return {"width": self.width, "height": self.height, "full_file_path": self.full_file_path}

    @property
    def full_file_path(self):
        return f"{self.file_path}/{self.file_name}.{self.file_extension}"

    def get_internal_full_file_path(self):
        return f"dist/{self.full_file_path}"

    def get_resized_image(self):
        return self.image.resize((self.width, self.height), Image.LANCZOS)

    def save_image(self, **kwargs):
        image = self.image.resize((self.width, self.height), Image.LANCZOS)
        image.save(self.get_internal_full_file_path(), self.file_extension, **kwargs)


def write_image_to_file(image):
    name = get_image_sha1(image)

    high = ImageDto("img", name, image.format, image.width, image)
    medium = ImageDto("img/medium", name, "webp", img_base_width_medium, image)
    low = ImageDto("img/low", name, "webp", img_base_width_low, image)

    high.save_image(optimize=False)
    medium.save_image(optimize=False)
    low.save_image(optimize=True, quality=60)

    return low, medium, high


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
                image: Image = image_loader.get(cell.coordinate)
                low, medium, high = write_image_to_file(image)
                value = {"low": low.as_dict(), "medium": medium.as_dict(), "high": high.as_dict()}
            painting_data[key] = value
        # If one of the first 3 keys('title','description','file_data') value is empty then skip the whole row
        if any(painting_data[key] is None for key in keys[:3]):
            print(f"WARNING! skipped row with data: {json.dumps(painting_data)}")
            continue
        paintings_data.append(painting_data)
    data = {'paintings': paintings_data}
    print(json.dumps(data))
    with open('data.json', 'w') as f:
        json.dump(data, f)


if __name__ == '__main__':
    main()
