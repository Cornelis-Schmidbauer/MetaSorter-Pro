import os
from shutil import move
from datetime import datetime
from exif import Image

# Quell- und Zielordner definieren
source_folder = "source"
destination_folder = "sorted"
supported_extensions = (".arw", ".dng", ".cr2", ".nef", ".mov", ".mp4", ".avi", ".jpg", ".jpeg", ".png")

# Fehlerprotokoll
error_log = "error_log.txt"

def get_creation_date(file_path, extension):
    """Versucht, das Erstellungsdatum aus Metadaten oder Dateiattributen zu extrahieren."""
    try:
        if extension in (".arw", ".dng", ".cr2", ".nef", ".jpg", ".jpeg", ".png"):
            # Metadaten für Bilder auslesen
            with open(file_path, "rb") as image_file:
                img = Image(image_file)
                if hasattr(img, 'datetime_original'):
                    return datetime.strptime(img.datetime_original, "%Y:%m:%d %H:%M:%S")
        elif extension in (".mov", ".mp4", ".avi"):
            # Änderungsdatum für Videos nutzen (falls keine Metadaten vorhanden)
            return datetime.fromtimestamp(os.path.getmtime(file_path))
    except Exception as e:
        log_error(file_path, f"Metadaten konnten nicht ausgelesen werden: {e}")
    # Fallback: Änderungsdatum der Datei
    return datetime.fromtimestamp(os.path.getmtime(file_path))

def create_folder_structure(base_folder, date):
    """Erstellt die Ordnerstruktur basierend auf Datum."""
    folder_path = os.path.join(base_folder, f"{date.year}/{date.month:02}/{date.day:02}")
    os.makedirs(folder_path, exist_ok=True)
    return folder_path

def log_error(file_path, message):
    """Schreibt Fehler ins Protokoll."""
    with open(error_log, "a") as log:
        log.write(f"Datei: {file_path} - Fehler: {message}\n")

def sort_files():
    """Sortiert Dateien basierend auf ihren Metadaten."""
    for file in os.listdir(source_folder):
        file_path = os.path.join(source_folder, file)
        if os.path.isfile(file_path) and file.lower().endswith(supported_extensions):
            try:
                extension = os.path.splitext(file)[1].lower()
                date = get_creation_date(file_path, extension)
                folder_path = create_folder_structure(destination_folder, date)
                move(file_path, os.path.join(folder_path, file))
                print(f"Verschoben: {file} → {folder_path}")
            except Exception as e:
                log_error(file_path, f"Fehler beim Verschieben: {e}")

# Hauptfunktion starten
if __name__ == "__main__":
    sort_files()
    print("Sortierung abgeschlossen. Fehler siehe error_log.txt.")
