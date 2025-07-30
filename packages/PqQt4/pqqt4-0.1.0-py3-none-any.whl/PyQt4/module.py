from .texts import TEXTS
import pyperclip

def copy_text(text_id: int = 1) -> bool:
    """Copy selected text to clipboard"""
    try:
        text = TEXTS.get(text_id, TEXTS[1])
        pyperclip.copy(text)

        return True
    except Exception as e:
        print(f"[PqQt4]: {str(e)}")
        return False

def get_all_texts() -> dict:
    """Return all available texts"""
    return TEXTS

def hello() -> str:
    return "."