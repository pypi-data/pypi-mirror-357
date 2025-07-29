from .grammer import (
    rule_based_corrector,
    build_dataset,
    train_tokenizer,
    Seq2Seq,
    train_model,
    correct_sentence
)
import torch

# Example sentences (correct ones)
correct_sentences = [
    "I have an apple.",
    "She likes to go to school every day.",
    "He does not like oranges.",
    "Thanks, I feel very nice to hear that.",
    "What is your name?",
    "My name is Python Artificial Intelligence.",
    "Do you understand English?",
    "The weather is nice today.",
    "I am learning to code.",
    "We are going to the market.",
    "It is raining outside.",
    "They have three cats.",
    "You should take a break.",
    "Can you help me?",
    "This is a great idea."
]

# Generate training data by corrupting correct sentences
training_data = build_dataset(correct_sentences)

# Flatten dataset sentences for tokenizer training
all_sentences = [sent for pair in training_data for sent in pair]

# Train tokenizer
tokenizer = train_tokenizer(all_sentences)

# Vocabulary size from tokenizer
vocab_size = tokenizer.get_vocab_size()

# Create the Seq2Seq model
model = Seq2Seq(vocab_size)

# Train the model (this will print loss per epoch)
train_model(model, training_data, tokenizer, epochs=5)

# Test input sentence with errors
def correct_grammar(sentence: str = 'thanks i feel very nice to here that.'):
    # Use model to correct the sentence
    corrected_text = correct_sentence(model, sentence, tokenizer)
    return rule_based_corrector(sentence)


