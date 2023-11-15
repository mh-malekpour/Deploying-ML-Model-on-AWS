from flask import Flask, jsonify
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
import torch 
import random
import string


app = Flask(__name__)

# Load pre-trained model and tokenizer
tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
model = DistilBertForSequenceClassification.from_pretrained('distilbert-base-uncased', num_labels=2)

def generate_random_text(length=50):
    letters = string.ascii_lowercase + ' '
    return ''.join(random.choice(letters) for i in range(length))


@app.route('/run_model')
def run_model():
    # Generate random input text
    input_txt = generate_random_text()

    # Tokenize the input text and run it through the model
    inputs = tokenizer(input_txt, return_tensors='pt', padding=True, truncation=True)
    outputs = model(**inputs)

    # The model returns logits, so let's turn that into probabilities
    probabilities = torch.softmax(outputs.logits, dim=-1)

    # Convert the tensor to a list and return
    probabilities_list = probabilities.tolist()[0]

    return jsonify({"input_txt": input_txt, "probabilities":probabilities_list})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5000')