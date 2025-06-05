# json_event_logger.py
import json
import os
from datetime import datetime
import logging # Manteniamo il logging standard per eventuali errori interni al modulo stesso

# Configurazione base per il logging di questo modulo (opzionale, per debug interno)
# Se vuoi che questo modulo scriva i suoi log in un file specifico, puoi configurarlo.
# Altrimenti, se fa parte di un progetto più grande, potrebbe usare la configurazione di logging globale.
# Per ora, lo lasciamo semplice. Potremmo aggiungere un logger specifico per la classe se necessario.

class JsonEventLogger:
    def __init__(self):
        """
        Costruttore della classe. Attualmente non necessita di inizializzazioni specifiche,
        ma potrebbe essere esteso in futuro (es. per configurare percorsi di default).
        """
        pass

    def append_event_to_file(self, event_data: dict, file_path: str) -> bool:
        """
        Aggiunge un evento (dizionario) a un file JSON che contiene una lista di eventi.
        Aggiunge automaticamente un timestamp ISO 8601 all'evento.

        Args:
            event_data (dict): Il dizionario dell'evento da aggiungere.
            file_path (str): Il percorso del file JSON a cui aggiungere l'evento.

        Returns:
            bool: True se l'operazione ha successo, False altrimenti.
        """
        if not isinstance(event_data, dict):
            logging.error("[JsonEventLogger] event_data deve essere un dizionario.")
            return False
        if not isinstance(file_path, str) or not file_path.strip():
            logging.error("[JsonEventLogger] file_path deve essere una stringa non vuota.")
            return False

        # Crea una copia per non modificare l'oggetto originale passato, se non si desidera
        event_to_save = event_data.copy()
        event_to_save["timestamp"] = datetime.now().isoformat()

        events_list = []
        try:
            if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                with open(file_path, 'r', encoding='utf-8') as f:
                    try:
                        events_list = json.load(f)
                        if not isinstance(events_list, list):
                            logging.warning(f"[JsonEventLogger] Il file {file_path} non conteneva una lista JSON valida. Verrà inizializzato come nuova lista.")
                            events_list = []
                    except json.JSONDecodeError:
                        logging.warning(f"[JsonEventLogger] Errore nel decodificare JSON da {file_path}. Il file potrebbe essere corrotto. Verrà inizializzato come nuova lista.")
                        events_list = [] # Tratta come se fosse vuoto o crea una nuova lista
            # Se il file non esiste o è vuoto, events_list rimane una lista vuota.
        except IOError as e:
            logging.error(f"[JsonEventLogger] Errore I/O durante la lettura di {file_path}: {e}")
            # Nonostante l'errore di lettura, proviamo comunque a scrivere una nuova lista,
            # ma potrebbe essere preferibile restituire False qui se la lettura è critica.
            events_list = [] # Assumiamo di voler creare un nuovo file o sovrascrivere uno corrotto

        events_list.append(event_to_save)

        try:
            # Assicurati che la directory esista
            os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(events_list, f, indent=4, ensure_ascii=False)
            logging.info(f"[JsonEventLogger] Evento aggiunto con successo a {file_path}")
            return True
        except IOError as e:
            logging.error(f"[JsonEventLogger] Impossibile scrivere l'evento su {file_path}. Dettagli: {e}")
            return False
        except Exception as e_gen:
            logging.error(f"[JsonEventLogger] Errore sconosciuto durante il salvataggio su {file_path}. Dettagli: {e_gen}")
            return False

    def load_events_from_file(self, file_path: str, sort_chronologically: bool = True) -> list:
        """
        Carica una lista di eventi (dizionari) da un file JSON.

        Args:
            file_path (str): Il percorso del file JSON da cui caricare gli eventi.
            sort_chronologically (bool): Se True (default), ordina gli eventi
                                         per timestamp in ordine ascendente.

        Returns:
            list: La lista di dizionari evento, o una lista vuota in caso di errore
                  o se il file non esiste/è vuoto.
        """
        if not isinstance(file_path, str) or not file_path.strip():
            logging.error("[JsonEventLogger] file_path deve essere una stringa non vuota per load_events_from_file.")
            return []

        if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
            logging.info(f"[JsonEventLogger] Il file {file_path} non esiste o è vuoto. Restituisco lista vuota.")
            return []

        loaded_events = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                loaded_events = json.load(f)
                if not isinstance(loaded_events, list):
                    logging.warning(f"[JsonEventLogger] Il file {file_path} non conteneva una lista JSON valida. Restituisco lista vuota.")
                    return []
        except json.JSONDecodeError:
            logging.warning(f"[JsonEventLogger] Errore nel decodificare JSON da {file_path}. Il file potrebbe essere corrotto. Restituisco lista vuota.")
            return []
        except IOError as e:
            logging.error(f"[JsonEventLogger] Errore I/O durante il caricamento da {file_path}: {e}")
            return []
        except Exception as e_gen:
            logging.error(f"[JsonEventLogger] Errore sconosciuto durante il caricamento da {file_path}. Dettagli: {e_gen}")
            return []

        if sort_chronologically:
            try:
                # Filtra solo gli elementi che sono dizionari e hanno un timestamp
                items_to_sort = [item for item in loaded_events if isinstance(item, dict) and "timestamp" in item]
                
                # Ordina. Le stringhe ISO 8601 si ordinano correttamente lessicograficamente.
                items_to_sort.sort(key=lambda item: item.get("timestamp", ""))
                
                # Se non tutti gli items erano ordinabili, potremmo decidere se restituire
                # solo quelli ordinati o la lista originale. Per ora, restituiamo quelli ordinati.
                # Se la lista originale conteneva items non dizionari o senza timestamp,
                # items_to_sort li avrà esclusi. Se vuoi mantenere tutti gli items e ordinare
                # solo quelli possibili, la logica dovrebbe essere diversa.
                # Per semplicità, assumiamo che la lista contenga oggetti evento consistenti.
                return items_to_sort
            except Exception as e_sort:
                logging.warning(f"[JsonEventLogger] Errore durante l'ordinamento degli eventi da {file_path}: {e_sort}. Restituisco lista non ordinata (o parzialmente processata).")
                return loaded_events # Restituisce la lista caricata ma non (completamente) ordinata
        
        return loaded_events

# --- Esempio di utilizzo (puoi decommentarlo per testare questo modulo da solo) ---
if __name__ == '__main__':
    # Configura un logging di base per vedere gli output del logger della classe durante il test
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    logger_instance = JsonEventLogger()
    log_file = "SHARD_CORE/sandbox/test_event_log.json" # Assicurati che la cartella esista o che la funzione la crei

    # Pulisci il file di log precedente se esiste, per test puliti
    if os.path.exists(log_file):
        os.remove(log_file)

    print(f"\n--- Test di 'append_event_to_file' ---")
    evento1 = {"azione": "login", "utente": "Andrea", "successo": True}
    if logger_instance.append_event_to_file(evento1, log_file):
        print(f"Evento 1 aggiunto a {log_file}")
    
    import time # Per avere timestamp diversi
    time.sleep(0.1)

    evento2 = {"azione": "query", "dettaglio": "chi sei?", "risposta_corta": "Sono SHARD..."}
    if logger_instance.append_event_to_file(evento2, log_file):
        print(f"Evento 2 aggiunto a {log_file}")

    time.sleep(0.1)
    evento_malformato = "questa non è un dizionario"
    if not logger_instance.append_event_to_file(evento_malformato, log_file):
        print(f"Correttamente fallito l'aggiunta di un evento non dizionario.")


    print(f"\n--- Test di 'load_events_from_file' (ordinato) ---")
    eventi_caricati_ordinati = logger_instance.load_events_from_file(log_file, sort_chronologically=True)
    if eventi_caricati_ordinati:
        print(f"Caricati {len(eventi_caricati_ordinati)} eventi (ordinati):")
        for evento in eventi_caricati_ordinati:
            print(f"  - {evento}")
    else:
        print(f"Nessun evento caricato da {log_file} o file non valido.")

    # Test di caricamento da file non esistente
    print(f"\n--- Test di 'load_events_from_file' (file non esistente) ---")
    eventi_non_esistenti = logger_instance.load_events_from_file("file_che_non_esiste.json")
    print(f"Eventi da file non esistente (dovrebbe essere lista vuota): {eventi_non_esistenti}")

    # Test di append su un file JSON che inizia non essendo una lista
    if os.path.exists("malformed_log.json"): os.remove("malformed_log.json")
    with open("malformed_log.json", "w") as f: f.write('{"non_una_lista": true}')
    print(f"\n--- Test di 'append_event_to_file' su file JSON non-lista ---")
    evento3 = {"azione": "test_sovrascrittura", "dettaglio": "il file precedente non era una lista"}
    if logger_instance.append_event_to_file(evento3, "malformed_log.json"):
        print(f"Evento 3 aggiunto a malformed_log.json (il file dovrebbe essere stato resettato a una lista)")
        eventi_da_malformed = logger_instance.load_events_from_file("malformed_log.json")
        print(f"Contenuto di malformed_log.json: {eventi_da_malformed}")
    if os.path.exists("malformed_log.json"): os.remove("malformed_log.json") # Pulizia
