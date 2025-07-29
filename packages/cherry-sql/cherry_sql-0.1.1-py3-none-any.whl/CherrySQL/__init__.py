# Пакет CherrySQL

import importlib.resources as pkg_resources
import shutil
import os

def cherry(target_dir=None):
    """
    Копирует все файлы из пакета CherrySQL в папку target_dir.
    Если target_dir не указан, копирует в текущую рабочую директорию пользователя.
    Пример использования:
        import CherrySQL
        CherrySQL.cherry()
    """
    import CherrySQL
    if target_dir is None:
        target_dir = os.getcwd()
    os.makedirs(target_dir, exist_ok=True)
    for file in pkg_resources.files(CherrySQL).iterdir():
        if file.is_file():
            shutil.copy(file, os.path.join(target_dir, file.name))
