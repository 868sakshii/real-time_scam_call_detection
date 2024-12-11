from datasets import load_dataset, DatasetDict
from transformers import AutoTokenizer, AutoModelForSequenceClassification, TrainingArguments, Trainer

# Load dataset
dataset = load_dataset('csv', data_files='D:\scam-call-detection\data\dataset\large_scam_dataset.csv')  # Your CSV file

# Tokenize dataset
tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")
def tokenize_function(example):
    return tokenizer(example["text"], padding="max_length", truncation=True)

tokenized_datasets = dataset.map(tokenize_function, batched=True)

# Split the dataset into train and test
# For simplicity, we'll use a simple split (e.g., 80% train, 20% test)
train_size = int(len(tokenized_datasets['train']) * 0.8)
test_size = len(tokenized_datasets['train']) - train_size

train_dataset = tokenized_datasets['train'].select(range(train_size))
test_dataset = tokenized_datasets['train'].select(range(train_size, train_size + test_size))

# Load model
model = AutoModelForSequenceClassification.from_pretrained("distilbert-base-uncased", num_labels=2)

# Training arguments
training_args = TrainingArguments(
    output_dir="D:\scam-call-detection\models\distilbert_model",
    evaluation_strategy="epoch",
    learning_rate=2e-5,
    per_device_train_batch_size=16,
    num_train_epochs=3,
    weight_decay=0.01,
)

# Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=test_dataset,
)

# Train model
trainer.train()
