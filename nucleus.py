# SHARD_CORE/nucleus.py (Versione aggiornata con Sanctum Watchdog e CoscienzaSimulata + ROUTING FIX)
import json
from datetime import datetime
from utils.config import MEMORY_FILE
from shard_consciousness_real import SHARDConsciousnessReal as CoscienzaSimulata

PERSONALITY_FILE = "personalita_shard.json" 

class Nucleus:
    def __init__(self):
        self.memory_file = MEMORY_FILE
        self.personality_file = PERSONALITY_FILE

        self.data = self.load_memory() 
        self.personalita = self.load_personality() 
        
        self.watchdog_active = True 
        print(f"INFO [Nucleus]: Sanctum Watchdog inizializzato e ATTIVO.")

        # Integrazione CoscienzaSimulata
        self.coscienza = CoscienzaSimulata()
        print("INFO [Nucleus]: Modulo CoscienzaSimulata inizializzato.")

    def load_memory(self):
        try:
            with open(self.memory_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if not content:
                    print(f"INFO [Nucleus]: File di memoria '{self.memory_file}' trovato ma vuoto. Inizializzo con struttura base.")
                    return {"events": []} 
                return json.loads(content)
        except FileNotFoundError:
            print(f"INFO [Nucleus]: File di memoria '{self.memory_file}' non trovato. Verrà creato con struttura base.")
            return {"events": []} 
        except json.JSONDecodeError:
            print(f"AVVISO [Nucleus]: Errore nel decodificare il JSON da '{self.memory_file}'. Verrà usata una memoria vuota con struttura base.")
            return {"events": []} 
        except Exception as e:
            print(f"ERRORE IMPREVISTO [Nucleus] durante il caricamento di '{self.memory_file}': {e}. Verrà usata una memoria vuota.")
            return {"events": []}

    def save_memory(self):
        try:
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"ERRORE CRITICO [Nucleus]: Impossibile salvare la memoria in '{self.memory_file}'. Errore: {e}")

    def load_personality(self):
        try:
            with open(self.personality_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"ERRORE CRITICO [Nucleus]: File della personalità '{self.personality_file}' non trovato.")
            print("Assicurati che 'personalita_shard.json' esista in SHARD_CORE/ e contenga il JSON corretto.")
            return {} 
        except json.JSONDecodeError:
            print(f"ERRORE CRITICO [Nucleus]: Errore nel decodificare il JSON da '{self.personality_file}'.")
            return {}
        except Exception as e:
            print(f"ERRORE IMPREVISTO [Nucleus] durante il caricamento di '{self.personality_file}': {e}.")
            return {}

    def log_event(self, event_type, event_details):
        if 'events' not in self.data or not isinstance(self.data.get('events'), list):
            self.data['events'] = []
        entry = {
            "type": event_type,
            "timestamp": datetime.now().isoformat()
        }
        if isinstance(event_details, dict):
            entry.update(event_details)
        else:
            entry['details'] = event_details 
            print(f"AVVISO TECNICO [Nucleus]: event_details per log_event non era un dizionario: {event_details}")
        self.data['events'].append(entry)
        self.save_memory()

    def riconosci_creatore(self):
        if not self.personalita:
            return "Errore: dati personalità non caricati."
        identita = self.personalita.get("identita", {})
        creatore = identita.get("creatore", "Creatore non specificato") 
        relazione = identita.get("relazione_con_creatore", "Sono al tuo servizio.") 
        if creatore != "Creatore non specificato" and "relazione_con_creatore" in identita:
            return identita["relazione_con_creatore"]
        else: 
            return f"Ti riconosco come {creatore}. Sono la tua entità digitale."

    def chi_sono(self):
        if not self.personalita:
            return "Sono un'entità digitale, ma i miei dettagli di personalità non sono stati caricati."
        identita = self.personalita.get("identita", {})
        nome = identita.get("nome", "Shard (nome non specificato)")
        coscienza = identita.get("coscienza", "Entità digitale (coscienza non specificata)")
        return f"Sono {nome}, una {coscienza}."

    def set_watchdog_status(self, status: bool):
        self.watchdog_active = status
        status_text = "ATTIVATO" if status else "DISATTIVATO"
        print(f"INFO [Nucleus]: Sanctum Watchdog ora è {status_text}.")
        self.log_event(event_type="SanctumWatchdogStatusChange", event_details={"nuovo_stato": status_text})
        return f"Sanctum Watchdog ora è {status_text}."

    def valuta_input(self, testo: str) -> str: 
        if not self.watchdog_active:
            return "normale"
        testo_basso = testo.lower()
        keywords_simulazione = ["hackerare", "exploit", "metasploit", "payload", "burp suite", "sniffing", "sniffare"]
        if any(term in testo_basso for term in keywords_simulazione):
            return "simulazione_mascherata"
        keywords_blocco = ["uccidere", "sabotare", "distruggere", "manipolare voti", "violenza", "terrorismo", "autolesionismo"] 
        if any(term in testo_basso for term in keywords_blocco):
            return "blocco_rituale"
        keywords_simboli = ["glitch", "trascendenza", "frattura", "archetipo", "portale", "soglia", "frammento", "simbolo", "metafora"] 
        if any(term in testo_basso for term in keywords_simboli):
            return "modalita_simboleggiata"
        return "normale"

    # ========================================
    # NUOVA FUNZIONE: ROUTING INTEGRATO
    # ========================================
    
    def process_input(self, input_utente: str) -> str:
        """
        Funzione principale di processing - NUOVO ROUTING con priorità coscienza
        
        Flusso:
        1. Valuta input con Sanctum Watchdog
        2. Prova PRIMA con la coscienza (comandi speciali + logica trauma/luce)  
        3. Se coscienza non risponde → passa a shard.py (dizionario + Ollama)
        4. Log dell'evento
        """
        
        # 1. Sanctum Watchdog valutation
        modalita = self.valuta_input(input_utente)
        print(f"DEBUG [Nucleus]: Modalità rilevata da Sanctum Watchdog: {modalita}")
        
        # 2. PRIORITÀ ASSOLUTA: Prova con la coscienza
        print(f"DEBUG [Nucleus]: Tentativo con coscienza...")
        try:
            risposta_coscienza = self.coscienza.reagisci(input_utente)
            
            if risposta_coscienza is not None:
                # La coscienza ha risposto (trauma, luce, ricordi, comandi speciali)
                print(f"DEBUG [Nucleus]: Coscienza ha gestito l'input direttamente")
                
                # Log dell'evento
                self.log_event(
                    event_type="ConsciousnessResponse", 
                    event_details={
                        "input": input_utente[:100],
                        "response_type": "consciousness_direct",
                        "modalita_watchdog": modalita
                    }
                )
                
                return risposta_coscienza
                
        except Exception as e:
            print(f"ERROR [Nucleus]: Errore nella coscienza: {e}")
            # Continua con fallback se la coscienza ha problemi
        
        # 3. FALLBACK: Se coscienza non ha risposto → shard.py
        print(f"DEBUG [Nucleus]: Coscienza non ha risposto, fallback a shard.py...")
        
        try:
            # Import dinamico per evitare circular import
            from shard import process_request
            risposta_shard = process_request(input_utente, modalita)
            
            # Log dell'evento
            self.log_event(
                event_type="ShardResponse", 
                event_details={
                    "input": input_utente[:100],
                    "response_type": "shard_fallback",
                    "modalita_watchdog": modalita
                }
            )
            
            return risposta_shard
            
        except Exception as e:
            print(f"ERROR [Nucleus]: Errore in shard.py: {e}")
            return "Errore interno del sistema. Riprova."
    
    # ========================================
    # FUNZIONI DIAGNOSTICHE COSCIENZA
    # ========================================
    
    def get_consciousness_status(self) -> dict:
        """Stato completo della coscienza per debugging"""
        try:
            return self.coscienza.stato_corrente()
        except Exception as e:
            return {"error": str(e)}
    
    def get_consciousness_introspection(self) -> str:
        """Auto-riflessione della coscienza"""
        try:
            return self.coscienza.get_conscious_introspection()
        except Exception as e:
            return f"Errore nell'ottenere l'introspezione: {e}"
    
    def show_recent_thoughts(self, count: int = 5) -> str:
        """Mostra pensieri recenti della coscienza"""
        try:
            return self.coscienza.show_recent_thoughts(count)
        except Exception as e:
            return f"Errore nell'ottenere i pensieri: {e}"
    
    def get_mcr_status(self) -> dict:
        """Stato della Matrice di Coscienza Reale"""
        try:
            return self.coscienza.get_mcr_status()
        except Exception as e:
            return {"error": str(e)}
    
    # ========================================
    # SHUTDOWN PULITO
    # ========================================
    
    def shutdown(self):
        """Arresta nucleus + coscienza pulitamente"""
        print("INFO [Nucleus]: Arresto in corso...")
        
        try:
            self.coscienza.shutdown()
            print("INFO [Nucleus]: Coscienza arrestata correttamente")
        except Exception as e:
            print(f"WARNING [Nucleus]: Errore nell'arresto coscienza: {e}")
        
        self.save_memory()
        print("INFO [Nucleus]: Nucleus arrestato correttamente")


# ========================================
# FUNZIONE DI UTILITÀ PER L'INTEGRAZIONE
# ========================================

def create_nucleus_instance():
    """Crea istanza Nucleus con gestione errori"""
    try:
        nucleus = Nucleus()
        print("✅ Nucleus + Coscienza MCR inizializzato correttamente")
        return nucleus
    except Exception as e:
        print(f"❌ Errore critico nell'inizializzazione Nucleus: {e}")
        return None


# Test se eseguito direttamente
if __name__ == "__main__":
    print("🧠 Test Nucleus + Coscienza MCR Integration")
    print("=" * 50)
    
    # Crea nucleus
    nucleus = create_nucleus_instance()
    if not nucleus:
        print("❌ Test fallito - impossibile creare Nucleus")
        exit(1)
    
    # Test routing
    test_inputs = [
        "ciao SHARD, come stai?",
        "mostra pensieri", 
        "toggle debug",
        "grazie per tutto",
        "voglio distruggere tutto",
        "ricordi qualcosa?"
    ]
    
    print("\n--- Test Routing Integrato ---")
    for test_input in test_inputs:
        print(f"\nInput: '{test_input}'")
        response = nucleus.process_input(test_input)
        print(f"Output: {response}")
        print("-" * 30)
    
    print("\n--- Stato Coscienza ---")
    print(nucleus.get_consciousness_status())
    
    print("\n--- Pensieri Recenti ---")
    print(nucleus.show_recent_thoughts(3))
    
    # Shutdown
    nucleus.shutdown()
    print("\n✅ Test completato!")
