import pyperclip

clipboard_content = pyperclip.paste()

if clipboard_content:
    print("Clipboard content: \n", clipboard_content)