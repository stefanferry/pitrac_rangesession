import pandas as pd

def match_shots_and_images(df_shots: pd.DataFrame, df_imgs: pd.DataFrame):
    results = []

    for _, shot_row in df_shots.iterrows():
        shot_id = int(shot_row["ShotNo"])
        shot_ts = shot_row["timestamp_ball_hit_csv"]

        # Bilder dieses Shots
        imgs = df_imgs[df_imgs["ShotNo"] == shot_id].copy()

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

r"""def match_all_images_for_shots(df_shots, df_imgs):
    results = []

    MAX_GAP = pd.Timedelta(minutes=1)

    for _, shot_row in df_shots.iterrows():
        shot_id = int(shot_row["ShotNo"])
        shot_ts = shot_row["timestamp_ball_hit_csv"]

        # Alle Bilder dieses Shots
        imgs = df_imgs[df_imgs["ShotNo"] == shot_id].copy()

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

    return pd.DataFrame(results)"""

def match_all_images_for_shots(df_shots, df_imgs, max_gap_minutes=0.2):
    """
    For each shot in df_shots, find all images from df_imgs within a MAX_GAP
    based on timestamp only. Returns df_shots with an 'images' column.
    """
    results = []

    MAX_GAP = pd.Timedelta(minutes=max_gap_minutes)

    # Make a copy to avoid modifying original df_imgs
    df_imgs_sorted = df_imgs.sort_values("timestamp_img").copy()

    for _, shot_row in df_shots.iterrows():
        shot_ts = shot_row["timestamp_ball_hit_csv"]

        # Calculate absolute time difference without modifying original df_imgs
        time_diff = (df_imgs_sorted["timestamp_img"] - shot_ts).abs()

        # Select images within MAX_GAP
        matching_imgs = df_imgs_sorted[time_diff <= MAX_GAP].copy()

        row = shot_row.to_dict()
        if matching_imgs.empty:
            row["images"] = []
        else:
            # Include timestamp differences if needed
            matching_imgs = matching_imgs.assign(
                time_diff_ms=(matching_imgs["timestamp_img"] - shot_ts).dt.total_seconds() * 1000
            )
            row["images"] = matching_imgs.to_dict(orient="records")

        results.append(row)

    return pd.DataFrame(results)