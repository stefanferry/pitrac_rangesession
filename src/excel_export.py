# excel_export.py

import pandas as pd
from pathlib import Path


def export_pkl_to_excel(pkl_path: str, excel_path: str):
    """
    Lädt eine PKL-Datei (DataFrame) und exportiert sie 1:1 nach Excel.
    Keine Änderungen, keine Filter, keine Bildlogik.
    """

    pkl_path = Path(pkl_path)
    excel_path = Path(excel_path)

    if not pkl_path.exists():
        raise FileNotFoundError(f"PKL-Datei nicht gefunden: {pkl_path}")

    # PKL laden
    df = pd.read_pickle(pkl_path)

    # Ordner für Excel-Datei erstellen
    excel_path.parent.mkdir(parents=True, exist_ok=True)

    # Excel exportieren
    df.to_excel(excel_path, index=False)

    return excel_path