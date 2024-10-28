import os
from transformers import LlamaForCausalLM,LlamaTokenizer,Trainer,TrainingArguments,DataCollatorForLanguageModeling
from datasets import load_dataset

tokenizer = LlamaTokenizer.from_pretrained('/root/.llama/checkpoints/Llama3.2-1B')
model = LlamaForCausalLM.from_pretrained('/root/.llama/checkpoints/Llama3.2-1B')

dataset = datasets.load_dataset()