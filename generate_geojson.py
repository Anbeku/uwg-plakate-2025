import os
import exifread
import json
from datetime import datetime

# >>> HIER ANPASSEN: Dein GitHub Nutzername
GITHUB_USERNAME = "Anbeku"  # ← ändern!
REPO_NAME = "uwg-plakate-2025"
IMAGE_FOLDER = "bilder"

GITHUB_BASE_URL = f"https://{GITHUB_USERNAME}.github.io/{REPO_NAME}/{IMAGE_FOLDER}"

def dms_to_decimal(dms_tag, ref):
    dms = [float(x.num) / x.den for x in dms_tag.values]
    decimal = dms[0] + dms[1] / 60 + dms[2] / 3600
    if ref in ['S', 'W']:
        decimal *= -1
    return decimal

def get_exif_data(image_path):
    with open(image_path, 'rb') as f:
        tags = exifread.process_file(f, details=False)

        try:
            lat = dms_to_decimal(tags['GPS GPSLatitude'], tags['GPS GPSLatitudeRef'].values)
            lon = dms_to_decimal(tags['GPS GPSLongitude'], tags['GPS GPSLongitudeRef'].values)
        except KeyError:
            return None

        # Datum/Uhrzeit
        date_time = tags.get('EXIF DateTimeOriginal') or tags.get('Image DateTime')
        if date_time:
            try:
                date_str = str(date_time.values)
                dt = datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
                date_iso = dt.isoformat()
            except:
                date_iso = date_str
        else:
            date_iso = None

        return {
            'lat': lat,
            'lon': lon,
            'datetime': date_iso
        }

def extract_all_gps():
    features = []
    image_dir = os.path.join(os.getcwd(), IMAGE_FOLDER)

    if not os.path.exists(image_dir):
        print(f"❌ Ordner nicht gefunden: {image_dir}")
        return

    for filename in sorted(os.listdir(image_dir)):
        if filename.lower().endswith(('.jpg', '.jpeg')):
            image_path = os.path.join(image_dir, filename)
            exif_data = get_exif_data(image_path)
            if exif_data:
                feature = {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [exif_data['lon'], exif_data['lat']]
                    },
                    "properties": {
                        "datetime": exif_data['datetime'],
                        "image_url": f"{GITHUB_BASE_URL}/{filename}"
                    }
                }
                features.append(feature)

    geojson = {
        "type": "FeatureCollection",
        "features": features
    }

    output_path = os.path.join(os.getcwd(), "photo_locations.geojson")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(geojson, f, indent=2)
    print(f"✅ Exportiert: {len(features)} Punkte → {output_path}")

if __name__ == "__main__":
    print(f"📁 Verzeichnis: {os.getcwd()}")
    extract_all_gps()
