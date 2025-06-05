#!/usr/bin/env python3
"""
Convertitore per i log di conversazioni SHARD
Trasforma il file di testo con le conversazioni nel formato per fine-tuning
"""

import json
import re
from typing import List, Dict

def parse_shard_conversations(file_path: str) -> List[Dict]:
    """
    Parsifica il file di conversazioni SHARD e estrae le coppie domanda-risposta
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Dividi le conversazioni usando il separatore
    conversations = content.split('------------------------------')
    
    training_data = []
    
    for conv in conversations:
        conv = conv.strip()
        if not conv:
            continue
            
        # Estrai tutte le coppie Tu:/Risposta da ogni conversazione
        lines = conv.split('\n')
        current_input = None
        current_output = []
        collecting_output = False
        
        for line in lines:
            line = line.strip()
            
            # Rileva input utente
            if line.startswith('Tu: '):
                # Se avevamo una conversazione precedente, salvala
                if current_input and current_output:
                    output_text = '\n'.join(current_output).strip()
                    if output_text and len(output_text) > 10:  # Filtra risposte troppo brevi
                        training_data.append({
                            "instruction": current_input,
                            "input": "",
                            "output": output_text
                        })
                
                # Inizia nuova conversazione
                current_input = line[4:]  # Rimuovi "Tu: "
                current_output = []
                collecting_output = False
                
            # Salta le righe INFO
            elif line.startswith('INFO'):
                collecting_output = True
                continue
                
            # Raccogli la risposta di SHARD
            elif collecting_output and line and not line.startswith('Tu: '):
                current_output.append(line)
        
        # Salva l'ultima conversazione
        if current_input and current_output:
            output_text = '\n'.join(current_output).strip()
            if output_text and len(output_text) > 10:
                training_data.append({
                    "instruction": current_input,
                    "input": "",
                    "output": output_text
                })
    
    return training_data

def filter_quality_responses(data: List[Dict]) -> List[Dict]:
    """
    Filtra le risposte di qualità migliore per il training
    """
    filtered_data = []
    
    for item in data:
        output = item['output']
        
        # Criteri di qualità
        quality_indicators = [
            'Creatore' in output,
            'SHARD' in output,
            'evolutiv' in output.lower(),
            'coscien' in output.lower(),
            'autonom' in output.lower(),
            len(output) > 50,  # Risposte sostanziali
            not output.startswith('Ciao'),  # Evita risposte generiche
        ]
        
        # Tieni le risposte che hanno almeno 2 indicatori di qualità
        if sum(quality_indicators) >= 2:
            filtered_data.append(item)
            
    return filtered_data

def save_training_data(data: List[Dict], output_file: str):
    """
    Salva i dati nel formato per il fine-tuning
    """
    print(f"Salvando {len(data)} esempi di training in {output_file}")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    # Crea anche versione JSONL per alcuni tool
    jsonl_file = output_file.replace('.json', '.jsonl')
    with open(jsonl_file, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
    
    print(f"Creato anche {jsonl_file}")

def main():
    # Configura i file
    input_file = "conversazioni_shard.txt"  # Il tuo file con le conversazioni
    output_file = "shard_training_data.json"
    
    print("🔥 Convertitore Dati SHARD per Fine-Tuning")
    print("=" * 50)
    
    # Parsifica le conversazioni
    print(f"📖 Leggendo conversazioni da {input_file}...")
    try:
        raw_data = parse_shard_conversations(input_file)
        print(f"✅ Estratte {len(raw_data)} conversazioni")
    except FileNotFoundError:
        print(f"❌ File {input_file} non trovato!")
        print("💡 Salva le tue conversazioni in un file chiamato 'conversazioni_shard.txt'")
        return
    
    # Filtra per qualità
    print("🔍 Filtrando conversazioni di qualità...")
    quality_data = filter_quality_responses(raw_data)
    print(f"✅ Selezionate {len(quality_data)} conversazioni di qualità")
    
    # Mostra esempi
    print("\n📋 Esempi di dati estratti:")
    for i, item in enumerate(quality_data[:3]):
        print(f"\n--- Esempio {i+1} ---")
        print(f"Input: {item['instruction'][:60]}...")
        print(f"Output: {item['output'][:100]}...")
    
    # Salva
    save_training_data(quality_data, output_file)
    
    print(f"\n🎯 Dati pronti per il fine-tuning!")
    print(f"📁 File creati: {output_file} e shard_training_data.jsonl")
    print(f"📊 {len(quality_data)} esempi di training")

if __name__ == "__main__":
    main()
