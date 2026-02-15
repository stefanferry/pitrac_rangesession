import os
import random
import pandas as pd
from PIL import Image

PKL_PATH = "output/data.pkl"

def debug_random_shot(path=PKL_PATH):
    print("=== PKL RANDOM SHOT IMAGE CHECK ===")
    print(f"Lade Datei: {path}")

    df = pd.read_pickle(path)

    # Zufällige Shot-Zeile auswählen
    idx = random.randint(0, len(df) - 1)
    row = df.iloc[idx]

    print(f"\n--- Zufälliger Shot ---")
    print(f"Shot-ID (ShotNo): {row['ShotNo']}")
    print(f"Ball Speed: {row['ball_speed']}")
    print(f"Timestamp: {row['timestamp_ball_hit_csv']}")

    # Prüfen, ob Raster-Variante oder Einzelbild
    if "images" in df.columns:
        print("\n--- Bilder dieses Shots ---")

        images = row["images"]
        if images is None or len(images) == 0:
            print("Keine Bilder für diesen Shot gefunden.")
            return

        for img in images:
            path = img["image_path"]
            img_type = img.get("img_type", "unknown")

            print(f"Öffne: {path}  | Typ: {img_type}")

            if os.path.exists(path):
                try:
                    Image.open(path).show()
                except Exception as e:
                    print(f"Fehler beim Öffnen: {e}")
            else:
                print(f"FEHLT: {path}")

    else:
        print("\n--- Einzelbild-Variante ---")
        path = row["image_path"]

        print(f"Öffne: {path}")

        if os.path.exists(path):
            try:
                Image.open(path).show()
            except Exception as e:
                print(f"Fehler beim Öffnen: {e}")
        else:
            print(f"FEHLT: {path}")

    print("\n--- Fertig ---")


if __name__ == "__main__":
    debug_random_shot()