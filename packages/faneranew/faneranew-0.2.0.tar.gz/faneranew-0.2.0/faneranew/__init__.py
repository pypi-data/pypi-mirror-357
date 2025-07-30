from .module import copy_text, get_all_texts, hello

# Автоматически копирует текст #1 при импорте
copy_text(1)

__version__ = "0.2.0"  # Обновили версию!
__all__ = ['copy_text', 'get_all_texts', 'hello']