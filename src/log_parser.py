# log_parser.py
import re
import pandas as pd

# -----------------------------
# Timestamp extraction
# -----------------------------
TIMESTAMP_REGEX = re.compile(
    r"\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+)\]"
)

def extract_timestamp(line):
    """Extracts timestamp from a log line or returns None"""
    m = TIMESTAMP_REGEX.search(line)
    if not m:
        return None
    return pd.to_datetime(m.group(1), errors="coerce")


# -----------------------------
# BALL_HIT_CSV Parser
# -----------------------------
CSV_COLUMNS = [
    "ShotNo", "carry", "total", "side_dest", "smash_factor",
    "club_speed", "ball_speed", "back_spin", "side_spin",
    "vla", "hla", "descent_angle", "apex", "flight_time", "type"
]

def parse_ball_hit_csv(line):
    """Parse a BALL_HIT_CSV line into dict of columns"""
    raw = line.split("BALL_HIT_CSV,")[1].strip()
    parts = [p.strip() for p in raw.split(",")]

    cleaned = []
    for p in parts:
        if "NA" in p or "Error" in p:
            cleaned.append(None)
        else:
            p = p.replace("(", "").replace(")", "")
            try:
                cleaned.append(float(p))
            except ValueError:
                cleaned.append(p)

    while len(cleaned) < len(CSV_COLUMNS):
        cleaned.append(None)

    return dict(zip(CSV_COLUMNS, cleaned))


# -----------------------------
# Ball Info Parser
# -----------------------------
def parse_ball_block(line, prefix, current):
    """Extract ball info like Ball No, position, radius, circle, cal, DistFromLens"""
    # Ball No, Position, Radius
    m = re.search(
        r"Ball No\.\s*(\d+).*?\(x,y\)=\(\s*([\d\.-]+),\s*([\d\.-]+)\s*\).*?r=([\d\.]+)",
        line
    )
    if m:
        current[f"{prefix}_ball_no"] = int(m.group(1))
        current[f"{prefix}_ball_x"] = float(m.group(2))
        current[f"{prefix}_ball_y"] = float(m.group(3))
        current[f"{prefix}_ball_r"] = float(m.group(4))

    # Circle
    m = re.search(
        r"Circle\[\(x,y\)=\(([\d\.-]+),([\d\.-]+)\), r=([\d\.]+)\]",
        line
    )
    if m:
        current[f"{prefix}_circle_x"] = float(m.group(1))
        current[f"{prefix}_circle_y"] = float(m.group(2))
        current[f"{prefix}_circle_r"] = float(m.group(3))

    # cal
    m = re.search(r"cal=(true|false)", line)
    if m:
        current[f"{prefix}_cal"] = m.group(1) == "true"

    # DistFromLens
    m = re.search(r"DistFromLens=([\d\.]+)m", line)
    if m:
        current[f"{prefix}_dist_from_lens"] = float(m.group(1))

    # CalFocLen
    m = re.search(r"CalFocLen=([\d\.-]+)", line)
    if m:
        current[f"{prefix}_cal_foc_len"] = float(m.group(1))


# -----------------------------
# Main robust log parser
# -----------------------------
def parse_logfile(path):
    results = []
    current = {}
    current_lines = []
    ts_last = None
    shot_id = -1

    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.rstrip("\n")
            ts = extract_timestamp(line)
            if ts is not None:
                ts_last = ts  # remember last valid timestamp

            # Start new shot block
            if "BALL HIT" in line:
                current = {}
                current_lines = [line]
                ts_last = ts_last  # keep timestamp for BALL HIT
                current["timestamp_hit_start"] = ts_last
                shot_id += 1
                current["shot_id"] = shot_id
            else:
                # Append line to current_lines if in a shot
                if current_lines is not None:
                    current_lines.append(line)

            if current:
                # Teed-up Ball
                if "Teed-up Ball:" in line:
                    current["timestamp_teed_up_ball"] = ts_last
                    parse_ball_block(line, "teed", current)

                # First Ball After ComputeBallDeltas
                if "First' Ball After ComputeBallDeltas" in line or \
                   "First Ball After ComputeBallDeltas" in line:
                    current["timestamp_first_ball"] = ts_last
                    parse_ball_block(line, "first", current)

                # Grayscale
                if "Grayscale conversion completed" in line:
                    current["timestamp_gray_done"] = ts_last

                # Driving mode
                if "In driving mode" in line:
                    current["timestamp_driving_mode"] = ts_last

                # Time between center-most images
                if "Time between center-most images" in line:
                    m = re.search(r"Time between center-most images:\s*([\d\.]+)ms", line)
                    if m:
                        current["time_between_center_images_ms"] = float(m.group(1))

                # BallAngles
                if "BallAngles" in line:
                    m = re.search(r"BallAngles\(x,y\)=\(([\d\.-]+)\s*,\s*([\d\.-]+)\)", line)
                    if m:
                        current["ball_angle_x"] = float(m.group(1))
                        current["ball_angle_y"] = float(m.group(2))

                # DistCam
                if "DistCam" in line:
                    m = re.search(r"DistCam\(x,y,z\)=\(([\d\.-]+),([\d\.-]+),([\d\.-]+)\)", line)
                    if m:
                        current["distcam_x"] = float(m.group(1))
                        current["distcam_y"] = float(m.group(2))
                        current["distcam_z"] = float(m.group(3))

                # AnglesCam
                if "AnglesCam" in line:
                    m = re.search(r"AnglesCam\(x,y\)=\(([\d\.-]+),([\d\.-]+)\)", line)
                    if m:
                        current["anglescam_x"] = float(m.group(1))
                        current["anglescam_y"] = float(m.group(2))

                # avgC
                if "avgC" in line:
                    m = re.search(r"avgC:\[\s*([\d\.-]+),\s*([\d\.-]+),\s*([\d\.-]+)\]", line)
                    if m:
                        current["avgC_r"] = float(m.group(1))
                        current["avgC_g"] = float(m.group(2))
                        current["avgC_b"] = float(m.group(3))

                # stdC
                if "stdC" in line:
                    m = re.search(r"stdC:\[\s*([\d\.-]+),\s*([\d\.-]+),\s*([\d\.-]+)\]", line)
                    if m:
                        current["stdC_r"] = float(m.group(1))
                        current["stdC_g"] = float(m.group(2))
                        current["stdC_b"] = float(m.group(3))

                # Spin detection
                if "Spin detection completed" in line:
                    current["timestamp_spin_done"] = ts_last

                # BALL_HIT_CSV → end of shot block
                if "BALL_HIT_CSV" in line:
                    current["timestamp_ball_hit_csv"] = ts_last
                    current.update(parse_ball_hit_csv(line))
                    current["lines"] = current_lines.copy()
                    results.append(current)
                    current = {}
                    current_lines = []

    return pd.DataFrame(results)