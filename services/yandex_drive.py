import requests
from config_data.config import Config, load_config


config: Config = load_config()
TOKEN = config.tg_bot.yatoken
HEADERS = {"Authorization": f"OAuth {TOKEN}"}


async def get_list_folders_to_path(path="disk:/") -> list[str]:
    """
    Выводит список файлов и папок по заданному пути на Яндекс.Диске
    :param path:
    :return:
    """
    url = "https://cloud-api.yandex.net/v1/disk/resources"
    params = {"path": path, "limit": 100}
    list_folder = []  # Массив для хранения результатов
    response = requests.get(url, headers=HEADERS, params=params)
    if response.status_code == 200:
        items = response.json().get("_embedded", {}).get("items", [])
        print(items)
        for item in items:
            if item['type'] == 'dir':
                list_folder.append(item['name'])
        return list_folder
    else:
        error_msg = f"❌ Ошибка: {response.text}"
        print(error_msg)


async def get_list_file_to_path(path="disk:/") -> list[str]:
    """
    Выводит список файлов и папок по заданному пути на Яндекс.Диске
    :param path:
    :return:
    """
    url = "https://cloud-api.yandex.net/v1/disk/resources"
    params = {"path": path, "limit": 100}
    list_folder = []  # Массив для хранения результатов
    response = requests.get(url, headers=HEADERS, params=params)
    if response.status_code == 200:
        items = response.json().get("_embedded", {}).get("items", [])
        print(items)
        for item in items:
            if item['type'] == 'file':
                list_folder.append(item['name'])
        return list_folder
    else:
        error_msg = f"❌ Ошибка: {response.text}"
        print(error_msg)


async def get_download_link(file_path):
    """Получает временную ссылку на скачивание файла"""
    url = "https://cloud-api.yandex.net/v1/disk/resources/download"
    params = {"path": file_path}

    response = requests.get(url, headers=HEADERS, params=params)
    if response.status_code == 200:
        result = f"📄 Ссылка для скачивания: {response.json()['href']}"
        return result
    else:
        error_msg = f"❌ Ошибка: {response.text}"
        print(error_msg)


async def get_photo_view_link(file_path: str) -> str:
    """Получает ссылку на просмотр фото в Яндекс.Диске."""
    url = "https://cloud-api.yandex.net/v1/disk/resources"
    params = {"path": file_path}

    response = requests.get(url, headers=HEADERS, params=params)
    if response.status_code == 200:
        public_url = response.json().get("public_url")
        if public_url:
            return public_url  # Ссылка на просмотр фото
        else:
            print("❌ Файл не опубликован, создаём публичную ссылку...")
            return await publish_photo(file_path)
    else:
        print("❌ Ошибка:", response.text)
        return None


async def publish_photo(file_path: str) -> str:
    """Делает фото публичным и возвращает ссылку на просмотр."""
    url = "https://cloud-api.yandex.net/v1/disk/resources/publish"
    params = {"path": file_path}

    response = requests.put(url, headers=HEADERS, params=params)
    if response.status_code == 202:
        return await get_photo_view_link(file_path)  # Получаем ссылку после публикации
    else:
        print("❌ Ошибка публикации:", response.text)
        return None
