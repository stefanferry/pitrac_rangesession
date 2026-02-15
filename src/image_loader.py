from pathlib import Path
import pandas as pd
import re

def parse_image_filename(path: Path):
    name = path.name

    # Shot extrahieren
    m_shot = re.search(r"Shot_(\d+)", name)
    if not m_shot:
        return None
    shot = int(m_shot.group(1))

    # Timestamp extrahieren
    m_ts = re.search(r"(\d{4}-[A-Za-z]{3}-\d{2})_(\d{2}\.\d{2}\.\d{2})", name)
    if not m_ts:
        return None

    date_str = m_ts.group(1)
    time_str = m_ts.group(2).replace(".", ":")

    ts = pd.to_datetime(f"{date_str} {time_str}", format="%Y-%b-%d %H:%M:%S")

    # relative Pfade erzeugen
    project_root = Path(__file__).resolve().parent.parent
    relative_path = path.resolve().relative_to(project_root)

    return {
        "shot": shot,
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

    return pd.DataFrame(records)