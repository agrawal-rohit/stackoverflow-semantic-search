from flask import Flask, request, json, jsonify
from flask_cors import CORS, cross_origin
import tensorflow as tf
import keras
from keras.models import load_model
import os
import numpy as np
import spacy
import pandas as pd
import keras.losses
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
import pickle
import keras.backend as K
from sklearn.preprocessing import MultiLabelBinarizer
from utils import preprocess_text
from semantic_search import searchresults
EN = spacy.load('en_core_web_sm')

# Flask App stuff
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# Custom loss function to handle multilabel classification task
def multitask_loss(y_true, y_pred):
    # Avoid divide by 0
    y_pred = K.clip(y_pred, K.epsilon(), 1 - K.epsilon())
    # Multi-task loss
    return K.mean(K.sum(- y_true * K.log(y_pred) - (1 - y_true) * K.log(1 - y_pred), axis=1))

def load_tag_encoder():
    data = pd.read_csv('../../Preprocessed_data.csv')
    
    # Make a dict having tag frequencies
    data.tags = data.tags.apply(lambda x: x.split('|'))
    tag_freq_dict = {}
    for tags in data.tags:
        for tag in tags:
            if tag not in tag_freq_dict:
                tag_freq_dict[tag] = 0
            else:
                tag_freq_dict[tag] += 1

    tags_to_use = 500
    tag_freq_dict_sorted = dict(sorted(tag_freq_dict.items(), key=lambda x: x[1], reverse=True))
    final_tags = list(tag_freq_dict_sorted.keys())[:tags_to_use]

    final_tag_data = []
    for tags in data.tags:
        temp = []
        for tag in tags:
            if tag in final_tags:
                temp.append(tag)
        final_tag_data.append(temp)

    tag_encoder = MultiLabelBinarizer()
    tags_encoded = tag_encoder.fit_transform(final_tag_data)
    return tag_encoder

def predict_tags(text):
    # Tokenize text
    x_test = pad_sequences(tokenizer.texts_to_sequences([text]), maxlen=MAX_SEQUENCE_LENGTH)
    # Predict
    with graph.as_default():
        prediction = model.predict([x_test])[0]
    for i,value in enumerate(prediction):
        if value > 0.5:
            prediction[i] = 1
        else:
            prediction[i] = 0
    tags = tag_encoder.inverse_transform(np.array([prediction]))
    return tags

# Load model and other relevant stuff
tag_encoder = load_tag_encoder()
MAX_SEQUENCE_LENGTH = 300
with open('../../models/tokenizer.pickle', 'rb') as handle:
    tokenizer = pickle.load(handle)
keras.losses.multitask_loss = multitask_loss
global graph
graph = tf.get_default_graph()
model = load_model('../../models/Tag_predictor.h5')

# Flask API Routes
@app.route('/')
@cross_origin()
def homepage():
    return jsonify({'test': "Working!"})

@app.route('/getsearchresults')
@cross_origin()
def getsearchresults():
    params = request.json
    if (params == None):
        params = request.args

    query = params["query"]
    query = preprocess_text(query)
    tags = list(predict_tags(query))
    results = searchresults(query, params["num_results"])
    return jsonify({'tags': tags, 'results': results})

if __name__ == '__main__':
    app.run(debug=True)