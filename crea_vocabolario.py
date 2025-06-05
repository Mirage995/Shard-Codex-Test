import json
import os # Per controllare se il file dizionario_nostro.json esiste

# --- Configurazione ---
INPUT_JSONL_FILE = "it-extract.jsonl"  # Il nome del tuo file scaricato e decompresso
OUTPUT_DICT_FILE = "dizionario_nostro.json"    # Il file dizionario di SHARD
MAX_ENTRIES_TO_PROCESS = 23000                 # Limite di voci da processare per ora (puoi cambiarlo)

def create_public_vocabulary():
    """
    Estrae parole e definizioni dal file JSONL di Wiktionary.
    """
    public_vocab = {}
    entries_processed = 0
    valid_entries_added = 0

    print(f"Inizio elaborazione del file: {INPUT_JSONL_FILE}")
    try:
        with open(INPUT_JSONL_FILE, 'r', encoding='utf-8') as f_in:
            for line_number, line in enumerate(f_in, 1):
                if entries_processed >= MAX_ENTRIES_TO_PROCESS:
                    print(f"Raggiunto il limite massimo di {MAX_ENTRIES_TO_PROCESS} voci da processare.")
                    break
                
                line_content = line.strip()
                if not line_content:  # Salta righe vuote se ce ne fossero
                    continue
                
                try:
                    data_entry = json.loads(line_content)
                    
                    word = data_entry.get("word")
                    senses = data_entry.get("senses")
                    
                    # Vogliamo solo parole italiane per il nostro dizionario principale
                    if data_entry.get("lang_code") != "it":
                        continue

                    if word and isinstance(word, str) and word.strip(): # Assicurati che la parola esista e non sia vuota
                        word = word.strip() # Pulisci spazi extra
                        if senses and isinstance(senses, list) and len(senses) > 0:
                            first_sense = senses[0]
                            if isinstance(first_sense, dict): # Verifica che il senso sia un dizionario
                                glosses = first_sense.get("glosses")
                                if glosses and isinstance(glosses, list) and len(glosses) > 0:
                                    definition = glosses[0]
                                    if isinstance(definition, str) and definition.strip():
                                        # Per ora prendiamo la definizione così com'è.
                                        # Potremmo volerla "pulire" in futuro.
                                        public_vocab[word] = definition.strip()
                                        valid_entries_added += 1
                                    else:
                                        # print(f"Attenzione: Definizione vuota o non stringa per la parola '{word}' alla riga {line_number}.")
                                        pass # Ignora se la definizione non è valida
                                else:
                                    # print(f"Attenzione: Campo 'glosses' mancante, vuoto o non lista per la parola '{word}' alla riga {line_number}.")
                                    pass
                            else:
                                # print(f"Attenzione: Il primo 'sense' non è un dizionario per la parola '{word}' alla riga {line_number}.")
                                pass
                        # else:
                            # print(f"Attenzione: Campo 'senses' mancante, vuoto o non lista per la parola '{word}' alla riga {line_number}.")
                            # pass # La parola potrebbe non avere sensi/definizioni (es. redirects)
                    # else:
                        # print(f"Attenzione: Parola mancante o non valida alla riga {line_number}.")
                        # pass
                        
                    entries_processed += 1
                    if entries_processed % 1000 == 0: # Stampa un progresso ogni 1000 righe lette
                        print(f"Lette {entries_processed} righe... Aggiunte {valid_entries_added} voci valide.")
                                
                except json.JSONDecodeError:
                    # print(f"Attenzione: Errore di decodifica JSON alla riga {line_number}: {line_content}")
                    entries_processed += 1 # Conta comunque come riga processata per il limite
                    continue 
                except Exception as e:
                    # print(f"Attenzione: Errore generico processando la riga {line_number} (parola: {word if 'word' in locals() and word else 'N/A'}): {e}")
                    entries_processed += 1 # Conta comunque come riga processata per il limite
                    continue
                    
    except FileNotFoundError:
        print(f"ERRORE CRITICO: File di input non trovato: {INPUT_JSONL_FILE}")
        return None
    except Exception as e:
        print(f"ERRORE CRITICO: Impossibile leggere il file di input {INPUT_JSONL_FILE}: {e}")
        return None

    print(f"Elaborazione completata. Righe totali lette: {entries_processed}. Voci valide aggiunte al vocabolario pubblico: {valid_entries_added}")
    return public_vocab

def initialize_or_load_shard_dictionary(output_file_path):
    """
    Inizializza un nuovo dizionario di SHARD o carica uno esistente.
    """
    base_structure = {
        "glossario": {},
        "memoria": {},
        "conoscenza": {},
        "vocabolario_pubblico": {}
    }
    
    if os.path.exists(output_file_path):
        try:
            with open(output_file_path, 'r', encoding='utf-8') as f_dict_in:
                print(f"Caricamento del dizionario esistente da: {output_file_path}")
                existing_dict = json.load(f_dict_in)
                # Assicura che tutte le chiavi base siano presenti, mantenendo i dati esistenti
                for key in base_structure:
                    if key not in existing_dict:
                        existing_dict[key] = base_structure[key]
                return existing_dict
        except Exception as e:
            print(f"Attenzione: Impossibile caricare il dizionario esistente {output_file_path}. Verrà creato con la struttura base. Errore: {e}")
            # Se il caricamento fallisce ma il file esiste, è meglio partire dalla struttura base
            # per evitare di propagare un JSON corrotto.
            return base_structure
    else:
        print(f"File dizionario non trovato. Verrà creato un nuovo file: {output_file_path} con la struttura base.")
        return base_structure

def save_shard_dictionary(shard_data, output_file_path):
    """
    Salva il dizionario completo di SHARD su file.
    """
    try:
        with open(output_file_path, 'w', encoding='utf-8') as f_dict_out:
            json.dump(shard_data, f_dict_out, indent=2, ensure_ascii=False)
        print(f"Dizionario di SHARD salvato/aggiornato con successo in: {output_file_path}")
    except Exception as e:
        print(f"ERRORE CRITICO: Impossibile salvare il dizionario di SHARD in {output_file_path}: {e}")

if __name__ == "__main__":
    print("Avvio script per creare/aggiornare il dizionario di SHARD...")
    
    # 1. Inizializza o carica il dizionario esistente di SHARD
    shard_dictionary_data = initialize_or_load_shard_dictionary(OUTPUT_DICT_FILE)
    
    # 2. Crea/Estrai il vocabolario pubblico dal file JSONL
    #    Questa parte sovrascriverà la sezione "vocabolario_pubblico" esistente
    #    se l'estrazione ha successo.
    extracted_public_vocab = create_public_vocabulary()
    
    if extracted_public_vocab is not None: # Se l'estrazione ha prodotto qualcosa (anche un dizionario vuoto se il file era vuoto o MAX_ENTRIES era 0)
        shard_dictionary_data["vocabolario_pubblico"] = extracted_public_vocab
        print(f"Sezione 'vocabolario_pubblico' aggiornata con {len(extracted_public_vocab)} voci.")
    else:
        print("Estrazione del vocabolario pubblico fallita o non ha prodotto dati. La sezione 'vocabolario_pubblico' non è stata modificata.")
        # Assicuriamoci che la chiave esista comunque, anche se vuota, se non c'era prima
        if "vocabolario_pubblico" not in shard_dictionary_data:
            shard_dictionary_data["vocabolario_pubblico"] = {}
            
    # 3. Salva il dizionario di SHARD (aggiornato o solo con la struttura base)
    save_shard_dictionary(shard_dictionary_data, OUTPUT_DICT_FILE)
    
    print("Script terminato.")
