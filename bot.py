import os
import nltk
import numpy as np
import tensorflow as tf

# Suppress TensorFlow logging
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  

# Import necessary libraries
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from sklearn.model_selection import train_test_split
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense, Dropout

# Download necessary NLTK data
nltk.download('punkt')  # This downloads the correct tokenizer
nltk.download('stopwords')

# Example small dataset of questions and responses
dataset = [
    ("hello", "Hi there! What's your name?"),
    ("what is your name", "I'm Chatbot! Nice to meet you."),
    ("how are you", "I'm here to assist you!"),
    ("tell me a story", "Once upon a time, in a land far away..."),
    ("give me some news", "Today's top story is about..."),
    ("what's the weather like", "I'm not a meteorologist, but it's probably nice!"),
    ("goodbye", "Goodbye! Have a great day!"),
]

# Preprocessing
stop_words = set(stopwords.words("english"))

def preprocess_text(text):
    tokens = word_tokenize(text.lower())
    filtered_tokens = [w for w in tokens if w.isalnum() and w not in stop_words]
    return " ".join(filtered_tokens)

# Preprocess dataset
questions, responses = zip(*dataset)
processed_questions = [preprocess_text(q) for q in questions]

# Tokenize and Pad Sequences
tokenizer = Tokenizer()
tokenizer.fit_on_texts(processed_questions)
vocab_size = len(tokenizer.word_index) + 1

sequences = tokenizer.texts_to_sequences(processed_questions)
padded_sequences = pad_sequences(sequences, padding='post')

# Convert responses to numeric labels for training
response_labels = {response: idx for idx, response in enumerate(set(responses))}
reverse_labels = {idx: response for response, idx in response_labels.items()}
numeric_responses = [response_labels[r] for r in responses]

# Split dataset
X_train, X_test, y_train, y_test = train_test_split(padded_sequences, numeric_responses, test_size=0.2, random_state=42)

# Define Model
model = Sequential([
    Embedding(vocab_size, 16, input_length=padded_sequences.shape[1]),
    LSTM(32, return_sequences=True),
    Dropout(0.2),
    LSTM(16),
    Dense(16, activation='relu'),
    Dense(len(response_labels), activation='softmax')
])

model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
model.summary()

# Train Model
model.fit(np.array(X_train), np.array(y_train), epochs=50, batch_size=4, validation_data=(np.array(X_test), np.array(y_test)))

# Chatbot function
def chatbot_response(user_input):
    processed_input = preprocess_text(user_input)
    seq = tokenizer.texts_to_sequences([processed_input])
    padded = pad_sequences(seq, maxlen=padded_sequences.shape[1], padding='post')

    # Predict response
    pred = model.predict(padded)
    response_idx = np.argmax(pred)
    response = reverse_labels[response_idx]
    return response

# Chatbot Interaction
def chat():
    print("Hello! I'm a simple chatbot. Type 'exit' to end the conversation.")
    print(chatbot_response("hello"))  # Initial greeting
    user_name = input("You: ")

    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("Chatbot: Goodbye! Have a great day!")
            break
        response = chatbot_response(user_input)
        print(f"Chatbot: {response}")

# Run the chatbot
if __name__ == "__main__":
    chat()
