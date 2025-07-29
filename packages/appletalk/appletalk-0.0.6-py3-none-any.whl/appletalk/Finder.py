
try:
    from . import init
except:
    import init
import os
FILEUTIS = {
    # Images
    "PNGS": "public.png",
    "JPEG": "public.jpeg",
    "GIF": "com.compuserve.gif",
    "TIFF": "public.tiff",
    "BMP": "com.microsoft.bmp",
    "IMAGE": "public.image",
    
    # Audio
    "AUDIO": "public.audio",
    "MP3": "public.mp3",
    "M4P": "com.apple.protected-mpeg-4-audio",
    "M4A": "com.apple.m4a-audio",
    "WAV": "com.microsoft.waveform-audio",
    "AIFF": "public.aiff-audio",
    
    # Video
    "VIDEO": "public.movie",
    "MP4": "public.mpeg-4",
    "MOV": "com.apple.quicktime-movie",
    "AVI": "public.avi",
    "MKV": "org.matroska.mkv",
    
    # Documents/Text
    "FOLDER": "public.folder",
    "APP": "com.apple.application-bundle",
    "BUNDLE": "com.apple.bundle",
    "EXE": "com.apple.executable",
    "NATIVEEXE": "com.apple.mach-o-binary",
    "CLI": "public.unix-executable",
    "ANY": "public.item",
    "DATA": "public.data",
    "UTF-8_TXT": "public.utf8-plain-text",
    "TEXT": "public.plain-text",
    "MARKDOWN": "net.daringfireball.markdown",
    "PLIST": "com.apple.property-list",
    "HTML": "public.html",
    "DOCS": "public.content",
    "PDF": "com.adobe.pdf",
    "RTF": "public.rtf",
    "RTFD": "com.apple.rtfd",
    
    # Source code
    "ANYCODE": "public.source-code",
    "PYTHON": "public.python-script",
    "JAVASCRIPT": "com.netscape.javascript-source", # apple forgor to update this lol
    "SHELLSCRIPT": "public.shell-script",
    "HTMLSCRIPT": "public.html",
    "JAVA": "com.sun.java-source",
    
    # Archives
    "ZIP": "com.pkware.zip-archive",
    "RAR": "com.rarlab.rar-archive",
    "TAR": "public.tar-archive",
    "GZIP": "org.gnu.gnu-zip-archive",
    "7Z": "org.7-zip.7-zip-archive",
    
    # Fonts
    "FONT": "public.font",
    "OTF": "public.opentype-font",
    "TTF": "public.truetype-font",
    
    # Databases
    "SQLITE": "com.apple.sqlite3-db",
    
    # Executables & Apps
    "KEXT": "com.apple.kernel-extension",
    "DMG": "com.apple.disk-image",
    
    # Miscellaneous
    "XML": "public.xml",
    "JSON": "public.json",
    "CSV": "public.comma-separated-values-text",
    
    # Custom / unofficial
    "RPY": "net.renpy.script",
}

run_applescript = init.run_applescript
def get_finder_front_window_path() -> str:
    script = '''
    tell application "Finder"
        try
            set thePath to (POSIX path of (target of front window as alias))
            return thePath
        on error
            return ""
        end try
    end tell
    '''
    return init.run_applescript(script)
def empty_trash() -> None:
    script = '''
    tell application "Finder"
        empty the trash
    end tell
    '''
    init.run_applescript(script)

def move_to_trash(path: str) -> None:
    script = f'''
    tell application "Finder"
        delete POSIX file "{path}"
    end tell
    '''
    init.run_applescript(script)
def get_finder_selection() -> list[str]:
    script = '''
    tell application "Finder"
        set selectedItems to selection
        set itemPaths to {}
        repeat with i in selectedItems
            set end of itemPaths to POSIX path of (i as alias)
        end repeat
        return itemPaths as string
    end tell
    '''
    result = init.run_applescript(script)
    return [item.strip() for item in result.split(",")] if result else []
def reveal_in_finder(path: str) -> None:
    script = f'''
    tell application "Finder"
        reveal POSIX file "{path}"
        activate
    end tell
    '''
    init.run_applescript(script)
def open_folder_in_finder(path: str) -> None:
    script = f'''
    tell application "Finder"
        open POSIX file "{path}"
        activate
    end tell
    '''
    init.run_applescript(script)
import subprocess

def quick_look_file(filepath):
    subprocess.run(["qlmanage", "-p", filepath])
def open_file(prompt="Choose a file", file_types=None):
    type_clause = ""
    if file_types:
        types_str = "{" + ", ".join([f'"{ftype}"' for ftype in file_types]) + "}"
        type_clause = f" of type {types_str}"
    
    script = f'''
    set chosenFile to choose file{type_clause} with prompt "{prompt}"
    POSIX path of chosenFile
    '''
    result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
    return result.stdout.strip() if result.returncode == 0 else None
def open_folder(prompt="Choose a folder"):
    return run_applescript(f'set f to choose folder with prompt "{prompt}"\nPOSIX path of f')
def save_file(prompt="Save as", default_name="Untitled.txt", default_folder=None):
    folder_line = f'set defaultFolder to POSIX file "{default_folder}"' if default_folder else ''
    default_location_line = 'default location defaultFolder' if default_folder else ''
    
    script = f'''
    {folder_line}
    set defaultName to "{default_name}"
    set f to choose file name with prompt "{prompt}" default name defaultName {default_location_line}
    POSIX path of f
    '''
    try:
        return run_applescript(script)
    except:
        return None

def save_new_folder(prompt="Select location to create new folder", default_name="New Folder"):
    # Step 1: Ask user for parent folder
    parent_folder = run_applescript(f'''
    set f to choose folder with prompt "{prompt}"
    POSIX path of f
    ''')
    if not parent_folder:
        return None
    
    # Step 2: Ask user for new folder name
    new_folder_name = run_applescript(f'''
    display dialog "Enter new folder name:" default answer "{default_name}"
    text returned of result
    ''')
    if not new_folder_name:
        return None
    
    # Step 3: Combine and return full path for folder creation
    new_folder_path = os.path.join(parent_folder, new_folder_name)
    return new_folder_path

def findfileclass(path):
    if not os.path.exists(path):
        return None
    try:
        result = subprocess.run(
            ["mdls", "-name", "kMDItemContentType", "-name", "kMDItemContentTypeTree", path],
            capture_output=True, text=True
        )
        return result.stdout.strip()
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    print("Window path "+get_finder_front_window_path())
    #open_folder_in_finder(os.path.expanduser("~"))
    #quick_look_file(os.path.expanduser("~/Documents/TESTTEST/TESTTEST/TESTTESTApp.swift"))
    print(open_file("Pick a PNG", file_types=["public.png"]))
    print(findfileclass("/Users/annes/Documents/EEEEE/game/script.rpy"))
    print(save_file("aaa", "ko.rb", "/"))
    print(save_new_folder("sadada"))