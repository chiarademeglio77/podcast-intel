import json
import os
import glob

# THESE PATHS MATCH YOUR COMPUTER EXACTLY
REPORT_SOURCE = r"C:\Users\Andromeda\Music\Grover Podcast\_Reports"
GITHUB_FOLDER = r"C:\GroverApp\podcast-intel" # Update this to where you just Cloned

def run_daily_sync():
    all_summaries = []
    
    # 1. Gather all your daily reports
    report_files = glob.glob(os.path.join(REPORT_SOURCE, "*_Reports-txt.txt"))
    
    for file_path in report_files:
        with open(file_path, "r", encoding="utf-8") as f:
            # Splits the NotebookLM output by the '---' line [cite: 106, 111]
            sections = f.read().split("---")
            
        for section in sections:
            lines = [l.strip() for l in section.strip().split("\n") if l.strip()]
            if len(lines) >= 4:
                # Matches the format: FILENAME, DATE, KEYWORDS, SUMMARY [cite: 102, 116]
                entry = {
                    "file": lines[0].replace("FILENAME:", "").strip(),
                    "date": lines[1].replace("DATE:", "").strip(),
                    "keys": [k.strip() for k in lines[2].replace("KEYWORDS:", "").split(",")],
                    "summary": lines[3].replace("SUMMARY:", "").strip()
                }
                if entry not in all_summaries:
                    all_summaries.append(entry)

    # 2. Save the master list into your GitHub folder
    master_file = os.path.join(GITHUB_FOLDER, "app_data.json")
    with open(master_file, "w", encoding="utf-8") as out:
        json.dump(all_summaries, out, indent=4)
    
    print(f"✅ Success! {len(all_summaries)} podcast summaries are ready to be pushed to the web.")

if __name__ == "__main__":
    run_daily_sync()