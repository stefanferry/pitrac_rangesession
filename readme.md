# PiTrac Range Session – Shot & Image Viewer
DISCLAIMER: This project relies heavily on LLM generated code and lacks so far sufficient testing and verification. Please verifiy data quality by randomly comparing the raw log and image files to the dasboard visualisation.

This project processes PiTrac shot data by combining the log file and images trough a timestamp matching logic to create a interactive analysis tool.  
It loads shot results from the log file, matches it with captured images, exports the combined dataset as a .pkl database, and provides an interactive dashboard for exploring each shot in detail.

---

## Features

### Logfile Parsing  
Reads raw `.log` files containing shot timestamps, ball data, and CSV‑based metrics.
Can be drawn from: 
```bash
/home/user/.pitrac/logs
```


### Image Loading  
Loads all images from directory and extracts timestamps and metadata.
Can be drawn from: 
```bash
/home/user/LM_Shares/Images
```

### Shot–Image Matching  
Automatically matches each shot with the closest images (within a 1‑minute window).

### PKL + Excel Export  
Saves the merged dataset as:
- a `.pkl` file for fast re‑loading  
- an optional `.xlsx` export for external analysis and troubleshooting

### Interactive Dash Plot  
A browser‑based dashboard that includes:
- scatter plot (configurable y-content vs. shot time-stamp)
- hover‑based shot selection
- **keyboard navigation** (← / →) -> not working right now
- automatic image display for each shot
- grouped spin images and other images
- special ordering (e.g., `final_found_ball` always last)

---



## Project Structure
```
pitrac_rangesession/
│
├── src/
│   ├── log_parser.py
│   ├── image_loader.py
│   ├── matcher.py
│   └── plotting.py
├── data/
│   ├── example/ #minimal example if you have no data at hand
│   │   ├── images/ #example images from three shots
│   │   ├── sample.log # three shots from wich one was not detected
│   ├── test_*.log #drop your logfile here
│   └── images/ #drop your images here
├── output/ 
│   └── data.pkl  #will be created after you run main.py
├── exports/ 
│   └── data.xlsx  #will be created after you run main.py
├── .venv/ 
├── excel_export.py 
├── .gitignore
├── main.py 
├── pyproject.toml
└── README.md
```
---

## How It Works (main.py)

### 1. Parse Logfile  
Extracts shot timestamps, ball speed, club speed, spin, and other metrics.

### 2. Load Images  
Reads all images from the session folder and extracts timestamps from filenames.

### 3. Match Shots ↔ Images  
Each shot is matched with the closest images based on timestamp proximity.

### 4. Save as PKL  
The merged dataset is stored as `output/data.pkl`.

### 5. Optional Excel Export  
The PKL is exported to `exports/data.xlsx`y for easy verification

### 6. Interactive Plot  
A Dash application opens in your browser and allows:
- exploring shots visually by hovering over datapoints in the diagram
- comparing metrics  
- viewing matched images  

---

## Running the Project

Activate your virtual environment and run:

```bash
python main.py
```
