# grammar_corrector_ai module

import re
import nltk
import torch
import torch.nn as nn
from nltk.tokenize import word_tokenize
from tokenizers import Tokenizer, models, trainers, pre_tokenizers

# Download NLTK resources
#nltk.download('punkt')
#nltk.download('averaged_perceptron_tagger')

# ---------- Rule-Based Correction ----------
def rule_based_corrector(text):
    text = re.sub(r'\bi\b', 'I', text)
    text = re.sub(r'\bto here\b', 'to hear', text)
    text = re.sub(r'\bthanks i\b', 'Thanks, I', text, flags=re.IGNORECASE)

    words = word_tokenize(text)
    tagged = nltk.pos_tag(words)

    corrected_words = []
    for i, (word, tag) in enumerate(tagged):
        if word.lower() == "go" and i > 0 and tagged[i-1][0].lower() in ["he", "she", "it"]:
            corrected_words.append("goes")
        else:
            corrected_words.append(word)

    return ' '.join(corrected_words)

# ---------- Data Generation ----------
def corrupt_sentence(sentence):
    sentence = sentence.replace("I", "i")
    sentence = sentence.replace("hear", "here")
    sentence = re.sub(r'\bgoes\b', 'go', sentence)
    return sentence

def build_dataset(correct_sentences):
    dataset = []
    for correct in correct_sentences:
        wrong = corrupt_sentence(correct)
        dataset.append((wrong, correct))
    return dataset

# ---------- Tokenizer ----------
def train_tokenizer(sentences):
    tokenizer = Tokenizer(models.BPE())
    tokenizer.pre_tokenizer = pre_tokenizers.Whitespace()
    trainer = trainers.BpeTrainer(
        vocab_size=1000,
        special_tokens=["<s>", "</s>", "<unk>", "<pad>"],
        show_progress=True
    )
    tokenizer.train_from_iterator(sentences, trainer)
    return tokenizer

# ---------- Seq2Seq Model ----------
class Seq2Seq(nn.Module):
    def __init__(self, vocab_size, emb_dim=128, hidden_dim=256):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, emb_dim)
        self.encoder = nn.LSTM(emb_dim, hidden_dim, batch_first=True)
        self.decoder = nn.LSTM(emb_dim, hidden_dim, batch_first=True)
        self.fc = nn.Linear(hidden_dim, vocab_size)

    def forward(self, src, tgt):
        emb_src = self.embedding(src)
        _, (hidden, cell) = self.encoder(emb_src)
        emb_tgt = self.embedding(tgt)
        output, _ = self.decoder(emb_tgt, (hidden, cell))
        return self.fc(output)

# ---------- Training ----------
print('Traning Start!')
def train_model(model, data, tokenizer, epochs=5):
    model.train()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    criterion = nn.CrossEntropyLoss(ignore_index=tokenizer.token_to_id("<pad>"))

    for epoch in range(epochs):
        total_loss = 0
        for corrupted, correct in data:
            corrupted_ids = [tokenizer.token_to_id("<s>")] + tokenizer.encode(corrupted).ids + [tokenizer.token_to_id("</s>")]
            correct_ids = [tokenizer.token_to_id("<s>")] + tokenizer.encode(correct).ids + [tokenizer.token_to_id("</s>")]

            input_tensor = torch.tensor([corrupted_ids])
            target_tensor = torch.tensor([correct_ids])

            optimizer.zero_grad()

            # Encoder
            emb_input = model.embedding(input_tensor)
            _, (hidden, cell) = model.encoder(emb_input)

            # Decoder input starts with <s>
            decoder_input = torch.tensor([[tokenizer.token_to_id("<s>")]])
            loss = 0

            for t in range(1, target_tensor.size(1)):
                emb_dec = model.embedding(decoder_input)
                output, (hidden, cell) = model.decoder(emb_dec, (hidden, cell))
                logits = model.fc(output[:, -1])
                loss += criterion(logits, target_tensor[:, t])
                # Teacher forcing: feed true token as next input
                decoder_input = target_tensor[:, t].unsqueeze(1)

            loss.backward()
            optimizer.step()
            total_loss += loss.item() / target_tensor.size(1)

        #print(f"Epoch {epoch+1}: Loss = {total_loss / len(data):.4f}")

print('Tranning Completed!')

# ---------- Inference ----------
def correct_sentence(model, input_text, tokenizer):
    model.eval()
    input_ids = tokenizer.encode(input_text).ids
    input_tensor = torch.tensor([input_ids])
    emb_input = model.embedding(input_tensor)
    _, (hidden, cell) = model.encoder(emb_input)

    start_token_id = tokenizer.token_to_id("<s>")
    end_token_id = tokenizer.token_to_id("</s>")

    if start_token_id is None or end_token_id is None:
        raise ValueError("Tokenizer missing special tokens <s> or </s>")

    output_ids = []
    current_input = torch.tensor([[start_token_id]])

    for _ in range(100):
        emb = model.embedding(current_input)
        out, (hidden, cell) = model.decoder(emb, (hidden, cell))
        logits = model.fc(out[:, -1])
        predicted_id = logits.argmax(dim=-1).item()
        output_ids.append(predicted_id)
        if predicted_id == end_token_id:
            break
        current_input = torch.tensor([[predicted_id]])

    return tokenizer.decode(output_ids)

# ---------- Exports ----------
__all__ = [
    "rule_based_corrector",
    "corrupt_sentence",
    "build_dataset",
    "train_tokenizer",
    "Seq2Seq",
    "train_model",
    "correct_sentence"
]
