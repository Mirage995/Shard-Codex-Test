# SHARD_CORE/autoscribe_utils.py
import os
from pathlib import Path
import re # Importiamo 're' per la sanificazione del nome del modulo

# Definiamo il percorso base di SHARD_CORE.
# Questo approccio assume che la cartella SHARD_CORE sia nella directory home dell'utente.
# Se hai SHARD_CORE in un percorso diverso, dovrai aggiustare questa riga.
SHARD_CORE_BASE_PATH = Path.home() / "SHARD_CORE"
# In alternativa, un modo più robusto se questo file fosse sempre eseguito
# da uno script che si trova in SHARD_CORE o in una sua sottocartella:
# try:
#     # Tenta di ottenere il percorso dello script principale se shard.py lo definisce
#     from . import SHARD_MAIN_DIR # Immaginando una variabile SHARD_MAIN_DIR in __init__.py o config
#     SHARD_CORE_BASE_PATH = Path(SHARD_MAIN_DIR)
# except ImportError:
#     # Fallback se SHARD_MAIN_DIR non è definito o siamo in esecuzione diretta
#     # Questo potrebbe non essere sempre affidabile se lo script viene chiamato da posti diversi
#     # print("Attenzione: SHARD_CORE_BASE_PATH potrebbe non essere corretto.")
#     SHARD_CORE_BASE_PATH = Path.cwd() # Usa la Current Working Directory come base
#     if SHARD_CORE_BASE_PATH.name != "SHARD_CORE":
#          # Se cwd non è SHARD_CORE, proviamo la home come da PDF
#          SHARD_CORE_BASE_PATH = Path.home() / "SHARD_CORE"


def salva_modulo_in_sandbox(nome_modulo: str, codice_modulo: str) -> str | None:
    """
    Salva il codice fornito come un modulo Python nella sandbox di SHARD.

    Args:
        nome_modulo (str): Il nome desiderato per il modulo (es. "mio_nuovo_helper").
                           L'estensione '.py' verrà aggiunta automaticamente se non presente.
        codice_modulo (str): Il codice Python da scrivere nel file.

    Returns:
        str | None: Il percorso completo al file salvato se ha successo, None altrimenti.
    """
    try:
        # Sanificazione di base del nome del modulo per renderlo un nome file Python valido
        # Rimuovi l'estensione .py se presente, la aggiungeremo noi
        if nome_modulo.lower().endswith(".py"):
            nome_modulo = nome_modulo[:-3]

        # Sostituisci caratteri non validi per un nome di modulo/file Python con underscore
        # Un nome di modulo dovrebbe essere un identificatore Python valido.
        safe_nome_modulo = re.sub(r'\W|^(?=\d)', '_', nome_modulo)
        if not safe_nome_modulo: # Se diventa vuoto dopo la sanificazione (es. solo caratteri speciali)
            safe_nome_modulo = "modulo_generato_da_shard"

        # Se il nome originale era diverso da quello sanificato, informa l'utente
        if nome_modulo != safe_nome_modulo:
            print(f"INFO: Il nome modulo '{nome_modulo}' è stato normalizzato in '{safe_nome_modulo}' per la validità del file.")

        nome_file_python = f"{safe_nome_modulo}.py"

        sandbox_dir = SHARD_CORE_BASE_PATH / "sandbox"
        # Crea la directory sandbox e le directory genitore necessarie, se non esistono.
        sandbox_dir.mkdir(parents=True, exist_ok=True) 

        file_modulo_path = sandbox_dir / nome_file_python

        with open(file_modulo_path, "w", encoding="utf-8") as f:
            f.write(codice_modulo)

        full_path_str = str(file_modulo_path.resolve()) # Ottieni il percorso assoluto
        print(f"Modulo '{nome_file_python}' salvato con successo in: {full_path_str}")
        return full_path_str
    except Exception as e:
        print(f"ERRORE: Impossibile salvare il modulo '{nome_modulo}' nella sandbox. Dettagli: {e}")
        import traceback
        traceback.print_exc() # Stampa il traceback completo per debug
        return None

# --- Esempio di utilizzo (puoi decommentarlo per testare questo script da solo) ---
# if __name__ == '__main__':
#     print(f"Percorso base SHARD_CORE rilevato: {SHARD_CORE_BASE_PATH}")
#     codice_esempio = """
# # Modulo di esempio generato
# def saluta():
#     print("Ciao dalla sandbox di SHARD!")
# 
# if __name__ == '__main__':
#     saluta()
# """
#     percorso_salvato = salva_modulo_in_sandbox("mio_primo_modulo_sandbox", codice_esempio)
#     if percorso_salvato:
#         print(f"File di test salvato in: {percorso_salvato}")

#     percorso_salvato_nome_strano = salva_modulo_in_sandbox("123 Nome con Spazi & Simboli!", codice_esempio)
#     if percorso_salvato_nome_strano:
#         print(f"File di test con nome strano salvato in: {percorso_salvato_nome_strano}")
