import json
import os
import glob

# PERCORSI CORRETTI
REPORT_SOURCE = r"C:\Users\Andromeda\Music\Grover Podcast\_Reports"
GITHUB_FOLDER = r"C:\Users\Andromeda\Music\Grover Podcast\_App"

def run_daily_sync():
    all_summaries = []
    
    # Controllo cartella
    if not os.path.exists(REPORT_SOURCE):
        print(f"❌ Errore: Cartella non trovata: {REPORT_SOURCE}")
        return

    # Cerca tutti i file .txt
    report_files = glob.glob(os.path.join(REPORT_SOURCE, "*.txt"))
    print(f"📂 Trovati {len(report_files)} file nella cartella _Reports")
    
    for file_path in report_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                # Divide i report separati da ---
                sections = f.read().split("---")
            
            for section in sections:
                # Pulisce le righe vuote
                lines = [l.strip() for l in section.strip().split("\n") if l.strip()]
                
                # LA LOGICA CLASSICA: Si aspetta almeno 4 righe in ordine
                if len(lines) >= 4:
                    entry = {
                        "file": lines[0].replace("FILENAME:", "").strip(),
                        "date": lines[1].replace("DATE:", "").strip(),
                        "keys": [k.strip() for k in lines[2].replace("KEYWORDS:", "").split(",")],
                        "summary": lines[3].replace("SUMMARY:", "").strip()
                    }
                    # Evita duplicati
                    if entry not in all_summaries:
                        all_summaries.append(entry)
                        
        except Exception as e:
            print(f"⚠️ Errore nel file {os.path.basename(file_path)}: {e}")

    # Salva il file finale
    master_file = os.path.join(GITHUB_FOLDER, "app_data.json")
    with open(master_file, "w", encoding="utf-8") as out:
        json.dump(all_summaries, out, indent=4)
    
    print(f"\n✅ SUCCESSO! Database rigenerato con {len(all_summaries)} episodi.")

if __name__ == "__main__":
    run_daily_sync()