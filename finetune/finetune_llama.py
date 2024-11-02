from unsloth import FastLanguageModel
import torch
from datasets import load_dataset
from transformers import (
    Trainer,
    TrainingArguments,
    DataCollatorForLanguageModeling
)
from peft import LoraConfig, get_peft_model, TaskType

max_seq_length = 2048
dtype = None
load_in_4bit = True 

# Initialize model with proper configuration
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = "unsloth/Llama-3.2-1B-Instruct-bnb-4bit",
    max_seq_length = max_seq_length,
    dtype = dtype,
    load_in_4bit = load_in_4bit,
)

# Load dataset
dataset = load_dataset('cnn_dailymail', '3.0.0', split='train[:1000]')
def tokenize_function(examples):
    # Add special tokens and create proper input format
    prompt_template = "Summarize this article:\n\n{}\n\nSummary:"
    texts = [prompt_template.format(article) for article in examples['article']]
    
    tokenized = tokenizer(
        texts,
        truncation=True,
        padding='max_length',
        max_length=512,
        return_tensors=None,
    )
    
    # Add labels for causal language modeling
    tokenized['labels'] = tokenized['input_ids'].copy()
    return tokenized

tokenized_datasets = dataset.map(
    tokenize_function,
    batched=True,
    remove_columns=['article', 'highlights', 'id']
)
peft_config = LoraConfig(
    task_type=TaskType.CAUSAL_LM,
    inference_mode=False,
    r=8,
    lora_alpha=32,
    lora_dropout=0.1,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    bias="none",  # Disable bias training
    modules_to_save=None,  # Don't save any modules fully
)
model = get_peft_model(model, peft_config)

# Ensure model is in training mode
model.train()
model.enable_input_require_grads()

class CustomDataCollator(DataCollatorForLanguageModeling):
    def __call__(self, examples):
        batch = super().__call__(examples)
        # Convert input_ids to labels for causal LM
        batch['labels'] = batch['input_ids'].clone()
        return batch

data_collator = CustomDataCollator(
    tokenizer=tokenizer,
    mlm=False
)

training_args = TrainingArguments(
    output_dir='./llama_finetuned',
    overwrite_output_dir=True,
    num_train_epochs=3,
    per_device_train_batch_size=1,
    gradient_accumulation_steps=4,
    save_steps=10_000,
    save_total_limit=2,
    logging_steps=500,
    learning_rate=5e-4,
    fp16=True,
    report_to="none",
    gradient_checkpointing=True,
    warmup_steps=100,
    weight_decay=0.01,
    remove_unused_columns=False,  # Important for custom datasets
)

# Initialize trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_datasets,
    data_collator=data_collator,
)

# Verify model setup
print("Number of trainable parameters:", sum(p.numel() for p in model.parameters() if p.requires_grad))
model.print_trainable_parameters()

# Test forward pass before training
def test_forward_pass():
    batch = next(iter(trainer.get_train_dataloader()))
    # Remove any requires_grad from integer tensors
    for k, v in batch.items():
        if isinstance(v, torch.Tensor) and v.dtype in [torch.long, torch.int, torch.int64]:
            v.requires_grad_(False)

# Run test forward pass
test_loss = test_forward_pass()

# Start training
trainer.train()

# Save the LoRA adapters
model.save_pretrained('./llama_finetuned')