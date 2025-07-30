from .texts import TEXTS
import pyperclip

def copy_text(text_id: int = 1) -> bool:
    """Копирует выбранный текст в буфер обмена"""
    try:
        text = TEXTS.get(text_id, TEXTS[1])
        pyperclip.copy(text)
        print(f"[faneranew] Скопирован текст #{text_id}: '{text}'")
        return True
    except Exception as e:
        print(f"[faneranew] Ошибка: {str(e)}")
        return False

def get_all_texts() -> dict:
    """Возвращает все доступные тексты"""
    return TEXTS

def hello() -> str:
    return "Добро пожаловать в faneranew!"