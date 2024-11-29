#steps/save_and_resume.py

import os
from utils.file_operations import save_to_csv
import config

def get_latest_step():
    step_dir = config.STEPS_DIR
    steps = [int(file.split("_")[0].replace("STEP", "")) for file in os.listdir(step_dir) if file.startswith("STEP")]
    if steps:
        latest_step = max(steps)
        latest_file = config.get_step_filename(latest_step, "*")
        return latest_step, pd.read_csv(latest_file)
    return 0, None

def apply_step(df, step_number, description, function):
    df = function(df)
    step_filename = config.get_step_filename(step_number, description)
    save_to_csv(df, step_filename)
    print(f"Saved STEP {step_number}: {description}")
    return df
