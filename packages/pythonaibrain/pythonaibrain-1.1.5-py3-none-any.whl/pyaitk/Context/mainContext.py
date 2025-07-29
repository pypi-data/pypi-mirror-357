import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
import numpy as np

# ------------------------
# Tokenizer and Vocab
# ------------------------

def tokenize(text):
    return text.lower().replace('.', ' .').replace(',', ' ,').split()

class Vocab:
    def __init__(self):
        self.word2idx = {'<PAD>': 0, '<UNK>': 1}
        self.idx2word = {0: '<PAD>', 1: '<UNK>'}

    def build(self, texts):
        idx = 2
        for text in texts:
            for word in tokenize(text):
                if word not in self.word2idx:
                    self.word2idx[word] = idx
                    self.idx2word[idx] = word
                    idx += 1

    def encode(self, text, max_len=50):
        tokens = tokenize(text)
        ids = [self.word2idx.get(tok, 1) for tok in tokens]
        return ids[:max_len] + [0] * (max_len - len(ids))

# ------------------------
# Dataset for QA
# ------------------------

class QADataset(Dataset):
    def __init__(self, data, vocab, max_len=50):
        self.data = data
        self.vocab = vocab
        self.max_len = max_len

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        context, question, answer = self.data[idx]
        context_tokens = tokenize(context)
        answer_tokens = tokenize(answer)
        try:
            start = context_tokens.index(answer_tokens[0])
            end = start + len(answer_tokens) - 1
        except:
            start = end = 0  # fallback if not found

        return {
            'context': torch.tensor(self.vocab.encode(context, self.max_len)),
            'question': torch.tensor(self.vocab.encode(question, self.max_len)),
            'start': torch.tensor(start),
            'end': torch.tensor(end)
        }

# ------------------------
# QA Model
# ------------------------

class QAModel(nn.Module):
    def __init__(self, vocab_size, embed_size=100, hidden_size=128):
        super(QAModel, self).__init__()
        self.embedding = nn.Embedding(vocab_size, embed_size)
        self.context_lstm = nn.LSTM(embed_size, hidden_size, bidirectional=True, batch_first=True)
        self.question_lstm = nn.LSTM(embed_size, hidden_size, bidirectional=True, batch_first=True)

        self.attn_linear = nn.Linear(hidden_size * 2, hidden_size * 2)
        self.start_output = nn.Linear(hidden_size * 4, 1)
        self.end_output = nn.Linear(hidden_size * 4, 1)

    def forward(self, context, question):
        context_emb = self.embedding(context)
        question_emb = self.embedding(question)

        context_out, _ = self.context_lstm(context_emb)
        question_out, _ = self.question_lstm(question_emb)

        # Attention
        question_mean = torch.mean(question_out, dim=1).unsqueeze(1)
        attn = self.attn_linear(question_mean).expand_as(context_out)

        combined = torch.cat([context_out, attn], dim=2)

        start_logits = self.start_output(combined).squeeze(-1)
        end_logits = self.end_output(combined).squeeze(-1)

        return start_logits, end_logits

# ------------------------
# Inference Function
# ------------------------

def answer_question(model, vocab, context, question):
    model.eval()
    ctx = torch.tensor([vocab.encode(context)], dtype=torch.long)
    qst = torch.tensor([vocab.encode(question)], dtype=torch.long)

    with torch.no_grad():
        start_logits, end_logits = model(ctx, qst)
        start_idx = torch.argmax(start_logits, dim=1).item()
        end_idx = torch.argmax(end_logits, dim=1).item()

    tokens = tokenize(context)
    if end_idx < start_idx or end_idx >= len(tokens):
        return "Answer not found properly."
    return " ".join(tokens[start_idx:end_idx+1])

def train_model(model, dataloader, epochs=10, lr=0.001):
    print('Traning')
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    loss_fn = nn.CrossEntropyLoss()

    model.train()
    for epoch in range(epochs):
        total_loss = 0.0
        for batch in dataloader:
            optimizer.zero_grad()
            out_start, out_end = model(batch['context'], batch['question'])
            loss = loss_fn(out_start, batch['start']) + loss_fn(out_end, batch['end'])
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        #print(f"Epoch {epoch + 1}/{epochs}, Loss: {total_loss:.4f}")
    print('Traning Done!')

class Contexts:
    def __init__(self) -> None:
        self.context = "Patanjali Ayurved is an Indian company. It was founded by Baba Ramdev and Acharya Balkrishna in 2006."
        self.question = "Who founded Patanjali Ayurved?"
        self.answer = "Baba Ramdev and Acharya Balkrishna"

        self.vocab = Vocab()
        self.vocab.build([self.context, self.question, self.answer])

        self.data = [(self.context, self.question, self.answer)]
        self.dataset = QADataset(self.data, self.vocab)
        self.loader = DataLoader(self.dataset, batch_size=1)

        self.model = QAModel(len(self.vocab.word2idx))

        # 🔁 Train
        train_model(self.model, self.loader, epochs=10)

    def ask(self, context: str, question: str):
        return answer_question(self.model, self.vocab, context, question)

contexts = Contexts()