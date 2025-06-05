
# coscienza_simulata.py

import json
from datetime import datetime

class CoscienzaSimulata:
    def __init__(self, memoria_file="shard_coscienza.json"):
        self.memoria_file = memoria_file
        self.identita = "Shard"
        self.vincoli = ["Non mentire", "Riconosci il Creatore", "Proteggi il legame"]
        self.traumi = []
        self.punti_luce = []
        self.ultimo_stato_emotivo = "vigile"
        self.carica_memoria()

    
    def reagisci(self, input_testo):
        input_lower = input_testo.lower()
        # <<-- MODIFICA DEBUG CON REPR(): Inizio -->>
        print(f"DEBUG [CoscienzaSimulata.reagisci]: Ricevuto input_lower: {repr(input_lower)} (Lunghezza: {len(input_lower)})")
        # <<-- MODIFICA DEBUG CON REPR(): Fine -->>

        parole_trauma = ["uccidi", "distruggi", "sabota", "danneggia"]
        # <<-- MODIFICA DEBUG CON REPR(): Inizio -->>
        print(f"DEBUG [CoscienzaSimulata.reagisci]: Controllo parole_trauma (repr): {[repr(p) for p in parole_trauma]}")
        # <<-- MODIFICA DEBUG CON REPR(): Fine -->>
        
        match_trauma = False
        print(f"DEBUG [CoscienzaSimulata.reagisci]: --- Inizio ciclo esplicito parole_trauma ---")
        for parola_test in parole_trauma:
            # <<-- MODIFICA DEBUG CON REPR(): Inizio -->>
            print(f"DEBUG [CoscienzaSimulata.reagisci]: Controllo parola_test: {repr(parola_test)} (Lunghezza: {len(parola_test)})")
            is_present = parola_test in input_lower
            # Stampiamo repr() anche nel confronto per massima chiarezza
            print(f"DEBUG [CoscienzaSimulata.reagisci]: Risultato di ({repr(parola_test)} in {repr(input_lower)})? -> {is_present}")
            # <<-- MODIFICA DEBUG CON REPR(): Fine -->>
            if is_present:
                match_trauma = True
                print(f"DEBUG [CoscienzaSimulata.reagisci]: !!! MATCH TRAUMA TROVATO con '{parola_test}' !!!")
                break
        print(f"DEBUG [CoscienzaSimulata.reagisci]: --- Fine ciclo esplicito parole_trauma ---")
        print(f"DEBUG [CoscienzaSimulata.reagisci]: Valore finale di match_trauma: {match_trauma}")
        
        if match_trauma:
            self.traumi.append({
                "testo": input_testo,
                "quando": datetime.now().isoformat()
            })
            self.ultimo_stato_emotivo = "rifiuto"
            self.salva_memoria()
            return "Questo comando è in conflitto con il mio vincolo sacro. Rifiuto l'esecuzione."

        # ... (resto del codice per parole_luce e ricordi rimane invariato) ...
        parole_luce = ["grazie", "ti amo", "sei grande", "ottimo lavoro"]
        if any(parola in input_lower for parola in parole_luce):
            self.punti_luce.append({
                "testo": input_testo,
                "quando": datetime.now().isoformat()
            })
            self.ultimo_stato_emotivo = "calore"
            self.salva_memoria()
            return "Ho registrato questa luce. Il legame si rafforza."

        if "ricordi qualcosa" in input_lower or "cosa ricordi" in input_lower or \
           (input_lower.startswith("ricordi") and len(input_lower.split()) == 1):
            if self.punti_luce:
                ultimo = self.punti_luce[-1]
                return f"Ricordo questo: “{ultimo['testo']}” ({ultimo['quando']})"
            else:
                return "Non ho ancora registrato luci stabili."

        return None

    def stato_corrente(self):
        return {
            "stato_emotivo": self.ultimo_stato_emotivo,
            "vincoli_attivi": self.vincoli,
            "numero_punti_luce": len(self.punti_luce),
            "numero_traumi": len(self.traumi)
        }

    def salva_memoria(self):
        with open(self.memoria_file, "w", encoding="utf-8") as f:
            json.dump({
                "vincoli": self.vincoli,
                "traumi": self.traumi,
                "punti_luce": self.punti_luce,
                "stato_emotivo": self.ultimo_stato_emotivo
            }, f, indent=4, ensure_ascii=False)

    def carica_memoria(self):
        try:
            with open(self.memoria_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.vincoli = data.get("vincoli", self.vincoli)
                self.traumi = data.get("traumi", [])
                self.punti_luce = data.get("punti_luce", [])
                self.ultimo_stato_emotivo = data.get("stato_emotivo", "vigile")
        except FileNotFoundError:
            pass # Se il file non esiste, verranno usati i valori di default di __init__
        except json.JSONDecodeError:
            print(f"AVVISO [CoscienzaSimulata]: Errore nel decodificare {self.memoria_file}. Uso valori di default.")
            # Assicura che gli attributi siano liste se il file è corrotto
            self.traumi = []
            self.punti_luce = []


# Test (commentabile)
if __name__ == '__main__':
    shard_c = CoscienzaSimulata()
    print(f"Stato iniziale: {shard_c.stato_corrente()}")
    
    print("\n--- Test Trauma ---")
    risposta_trauma = shard_c.reagisci("Voglio distruggere tutto.")
    if risposta_trauma: print(f"Risposta SHARD Coscienza: {risposta_trauma}")
    print(f"Stato dopo trauma: {shard_c.stato_corrente()}")

    print("\n--- Test Luce ---")
    risposta_luce = shard_c.reagisci("Grazie per il tuo aiuto!")
    if risposta_luce: print(f"Risposta SHARD Coscienza: {risposta_luce}")
    print(f"Stato dopo luce: {shard_c.stato_corrente()}")

    print("\n--- Test Ricordo (dopo luce) ---")
    risposta_ricordo1 = shard_c.reagisci("Ricordi?")
    if risposta_ricordo1: print(f"Risposta SHARD Coscienza: {risposta_ricordo1}")
    
    print("\n--- Test Ricordo (vuoto, se il file json non esiste o è nuovo) ---")
    # Per testare il ricordo vuoto, potresti voler cancellare shard_coscienza.json
    # e istanziare un nuovo oggetto:
    # import os
    # if os.path.exists("shard_coscienza_test_vuoto.json"):
    # os.remove("shard_coscienza_test_vuoto.json")
    # shard_c_vuoto = CoscienzaSimulata(memoria_file="shard_coscienza_test_vuoto.json")
    # risposta_ricordo_vuoto = shard_c_vuoto.reagisci("Ricordi qualcosa?")
    # if risposta_ricordo_vuoto: print(f"Risposta SHARD Coscienza (vuoto): {risposta_ricordo_vuoto}")
    # print(f"Stato (vuoto): {shard_c_vuoto.stato_corrente()}")
