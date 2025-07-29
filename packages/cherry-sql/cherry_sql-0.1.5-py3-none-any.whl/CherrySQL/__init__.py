# Пакет CherrySQL

import importlib.resources as pkg_resources
import shutil
import os

def _copy_tree(src, dst):
    os.makedirs(dst, exist_ok=True)
    for item in src.iterdir():
        if item.is_file():
            shutil.copy(item, os.path.join(dst, item.name))
        elif item.is_dir():
            _copy_tree(item, os.path.join(dst, item.name))

def cherry(target_dir=None):
    """
    Копирует все папки и файлы из пакета CherrySQL в папку target_dir.
    Если target_dir не указан, копирует в текущую рабочую директорию пользователя.
    Пример использования:
        import CherrySQL
        CherrySQL.cherry()
    """
    import CherrySQL
    if target_dir is None:
        target_dir = os.getcwd()
    # Копируем все папки и файлы верхнего уровня из CherrySQL
    for item in pkg_resources.files(CherrySQL).iterdir():
        dst_path = os.path.join(target_dir, item.name)
        if item.is_file():
            shutil.copy(item, dst_path)
        elif item.is_dir():
            _copy_tree(item, dst_path)
