# PiTrac Range Session – Shot & Image Viewer

This project processes Pitrac data by combining log files, images trough an automated matching logic to create a fully interactive analysis tool.  
It loads shot results from the log file, matches it with captured images, exports the combined dataset as a .pkl database, and provides an interactive dashboard for exploring each shot in detail.

---

## 🚀 Features

### ✔ Logfile Parsing  
Reads raw `.log` files containing shot timestamps, ball data, and CSV‑based metrics.
Can be drawn from: 
```bash
/home/pitracsf1/.pitrac/logs
```


### ✔ Image Loading  
Loads all images from directory and extracts timestamps and metadata.
Can be drawn from: 
```bash
/home/user/LM_Shares/Images
```

### ✔ Shot–Image Matching  
Automatically matches each shot with the closest images (within a 1‑minute window).

### ✔ PKL + Excel Export  
Saves the merged dataset as:
- a `.pkl` file for fast re‑loading  
- an optional `.xlsx` export for external analysis and troubleshooting

### ✔ Interactive Dash Plot  
A browser‑based dashboard that includes:
- scatter plot (configurable y-content vs. shot time-stamp)
- hover‑based shot selection
- **keyboard navigation** (← / →) -> not working right now
- automatic image display for each shot
- grouped spin images and other images
- special ordering (e.g., `final_found_ball` always last)

---

## 📦 Project Structure

project/ 
│ 
├── src/ 
│   ├── log_parser.py 
│   ├── image_loader.py 
│   ├── matcher.py 
│   └── plotting.py  
├── data/ 
│   ├── test_*.log 
│   └── images/ 
├── output/ 
│   └── data.pkl 
├── exports/ 
│   └── data.xlsx 
├── .venv/ 
├── excel_export.py 
├── .gitignore
├── main.py 
├── pyproject.toml
└── README.md

---

## 🧠 How It Works

### 1. Parse Logfile  
Extracts shot timestamps, ball speed, club speed, spin, and other metrics.

### 2. Load Images  
Reads all images from the session folder and extracts timestamps from filenames.

### 3. Match Shots ↔ Images  
Each shot is matched with the closest images based on timestamp proximity.

### 4. Save as PKL  
The merged dataset is stored as `output/data.pkl`.

### 5. Optional Excel Export  
The PKL is exported to `exports/data.xlsx`.

### 6. Interactive Plot  
A Dash application opens in your browser and allows:
- exploring shots visually  
- comparing metrics  
- viewing matched images  
- navigating with keyboard arrows  

---

## ▶️ Running the Project

Activate your virtual environment and run:

```bash
python main.py
```
