from src.log_parser import parse_logfile
from src.image_loader import load_images
from src.matcher import match_all_images_for_shots
from src.plotting import interactive_plot
from src.excel_export import export_pkl_to_excel
import os
import pandas as pd

def ensure_directories():
    os.makedirs("output", exist_ok=True)
    os.makedirs("exports", exist_ok=True)

def main():
    ensure_directories()
    
    log_path = "data/test_2026-02-14_17-15-51.0.log" #enter your log file here
    image_dir = "data/images"
    pkl_path = "output/data.pkl"
    excel_path = "exports/data.xlsx"

    """log_path = "data/example/sample.log"
    image_dir = "data/example/images"
    pkl_path = "output/data.pkl"
    excel_path = "exports/data.xlsx" """

    # 1) Read log (alle Shots + Timestamps + Ball-Daten + CSV-Daten)
    log_df = parse_logfile(log_path)

    # 2) Image + timestamp + shot number read
    img_df = load_images(image_dir)

    # 3) Match: Shot ↔ Picture with minimal time difference (max 1 minute allowed)
    merged_df = match_all_images_for_shots(log_df, img_df)

    # 4) .pkl save
    merged_df.to_pickle(pkl_path)

    # 5) excel export if wanted
    export_path = export_pkl_to_excel(pkl_path, excel_path)
    print("Excel saved in:", export_path)

    # 6) Interactive Plot
    #interactive_plot(merged_df, y_columns=["ball_speed", "back_spin"])
    interactive_plot(merged_df, y_axes={
        "ball_speed": 1,
        "time_between_center_images_ms": 2
        })



if __name__ == "__main__":
    main()