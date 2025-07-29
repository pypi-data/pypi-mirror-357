import subprocess

def get_clipboard_text():
    try:
        return subprocess.check_output('pbpaste', text=True)
    except subprocess.CalledProcessError:
        return ""

def set_clipboard_text(text):
    try:
        process = subprocess.Popen('pbcopy', stdin=subprocess.PIPE, text=True)
        process.communicate(text)
    except Exception as e:
        print(f"Failed to set clipboard: {e}")

# Example usage:
if __name__ == "__main__":
    current_clipboard = get_clipboard_text()
    print("Clipboard contains:", current_clipboard)

    set_clipboard_text("Hello from appletalk!")
    print("Clipboard updated.")
