from pathlib import Path
import pandas as pd
import re

# Regex for timestamp in filename: e.g., 2026-Apr-04_17.08.44
TIMESTAMP_FN_REGEX = re.compile(r"(\d{4}-[A-Za-z]{3}-\d{2})_(\d{2}\.\d{2}\.\d{2})")

def parse_image_filename(path: Path):
    name = path.name

    # Timestamp extrahieren
    m_ts = TIMESTAMP_FN_REGEX.search(name)
    if not m_ts:
        return None

    date_str = m_ts.group(1)
    time_str = m_ts.group(2).replace(".", ":")

    ts = pd.to_datetime(f"{date_str} {time_str}", format="%Y-%b-%d %H:%M:%S", errors="coerce")
    if pd.isna(ts):
        return None

    # relative Pfade erzeugen
    project_root = Path(__file__).resolve().parent.parent
    relative_path = path.resolve().relative_to(project_root)

    return {
        "timestamp_img": ts,
        "image_path": str(relative_path).replace("\\", "/")
    }


def load_images(image_dir: str) -> pd.DataFrame:
    paths = list(Path(image_dir).glob("*.png"))
    records = []

    for p in paths:
        parsed = parse_image_filename(p)
        if parsed:
            records.append(parsed)

    df = pd.DataFrame(records)
    df.sort_values("timestamp_img", inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df