import pandas as pd
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification
from transformers import Trainer, TrainingArguments
import torch
from sklearn.metrics import classification_report

# Load the test dataset
test_file = "D:\scam-call-detection\data\dataset\large_scam_dataset.csv"  # Replace with your test CSV file
test_data = pd.read_csv(test_file)

# Check the columns of the dataset
print("Column names in the dataset:", test_data.columns)

# Let's assume the actual column name for the text is 'text' or you can replace it with the correct column name
messages = test_data["text"].tolist()  # Replace "text" with the correct column name if needed
labels = test_data["label"].tolist()  # Make sure 'label' is the correct column for your labels

# Load the pre-trained DistilBERT model and tokenizer
model = DistilBertForSequenceClassification.from_pretrained("D:/scam-call-detection/models/distilbert_model")
tokenizer = DistilBertTokenizerFast.from_pretrained("distilbert-base-uncased-finetuned-sst-2-english")

# Tokenize the input messages
inputs = tokenizer(messages, padding=True, truncation=True, return_tensors="pt", max_length=512)

# Prepare the dataset for evaluation (create a PyTorch Dataset)
class ScamDataset(torch.utils.data.Dataset):
    def __init__(self, inputs, labels):
        self.inputs = inputs
        self.labels = labels

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.inputs.items()}
        item['labels'] = torch.tensor(self.labels[idx])
        return item

test_dataset = ScamDataset(inputs, labels)

# Evaluate the model
trainer = Trainer(
    model=model,
    eval_dataset=test_dataset,
)

# Predict and print classification report
predictions = trainer.predict(test_dataset)
pred_labels = torch.argmax(torch.tensor(predictions.predictions), axis=1).numpy()

# Print the classification report
print(classification_report(labels, pred_labels))
