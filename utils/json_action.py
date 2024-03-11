import json
from config import logger


async def open_json(path):
    data = None
    try:
        with open(path, encoding='utf-8') as file:
            data = json.load(file)
    except Exception as e:
        logger.error(e)
        data = 'Нет'
    finally:
        if not data:
            data = 'Нет'
        return data


async def write_json(lst, filename):
    try:
        with open(f'data/{filename}', 'w', encoding='utf-8') as file:
            json.dump(lst, file, indent=4, ensure_ascii=False)
    except Exception as e:
        logger.error(e)