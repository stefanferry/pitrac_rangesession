import pandas as pd

def match_shots_and_images(df_shots: pd.DataFrame, df_imgs: pd.DataFrame):
    results = []

    for _, shot_row in df_shots.iterrows():
        shot_id = int(shot_row["ShotNo"])
        shot_ts = shot_row["timestamp_ball_hit_csv"]

        # Bilder dieses Shots
        imgs = df_imgs[df_imgs["shot"] == shot_id]

        if imgs.empty:
            # Kein Bild gefunden
            row = shot_row.to_dict()
            row["image_path"] = None
            row["timestamp_img"] = None
            row["img_time_diff_ms"] = None
            results.append(row)
            continue

        # Zeitdifferenz berechnen
        imgs = imgs.copy()
        imgs["time_diff"] = (imgs["timestamp_img"] - shot_ts).abs()

        # Bild mit minimaler Abweichung
        best = imgs.sort_values("time_diff").iloc[0]

        row = shot_row.to_dict()
        row["image_path"] = best["image_path"]
        row["timestamp_img"] = best["timestamp_img"]
        row["img_time_diff_ms"] = best["time_diff"].total_seconds() * 1000

        results.append(row)

    return pd.DataFrame(results)

def match_all_images_for_shots(df_shots, df_imgs):
    results = []

    MAX_GAP = pd.Timedelta(minutes=1)

    for _, shot_row in df_shots.iterrows():
        shot_id = int(shot_row["ShotNo"])
        shot_ts = shot_row["timestamp_ball_hit_csv"]

        # Alle Bilder dieses Shots
        imgs = df_imgs[df_imgs["shot"] == shot_id].copy()

        row = shot_row.to_dict()

        if imgs.empty:
            row["images"] = []
            results.append(row)
            continue

        # Zeitdifferenz berechnen
        imgs["time_diff"] = (imgs["timestamp_img"] - shot_ts).abs()

        # Nur Bilder innerhalb 1 Minute behalten
        imgs = imgs[imgs["time_diff"] <= MAX_GAP]

        if imgs.empty:
            row["images"] = []
        else:
            row["images"] = imgs.to_dict(orient="records")

        results.append(row)

    return pd.DataFrame(results)