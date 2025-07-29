import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import nltk
from nltk.tokenize import word_tokenize
import requests

nltk.download('punkt')

# === TRAINING DATA FOR NER ===
sentences = [
    "I live in Delhi",
    "He went to Mumbai yesterday",
    "Bengaluru is beautiful",
    "I love eating apples",
    "She works in Hyderabad",
    "Nagpur is hot in summer",
    "Bananas are yellow",
    "Going to Kolkata tomorrow",
    "Weather in Chennai is humid"
]

labels = [
    [0, 0, 0, 1],
    [0, 0, 0, 1, 0],
    [1, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 1],
    [1, 0, 0, 0, 0],
    [0, 0, 0],
    [0, 0, 1, 0],
    [0, 0, 1, 0, 0]
]

# === BUILD VOCAB ===
tokenized = [word_tokenize(s) for s in sentences]
vocab = {'<PAD>': 0, '<UNK>': 1}
for sent in tokenized:
    for word in sent:
        if word not in vocab:
            vocab[word] = len(vocab)

# === DATASET + DATALOADER ===
class NERDataset(Dataset):
    def __init__(self, sents, tags):
        self.sents = sents
        self.tags = tags
    def __len__(self):
        return len(self.sents)
    def __getitem__(self, idx):
        words = self.sents[idx]
        ids = [vocab.get(w, vocab['<UNK>']) for w in words]
        return torch.tensor(ids), torch.tensor(self.tags[idx])

def pad_collate(batch):
    inputs, targets = zip(*batch)
    x_padded = nn.utils.rnn.pad_sequence(inputs, batch_first=True)
    y_padded = nn.utils.rnn.pad_sequence(targets, batch_first=True)
    return x_padded, y_padded

# === MODEL ===
class BiLSTM_NER(nn.Module):
    def __init__(self, vocab_size, emb_dim, hidden_dim):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, emb_dim, padding_idx=0)
        self.lstm = nn.LSTM(emb_dim, hidden_dim, batch_first=True, bidirectional=True)
        self.fc = nn.Linear(hidden_dim * 2, 2)  # 2 tags: city / non-city
    def forward(self, x):
        x = self.embedding(x)
        x, _ = self.lstm(x)
        x = self.fc(x)
        return x

# === TRAINING ===
dataset = NERDataset(tokenized, labels)
loader = DataLoader(dataset, batch_size=2, shuffle=True, collate_fn=pad_collate)

model = BiLSTM_NER(len(vocab), emb_dim=64, hidden_dim=32)
optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
criterion = nn.CrossEntropyLoss()

for epoch in range(10):
    model.train()
    for batch_x, batch_y in loader:
        out = model(batch_x)
        loss = criterion(out.view(-1, 2), batch_y.view(-1))
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
    print(f"Epoch {epoch+1} loss: {loss.item():.4f}")

# === WEATHER FETCHING ===
def get_weather(city_name, api_key):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api_key}&units=metric"
    response = requests.get(url)
    if response.status_code != 200:
        return f"Could not fetch weather for '{city_name}'."
    data = response.json()
    desc = data["weather"][0]["description"]
    temp = data["main"]["temp"]
    return f"🌤️ {city_name}: {desc}, {temp}°C"

# === INFERENCE ===
def extract_city(text):
    tokens = word_tokenize(text)
    input_ids = torch.tensor([[vocab.get(w, vocab['<UNK>']) for w in tokens]])
    model.eval()
    with torch.no_grad():
        logits = model(input_ids)
        preds = torch.argmax(logits, dim=-1).squeeze().tolist()
    cities = [w for w, p in zip(tokens, preds) if p == 1]
    return cities

# === MAIN APP ===
if __name__ == "__main__":
    api_key = "561c40a7d1de42d04a6343355a4a8921"  # Replace with your real key
    while True:
        user_input = input("\nAsk about weather (or type 'exit'): ")
        if user_input.lower() == "exit":
            break
        city_list = extract_city(user_input)
        if not city_list:
            print("❌ No city detected. Please try again.")
        else:
            for city in city_list:
                print(get_weather(city, api_key))
