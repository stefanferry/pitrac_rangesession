import os
import pandas as pd

df = pd.read_pickle("output/data.pkl")

shot = 83  # Beispiel aus deiner Fehlermeldung

for img in df.loc[df["ShotNo"] == shot, "images"].iloc[0]:
    p = img["image_path"]
    print(p, "→", os.path.exists(p))