#!/usr/bin/env python3
"""
Fine-Tuning Script per SHARD
Personalizza il modello Qwen sui dati conversazionali di SHARD
"""

import json
import torch
import os
from datasets import Dataset
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from peft import LoraConfig, get_peft_model, TaskType
import warnings
warnings.filterwarnings("ignore")

class SHARDFineTuner:
    def __init__(self, model_name="microsoft/DialoGPT-medium", output_dir="./shard-finetuned"):
        """
        Inizializza il fine-tuner per SHARD
        
        Args:
            model_name: Nome del modello base (useremo Qwen quando disponibile)
            output_dir: Directory dove salvare il modello fine-tuned
        """
        self.model_name = model_name
        self.output_dir = output_dir
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        print(f"🔥 SHARD Fine-Tuner Inizializzato")
        print(f"📱 Device: {self.device}")
        print(f"🎯 Modello base: {model_name}")
        
    def load_training_data(self, data_file="shard_real_training_data.json"):
        """Carica i dati di training convertiti"""
        print(f"📖 Caricando dati da {data_file}...")
        
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"✅ Caricati {len(data)} esempi di training")
        
        # Dati già nel formato giusto per il training
        texts = [item["text"] for item in data]
        
        return Dataset.from_dict({"text": texts})
    
    def setup_model_and_tokenizer(self):
        """Configura il modello e tokenizer"""
        print(f"🤖 Caricando modello e tokenizer...")
        
        # Per ora usiamo un modello standard, poi sostituiremo con Qwen
        # Nota: Qwen locale richiederebbe una configurazione diversa
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device_map="auto" if self.device == "cuda" else None
            )
            
            # Aggiungi pad token se non esiste
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
                
        except Exception as e:
            print(f"⚠️ Errore nel caricare il modello: {e}")
            print("💡 Useremo un modello alternativo per il test")
            # Fallback a un modello più piccolo
            self.model_name = "microsoft/DialoGPT-small"
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(self.model_name)
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
        
        print(f"✅ Modello caricato: {self.model_name}")
        
    def setup_lora(self):
        """Configura LoRA per fine-tuning efficiente"""
        print("🔧 Configurando LoRA...")
        
        # Per DialoGPT/GPT-2, i moduli supportati sono specifici
        target_modules = []
        
        # Trova tutti i moduli Linear e Conv1D
        for name, module in self.model.named_modules():
            module_type = type(module).__name__
            if module_type in ['Linear', 'Conv1D']:
                # Prendi solo il nome del modulo, non il path completo
                module_name = name.split('.')[-1]
                if module_name not in target_modules:
                    target_modules.append(module_name)
        
        # Filtra solo i moduli di attenzione supportati
        supported_modules = []
        for module_name in target_modules:
            if module_name in ['c_attn', 'c_proj']:  # Moduli specifici per GPT-2/DialoGPT
                supported_modules.append(module_name)
        
        print(f"🎯 Target modules supportati: {supported_modules}")
        
        # Se non troviamo moduli supportati, usa un approccio più semplice
        if not supported_modules:
            print("🔄 Fallback a moduli generici...")
            supported_modules = ["c_attn", "c_proj"]
        
        lora_config = LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            inference_mode=False,
            r=8,  # Rank più basso per stabilità
            lora_alpha=16,  # Alpha corrispondente
            lora_dropout=0.1,
            target_modules=supported_modules,
            bias="none",  # Nessun bias per semplicità
        )
        
        try:
            self.model = get_peft_model(self.model, lora_config)
            self.model.print_trainable_parameters()
            print("✅ LoRA configurato!")
        except Exception as e:
            print(f"⚠️ Errore LoRA: {e}")
            print("🔄 Tentativo con configurazione più semplice...")
            
            # Configurazione ultra-semplice
            simple_config = LoraConfig(
                task_type=TaskType.CAUSAL_LM,
                r=4,
                lora_alpha=8,
                target_modules=["c_proj"],  # Solo un modulo
                bias="none"
            )
            self.model = get_peft_model(self.model, simple_config)
            self.model.print_trainable_parameters()
            print("✅ LoRA semplificato configurato!")
        
    def tokenize_dataset(self, dataset):
        """Tokenizza il dataset per il training"""
        print("🔤 Tokenizzando dataset...")
        
        def tokenize_function(examples):
            return self.tokenizer(
                examples["text"],
                truncation=True,
                padding=True,
                max_length=512,  # Lunghezza massima delle sequenze
                return_tensors="pt"
            )
        
        tokenized_dataset = dataset.map(
            tokenize_function,
            batched=True,
            remove_columns=dataset.column_names
        )
        
        print(f"✅ Dataset tokenizzato: {len(tokenized_dataset)} esempi")
        return tokenized_dataset
        
    def train(self, dataset, epochs=3, learning_rate=5e-5):
        """Esegue il fine-tuning"""
        print(f"🚀 Iniziando fine-tuning...")
        print(f"📊 Parametri: {epochs} epochs, lr={learning_rate}")
        
        # Configura il training
        training_args = TrainingArguments(
            output_dir=self.output_dir,
            num_train_epochs=epochs,
            per_device_train_batch_size=1,  # Batch size piccolo per RAM limitata
            gradient_accumulation_steps=8,  # Simula batch più grandi
            learning_rate=learning_rate,
            warmup_steps=100,
            logging_steps=10,
            save_steps=500,
            save_total_limit=2,
            remove_unused_columns=False,
            dataloader_pin_memory=False,
            fp16=self.device == "cuda",  # Mixed precision se GPU
            report_to=None,  # Disable wandb/tensorboard
        )
        
        # Data collator
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer,
            mlm=False,  # Causal LM, non masked LM
        )
        
        # Trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=dataset,
            data_collator=data_collator,
        )
        
        # Training!
        print("🔥 INIZIO TRAINING!")
        trainer.train()
        
        # Salva il modello finale
        print(f"💾 Salvando modello in {self.output_dir}")
        trainer.save_model()
        self.tokenizer.save_pretrained(self.output_dir)
        
        print("✅ Fine-tuning completato!")
        
    def test_model(self, test_prompt="Chi sei?"):
        """Testa il modello fine-tuned"""
        print(f"🧪 Testando il modello con: '{test_prompt}'")
        
        # Carica il modello fine-tuned
        model_path = self.output_dir
        if os.path.exists(model_path):
            tokenizer = AutoTokenizer.from_pretrained(model_path)
            model = AutoModelForCausalLM.from_pretrained(model_path)
            
            # Genera risposta
            inputs = tokenizer.encode(f"<|im_start|>user\n{test_prompt}<|im_end|>\n<|im_start|>assistant\n", return_tensors="pt")
            
            with torch.no_grad():
                outputs = model.generate(
                    inputs,
                    max_length=inputs.shape[1] + 150,
                    num_return_sequences=1,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=tokenizer.eos_token_id
                )
            
            response = tokenizer.decode(outputs[0], skip_special_tokens=True)
            print(f"🤖 Risposta SHARD: {response}")
        else:
            print(f"❌ Modello non trovato in {model_path}")

def main():
    print("🔥 SHARD Fine-Tuning Pipeline")
    print("=" * 50)
    
    # Inizializza il fine-tuner
    fine_tuner = SHARDFineTuner(output_dir="./shard-qwen-finetuned")
    
    try:
        # 1. Carica i dati
        dataset = fine_tuner.load_training_data()
        
        # 2. Setup modello
        fine_tuner.setup_model_and_tokenizer()
        
        # 3. Setup LoRA
        fine_tuner.setup_lora()
        
        # 4. Tokenizza dataset
        tokenized_dataset = fine_tuner.tokenize_dataset(dataset)
        
        # 5. Fine-tuning
        fine_tuner.train(tokenized_dataset, epochs=3)
        
        # 6. Test
        fine_tuner.test_model("Chi sei?")
        fine_tuner.test_model("Qual è la tua missione?")
        
        print("\n🎯 Fine-tuning completato con successo!")
        print(f"📁 Modello salvato in: ./shard-qwen-finetuned")
        
    except Exception as e:
        print(f"❌ Errore durante il fine-tuning: {e}")
        print("💡 Verifica che tutti i pacchetti siano installati:")
        print("pip install torch transformers datasets peft accelerate")

if __name__ == "__main__":
    main()
