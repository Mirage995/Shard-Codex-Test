# ShardCore/utils/knowledge_parser.py
import json
import re
import os

DEFAULT_DIZIONARIO_PATH = "dizionario_nostro.json" 

def load_knowledge(path_to_dict_file: str):
    """
    Carica il file JSON del dizionario di SHARD.
    path_to_dict_file: DEVE essere il percorso corretto e completo al file.
    """
    try:
        with open(path_to_dict_file, 'r', encoding='utf-8') as file:
            knowledge = json.load(file)
            # Assicuriamoci che le sezioni principali esistano per evitare KeyError dopo
            knowledge.setdefault("vocabolario_pubblico", {})
            knowledge.setdefault("glossario", {})
            knowledge.setdefault("memoria", {})
            knowledge.setdefault("conoscenza", {})
            print(f"INFO [knowledge_parser.load_knowledge]: Dizionario caricato con successo da: {path_to_dict_file}")
            return knowledge
    except FileNotFoundError:
        print(f"ERRORE [knowledge_parser.load_knowledge]: File dizionario non trovato: {path_to_dict_file}")
        return {"vocabolario_pubblico": {}, "glossario": {}, "memoria": {}, "conoscenza": {}}
    except json.JSONDecodeError:
        print(f"ERRORE [knowledge_parser.load_knowledge]: Errore nel decodificare JSON dal file: {path_to_dict_file}")
        return {"vocabolario_pubblico": {}, "glossario": {}, "memoria": {}, "conoscenza": {}}
    except Exception as e:
        print(f"ERRORE [knowledge_parser.load_knowledge]: Errore imprevisto durante il caricamento del dizionario ({path_to_dict_file}): {e}")
        return {"vocabolario_pubblico": {}, "glossario": {}, "memoria": {}, "conoscenza": {}}

def get_definition(question: str, knowledge: dict) -> str | None:
    """
    Cerca una definizione nel vocabolario_pubblico e nel glossario.
    Riconosce pattern come "Cosa significa X?", "Definizione di X", ecc.
    """
    question_lower = question.lower()
    
    patterns = [
        r"^(?:cosa significa|qual è il significato di|significato di|definizione di|spiegami(?: il termine)?)\s+['\"]?(.*?)['\"]?\??$",
        r"^(?:cos'è|cos è|chi è)\s+['\"]?(.*?)['\"]?\??$"
    ]
    
    term_to_define = None
    for pattern in patterns:
        match = re.search(pattern, question_lower, re.IGNORECASE)
        if match:
            term_to_define = match.group(1).strip()
            if term_to_define: 
                break 

    if term_to_define:
        glossario_section = knowledge.get("glossario", {})
        for key, value in glossario_section.items():
            if key.lower() == term_to_define: # Confronto case-insensitive per il termine estratto
                return f"[Dal Glossario]: {key}: {value}"
        
        vocabolario_section = knowledge.get("vocabolario_pubblico", {})
        for key, value in vocabolario_section.items():
            if key.lower() == term_to_define: # Confronto case-insensitive per il termine estratto
                return value 
    return None

def improved_generic_search(question: str, knowledge_section_name: str, knowledge_base_dict: dict) -> str | None:
    """
    Cerca se qualche CHIAVE della sezione specificata del dizionario è menzionata nella domanda,
    come parola/frase intera. Restituisce il valore della chiave più lunga trovata.
    """
    section = knowledge_base_dict.get(knowledge_section_name, {})
    if not isinstance(section, dict) or not section : 
        return None

    question_lower = question.lower()
    
    best_match_value = None
    len_longest_key_match = 0

    for key, value in section.items():
        key_lower = key.lower()
        try:
            # Costruisce un pattern regex per cercare la chiave come parola/frase intera
            # re.escape gestisce eventuali caratteri speciali nella chiave
            # \b assicura che ci siano confini di parola attorno alla chiave
            pattern = r'\b' + re.escape(key_lower) + r'\b'
            if re.search(pattern, question_lower, re.IGNORECASE): # Aggiunto re.IGNORECASE
                if len(key_lower) > len_longest_key_match:
                    len_longest_key_match = len(key_lower)
                    best_match_value = f"[Dalla sezione '{knowledge_section_name}']: \"{key}\": {value}"
        except re.error:
            # Fallback di emergenza se la chiave crea un pattern regex non valido (molto raro con re.escape)
            # print(f"DEBUG: Errore Regex con la chiave '{key_lower}', uso fallback a semplice 'in'.")
            if key_lower in question_lower: 
                if len(key_lower) > len_longest_key_match:
                    # Applica questo fallback solo se non avevamo già un match migliore con regex
                    if len_longest_key_match == 0: 
                        len_longest_key_match = len(key_lower)
                        best_match_value = f"[Dalla sezione '{knowledge_section_name}' (fallback match)]: \"{key}\": {value}"
    
    return best_match_value

# --- PER TESTARE QUESTO MODULO DIRETTAMENTE ---
if __name__ == "__main__":
    print("Avvio Test del Knowledge Parser...")

    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        if os.path.basename(script_dir) == "utils":
            shard_core_dir = os.path.dirname(script_dir)
        else: 
            shard_core_dir = script_dir
        dizionario_target_path = os.path.join(shard_core_dir, "dizionario_nostro.json")
        dizionario_target_path = os.path.normpath(dizionario_target_path)
        print(f"DEBUG [knowledge_parser.__main__]: Tentativo di caricare il dizionario da: {dizionario_target_path}")
    except NameError: 
        dizionario_target_path = DEFAULT_DIZIONARIO_PATH 
        print(f"DEBUG [knowledge_parser.__main__]: __file__ non definito, uso path di default relativo alla CWD: {dizionario_target_path}")

    knowledge_base = load_knowledge(dizionario_target_path)

    if not (knowledge_base.get("vocabolario_pubblico") or \
            knowledge_base.get("glossario") or \
            knowledge_base.get("memoria") or \
            knowledge_base.get("conoscenza") ) and \
       any(knowledge_base.get(key, {}) for key in ["vocabolario_pubblico", "glossario", "memoria", "conoscenza"]):
            print(f"ATTENZIONE [knowledge_parser.__main__]: Dizionario '{dizionario_target_path}' caricato, ma le sezioni chiave sono vuote o non contengono dati. I test potrebbero non trovare risultati.")
    
    print("\n--- Test get_definition ---")
    test_questions_def = [
        "Cosa significa casa?",
        "Definizione di albero",
        "Significato di Frammento", 
        "cos'è algoritmo"
    ]
    for q in test_questions_def:
        print(f"\nDomanda: {q}")
        answer = get_definition(q, knowledge_base)
        print(f"Risposta: {answer if answer else 'Non trovata da get_definition.'}")

    print("\n--- Test improved_generic_search ---")
    # Per questi test, assicurati che il tuo dizionario_nostro.json contenga chiavi corrispondenti
    # Esempio per dizionario_nostro.json (da aggiungere se non presenti):
    # "conoscenza": { 
    #   "trascendenza": "Superamento dei limiti della percezione materiale.",
    #   "IA_forte": "Un'intelligenza artificiale con capacità cognitive uguali o superiori a quelle umane.",
    #   "IA": "Intelligenza Artificiale in generale." 
    # },
    # "memoria": { 
    #   "evento attivazione shard": "SHARD è stato attivato il 16 Maggio 2025.",
    #   "cena importante venerdì scorso": "Andrea è andato a cena da 'Il Bersagliere' (inventato da SHARD!)"
    # }
    test_generic_questions = [
        ("Parlami un po' della trascendenza", "conoscenza"),
        ("Cosa sai sulla IA_forte?", "conoscenza"),
        ("Vorrei sapere della IA in generale e anche della IA_forte", "conoscenza"), 
        ("Ricordi qualcosa sulla cena importante venerdì scorso?", "memoria"),
        ("Cosa è successo durante l'evento attivazione shard?", "memoria"),
        ("Parlami di un evento importante", "memoria"),
        ("Qual è la capitale dell'Italia?", "conoscenza") # Per testare il falso positivo con "IA"
    ]

    for q_text, section_name in test_generic_questions:
        print(f"\nDomanda: {q_text} (Sezione testata: {section_name})")
        answer = improved_generic_search(q_text, section_name, knowledge_base)
        print(f"Risposta: {answer if answer else 'Non trovata da improved_generic_search.'}")
    
    print("\nTest del Knowledge Parser terminato.")
