import torch
import torch.nn as nn
import torchaudio
from torch.utils.data import Dataset, DataLoader
import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
import os

characters = 'abcdefghijklmnopqrstuvwxyz'

num_classes = len(characters) + 1

char_to_idx = {c: i for i, c in enumerate(characters, 1)}

idx_to_char = {i: c for c, i in char_to_idx.items()}

def text_to_int(text) -> list:
    return [char_to_idx.get(c, 0) for c in text.lower()]

def int_to_text(indices) -> str:
    return ''.join(idx_to_char[i] for i in indices if i != 0)

class SpeechDataset(Dataset):
    def __init__(self, audio_files, transcripts) -> None:
        self.audio_files = audio_files
        self.transcripts = transcripts
        self.transform = torchaudio.transforms.MelSpectrogram(sample_rate= 16000, n_mels=128)

    def __len__(self):
        return len(self.audio_files)

    def __getitem__(self, idx):
        waveform, sample_rate = torchaudio.load(self.audio_files[idx])

        if sample_rate != 16000:
            resampler = torchaudio.transforms.Resample(sample_rate, 16000)
            waveform = resampler(waveform)

        features = self.transform(waveform).squeeze(0).transpose(0, 1)
        label = torch.tensor(text_to_int(self.transcripts[idx]))

        return features, label

def collect_fn(batch):
    features = [item[0] for item in batch]
    label = [item[1] for item in batch]
    feature_lengths = torch.tensor([f.size(0) for f in features])
    label_lengths = torch.tensor([len(l) for l in label])
    padded_features = nn.utils.rnn.pad_sequence(features, batch_first= True).transpose(1, 2)
    padded_labels = torch.cat(label)

    return padded_features, padded_labels, feature_lengths, label_lengths

class SpeechRecognitionModel(nn.Module):
    def __init__(self, input_dim: int = 128, hidden_dim: int = 256, output_dim: int = num_classes, num_layers: int = 3) -> None:
        super().__init__()
        self.rnn = nn.GRU(input_dim, hidden_dim, num_layers, batch_first= True, bidirectional = True)
        self.fc = nn.Linear(hidden_dim * 2, output_dim)

    def forward(self, x):
        x = x.transpose(1, 2)
        x, _ = self.rnn(x)
        return x.log_softmax(dim= -1)

model = SpeechRecognitionModel()
ctc_loss = nn.CTCLoss(blank = 0, zero_infinity= True)
optimizer = torch.optim.Adam(model.parameters(), lr= 0.001)

print('Traning Started!')
def train(dataloder):
    model.train()
    for features, labels, feature_lengths, label_lengths in dataloder:
        optimizer.zero_grad()
        outputs = model(features)
        outputs = outputs.permute(1, 0, 2)
        loss = ctc_loss(outputs, labels, feature_lengths, label_lengths)
        loss.backward()
        optimizer.step()
        #print(f'Loss: {loss.item()}')

print('Traning Completed!')

def greedy_decode(output, input_lengths):
    decoded_batch = []
    for i, length in enumerate(input_lengths):
        probs = output[i][:length]
        preds = torch.argmax(probs, dim= -1).tolist()
        prev = -1
        decoded = [p for p in preds if p != prev and p != 0]
        prev = preds[0] if preds else -1
        decoded_batch.append(int_to_text(decoded))

    return decoded_batch

def record(time_duration: int = 5, sample_rate: int = 16000) -> str:
    audio = sd.rec(int(time_duration * sample_rate), samplerate= sample_rate, channels= 1, dtype= 'int16')
    sd.wait()
    file_name = r'.\assert\rec_audio.wav'
    write(file_name, sample_rate, audio)
    return 'DONE'


class STTModel:
    def __init__(self, time_duration: int = 5, sample_rate: int = 16000):
        self.duration = time_duration # seconds of recording
        self.sample_rate = sample_rate # 16KHz is common for speech recognition

    def predict(self) -> str:
        record()
        waveform, _ = torchaudio.load(r'.\assert\rec_audio.wav')
        features = torchaudio.transforms.MelSpectrogram(self.sample_rate, n_mels= 128)
        features = features.squeeze(0).transpose(0, 1).unsqueeze(0).transpose(1, 2)

        with torch.no_grad():
            out = model(features)
            decoded = greedy_decode(out.transpose(0, 1), [out.size(1)])
            return decoded[0]

    def save(self):
        torch.save(model.state_dict(), r'.\stt_model.pth')

    def load(self):
        if os.path.exists(r'.\stt_model.pth'):
            model.load_state_dict(torch.load(r".\stt_model.pth"))
            model.eval()

sttModel = STTModel()
if os.path.exists(r'.\stt_model.wav'):
    pass

else:
    audio_files = [r'.\assert\audio1.wav', r'.\assert\audio2.wav']
    transcripts = ['Hello world', 'testing']

    dataset = SpeechDataset(audio_files, transcripts)
    dataloder = DataLoader(dataset, batch_size= 2, collate_fn= collect_fn)
    train(dataloder)
    sttModel.save()

class STT:
    def __init__(self) -> None:
        sttModel.load()
        self.text = sttModel.predict()

    def outputs(self) -> str:
        return self.text
