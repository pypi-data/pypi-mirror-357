import pyperclip

DEFAULT_TEXT = "Установлен пакет faneranew! ✨"

def copy_to_clipboard(text: str) -> bool:
    try:
        pyperclip.copy(text)
        print(f"[faneranew] Скопировано: '{text}'")
        return True
    except Exception as e:
        print(f"[faneranew] Ошибка: {str(e)}")
        return False

def hello() -> str:
    return "Hello from faneranew!"