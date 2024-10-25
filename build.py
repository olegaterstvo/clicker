import PyInstaller.__main__

PyInstaller.__main__.run([
    'main.py',
    '--windowed',
    '--onefile',
    '--icon=icon.ico',
    '--clean',
    '--name=ChronosProjectAdvancedKlickerApplication',
    '--version-file=file_version_info.txt'
])