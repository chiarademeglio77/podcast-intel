import json
import os
import glob

# PERCORSI (Il tuo computer)
REPORT_SOURCE = r"C:\Users\Andromeda\Music\Grover Podcast\_Reports"
GITHUB_FOLDER = r"C:\Users\Andromeda\Music\Grover Podcast\_App"

def run_daily_sync():
    all_summaries = []
    
    # 1. Cerca tutti i file .txt
    if not os.path.exists(REPORT_SOURCE):
        print(f"❌ Errore: Cartella non trovata: {REPORT_SOURCE}")
        return

    # Cerca qualsiasi file .txt (più flessibile)
    report_files = glob.glob(os.path.join(REPORT_SOURCE, "*.txt"))
    print(f"📂 Trovati {len(report_files)} file nella cartella _Reports")
    
    for file_path in report_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                
            # Divide in sezioni se ci sono più podcast nello stesso file
            sections = content.split("---")
            
            for section in sections:
                lines = [l.strip() for l in section.strip().split("\n") if l.strip()]
                if not lines: continue
                
                # --- LOGICA INTELLIGENTE ---
                # Invece di fidarci dell'ordine (riga 1, riga 2...), cerchiamo le etichette
                entry = {}
                summary_lines = []
                capture_summary = False
                
                for line in lines:
                    if line.startswith("FILENAME:"):
                        entry["file"] = line.replace("FILENAME:", "").strip()
                        capture_summary = False
                    elif line.startswith("DATE:"):
                        entry["date"] = line.replace("DATE:", "").strip()
                        capture_summary = False
                    elif line.startswith("KEYWORDS:"):
                        raw_keys = line.replace("KEYWORDS:", "").strip()
                        entry["keys"] = [k.strip() for k in raw_keys.split(",") if k.strip()]
                        capture_summary = False
                    elif line.startswith("SUMMARY:"):
                        first_line_summary = line.replace("SUMMARY:", "").strip()
                        if first_line_summary:
                            summary_lines.append(first_line_summary)
                        capture_summary = True
                    elif capture_summary:
                        # Se stiamo leggendo il riassunto e la riga non è un header, è parte del testo
                        summary_lines.append(line)
                
                # Uniamo le righe del riassunto
                entry["summary"] = " ".join(summary_lines)

                # CONTROLLO DI QUALITÀ
                # Se manca la data, usa "Unknown Date" invece di rompersi
                if "date" not in entry:
                    entry["date"] = "Unknown Date"
                if "file" not in entry:
                    # Se non trova FILENAME nel testo, usa il nome del file fisico
                    entry["file"] = os.path.basename(file_path)
                
                # Aggiungiamo solo se abbiamo almeno un riassunto
                if "summary" in entry and entry["summary"]:
                    all_summaries.append(entry)
                    
        except Exception as e:
            print(f"⚠️ Errore leggendo {os.path.basename(file_path)}: {e}")

    # Salva il file JSON
    master_file = os.path.join(GITHUB_FOLDER, "app_data.json")
    with open(master_file, "w", encoding="utf-8") as out:
        json.dump(all_summaries, out, indent=4)
    
    print(f"\n✅ SUCCESSO! Database rigenerato con {len(all_summaries)} podcast.")
    print(f"📁 File salvato in: {master_file}")

if __name__ == "__main__":
    run_daily_sync()