import json
import os
import glob

# PERCORSI CORRETTI PER IL TUO PC
REPORT_SOURCE = r"C:\Users\Andromeda\Music\Grover Podcast\_Reports"
GITHUB_FOLDER = r"C:\Users\Andromeda\Music\Grover Podcast\_App"

def run_daily_sync():
    all_summaries = []
    
    # Controlla se le cartelle esistono
    if not os.path.exists(REPORT_SOURCE):
        print(f"❌ Errore: La cartella dei report non esiste: {REPORT_SOURCE}")
        return
    
    # Cerca i file report
    report_files = glob.glob(os.path.join(REPORT_SOURCE, "*_Reports-txt.txt"))
    print(f"File trovati in _Reports: {len(report_files)}")
    
    for file_path in report_files:
        with open(file_path, "r", encoding="utf-8") as f:
            sections = f.read().split("---")
            
        for section in sections:
            lines = [l.strip() for l in section.strip().split("\n") if l.strip()]
            if len(lines) >= 4:
                entry = {
                    "file": lines[0].replace("FILENAME:", "").strip(),
                    "date": lines[1].replace("DATE:", "").strip(),
                    "keys": [k.strip() for k in lines[2].replace("KEYWORDS:", "").split(",")],
                    "summary": lines[3].replace("SUMMARY:", "").strip()
                }
                if entry not in all_summaries:
                    all_summaries.append(entry)

    if not all_summaries:
        print("⚠️ Nessun dato trovato nei file .txt. Controlla il formato!")
        return

    # Salva il file JSON nella stessa cartella dell'app
    master_file = os.path.join(GITHUB_FOLDER, "app_data.json")
    
    try:
        with open(master_file, "w", encoding="utf-8") as out:
            json.dump(all_summaries, out, indent=4)
        print(f"✅ SUCCESSO! Creato: {master_file}")
        print(f"Episodi pronti: {len(all_summaries)}")
    except Exception as e:
        print(f"❌ Errore durante il salvataggio: {e}")

if __name__ == "__main__":
    run_daily_sync()