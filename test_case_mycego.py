import io
import requests
import zipfile
from PIL import Image

def download_zip_file(folders:str, oauth_token:str) -> dict[str, bytes]:

    url = 'https://cloud-api.yandex.net/v1/disk/public/resources/download'
    headers = {
        'Authorization': f'OAuth {oauth_token}',
    }

    download_contents = {}

    for folder in folders:
        params = {
            'public_key': f'https://disk.yandex.ru/d/V47MEP5hZ3U1kg',
            'path': f'/{folder}',
        }   

        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            response_json = response.json()
            zip_file_response = requests.get(response_json['href'])
            zip_file_response.raise_for_status()
            download_contents[folder] = zip_file_response.content

        else:
            print(f"Ошибка: {response.status_code}")

    return download_contents

def extract_images_from_zip(zip_contents: dict[str, bytes]) -> dict[str, list]:
    results = {}
    for folder, zip_content in zip_contents.items():
        images = []
        with zipfile.ZipFile(io.BytesIO(zip_content)) as zip_file:
            for file_name in zip_file.namelist():
                if file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
                    with zip_file.open(file_name) as file:
                        image = Image.open(io.BytesIO(file.read()))
                        images.append(image)
        results[folder] = images
    return results

def create_tiff(images: list, output_path: str) -> None:

    new_width = 200 #Ширина для изоборожений
    new_height = 220 #Высота для изоборожений
    spacing = 35 #Отступы между изоборожениями
    padding_around = 100 #Общий оступ по кроям
    max_columns = 4 #Кол-во столбцов для изображений

    resized_images = [image.resize((new_width, new_height)) for image in images]

    num_images = len(resized_images)
    num_rows = (num_images + max_columns - 1) // max_columns

    total_width = (new_width + spacing) * min(max_columns, num_images) - spacing
    total_height = (new_height + spacing) * num_rows - spacing

    new_image = Image.new('RGB', (total_width + padding_around * 2, total_height + padding_around * 2), 'white')

    if not images:
        return
    for index, image in enumerate(resized_images):
        row = index // max_columns
        col = index % max_columns
        x_offset = col * (new_width + spacing) + padding_around
        y_offset = row * (new_height + spacing) + padding_around
        new_image.paste(image, (x_offset, y_offset))

    new_image.save(output_path)

def main(folders):

    oauth_token = '' #OAuth-токен для работы с яндекс диском https://yandex.ru/dev/disk-api/doc/ru/reference/public
    zip_content = download_zip_file(folders, oauth_token)
    results = extract_images_from_zip(zip_content)
    for folder, images in results.items():
        create_tiff(images, f"{folder}.tiff")
        print(f"TIFF файл сохранен как {folder}")

if __name__ == "__main__":
    folders = ['1388_12_Наклейки 3-D_3', '1369_12_Наклейки 3-D_3']
    main(folders)