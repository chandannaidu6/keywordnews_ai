import torch
import os
from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    Trainer,
    TrainingArguments,
)
from peft import LoraConfig,get_peft_model,TaskType
from torch.nn.utils.rnn import pad_sequence

model_name="gpt2"
device="cpu"
train_split = "train[:1000]"
max_seq_length = 256
batch_size = 1
num_epochs = 1

dataset = load_dataset("cnn_dailymail","3.0.0",split=train_split)

tokenizer = AutoTokenizer.from_pretrained(model_name)
tokenizer.pad_token = tokenizer.eos_token

def tokenize_function(examples):
    text = [f"Summarize:\n\n{article}\n\nSummary:" for article in examples['article']]
    outputs = tokenizer(
        text,
        truncation=True,
        padding=False,
        max_length=max_seq_length
    )
    outputs['labels'] = outputs['input_ids'].copy()
    return outputs
tokenized_data = dataset.map(
    tokenize_function,
    batched=True,
    remove_columns=['article','highlights','id']     
)


#
# 4. Load the base model on CPU
#
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float32,
)
model.to(device)

#
# 5. Apply LoRA
#
lora_config = LoraConfig(
    r=8,
    lora_alpha=32,
    lora_dropout=0.1,
    bias="none",
    task_type=TaskType.CAUSAL_LM,
    inference_mode=False,
    # GPT-2 uses Conv1D modules: "c_attn", "c_proj"
    target_modules=["c_attn", "c_proj"],
)
model = get_peft_model(model, lora_config)
model.train()

#
# 6. Custom Data Collator (No 'causal_mask')
#
class GPT2DataCollator:
    """
    Custom collator that pads input_ids, attention_mask, and labels,
    ensuring no 'causal_mask' or other unexpected fields are created.
    """
    def __init__(self, tokenizer, max_length=256):
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __call__(self, features):
        input_ids_list = []
        attention_mask_list = []
        labels_list = []

        for f in features:
            # Convert to torch tensors
            in_ids = torch.tensor(f["input_ids"], dtype=torch.long)
            # If 'attention_mask' is missing, default to all 1s
            if "attention_mask" in f:
                at_mask = torch.tensor(f["attention_mask"], dtype=torch.long)
            else:
                at_mask = torch.ones_like(in_ids)
            if "labels" in f:
                lbls = torch.tensor(f["labels"], dtype=torch.long)
            else:
                lbls = in_ids.clone()

            input_ids_list.append(in_ids)
            attention_mask_list.append(at_mask)
            labels_list.append(lbls)

        # Pad sequences with pad_token_id for input_ids, 0 for attention_mask, -100 for labels
        input_ids = pad_sequence(input_ids_list, batch_first=True, padding_value=self.tokenizer.pad_token_id)
        attention_mask = pad_sequence(attention_mask_list, batch_first=True, padding_value=0)
        labels = pad_sequence(labels_list, batch_first=True, padding_value=-100)

        # Truncate if needed
        if input_ids.size(1) > self.max_length:
            input_ids = input_ids[:, :self.max_length]
            attention_mask = attention_mask[:, :self.max_length]
            labels = labels[:, :self.max_length]

        return {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
            "labels": labels
        }

data_collator = GPT2DataCollator(tokenizer=tokenizer, max_length=max_seq_length)

#
# 7. Training Arguments
#
training_args = TrainingArguments(
    output_dir="./gpt2_finetuned_cpu",
    overwrite_output_dir=True,
    num_train_epochs=num_epochs,
    per_device_train_batch_size=batch_size,
    gradient_accumulation_steps=4,
    logging_steps=50,
    save_steps=100,
    fp16=False,          # CPU doesn't support FP16 by default
    report_to="none",
)

#
# 8. Initialize Trainer
#
from transformers import Trainer

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_data,
    data_collator=data_collator,
)

#
# 9. Optional: Test a Forward Pass
#
def test_forward_pass():
    batch = next(iter(trainer.get_train_dataloader()))
    # Clean up batch to remove any unknown fields
    for k, v in list(batch.items()):
        if isinstance(v, torch.Tensor):
            batch[k] = v.to(device)
        # Remove anything GPT-2 won't understand
        if k not in ["input_ids", "attention_mask", "labels"]:
            del batch[k]

    # Forward pass
    with torch.no_grad():
        outputs = model(**batch)
        loss_val = outputs.loss.item()
        print("Test forward pass loss:", loss_val)
    return loss_val

test_loss = test_forward_pass()

#
# 10. Train
#
trainer.train()

#
# 11. Save final LoRA adapters and tokenizer
#
os.makedirs("./gpt2_finetuned_cpu", exist_ok=True)
model.save_pretrained("./gpt2_finetuned_cpu")
tokenizer.save_pretrained("./gpt2_finetuned_cpu")

print("LoRA fine-tuning on CPU complete!")
