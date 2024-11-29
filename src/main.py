import os
from steps.load_data import load_or_create_combined_data
from steps.process_steps import apply_all_steps
from steps.save_and_resume import get_latest_step

def main():
    latest_step, df_combined = get_latest_step()
    print(f"Starting from STEP {latest_step}")

    if latest_step == 0:
        df_combined = load_or_create_combined_data()

    df_combined = apply_all_steps(df_combined, starting_step=latest_step)
    print("Pipeline completed successfully!")

if __name__ == "__main__":
    main()