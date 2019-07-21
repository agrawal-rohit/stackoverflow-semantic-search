import pandas as pd
from utils import preprocess_text
import numpy as np
import gensim
from sklearn.metrics.pairwise import cosine_similarity

data = pd.read_csv('../../Preprocessed_data.csv')
all_title_embeddings = pd.read_csv('../../models/title_embeddings.csv').values

# Import saved Wordvec Embeddings
w2v_model = gensim.models.word2vec.Word2Vec.load('../../models/SO_word2vec_embeddings.bin')

def question_to_vec(question, embeddings, dim=300):
    question_embedding = np.zeros(dim)
    valid_words = 0
    for word in question.split(' '):
        if word in embeddings:
            valid_words += 1
            question_embedding += embeddings[word]
    if valid_words > 0:
        return question_embedding/valid_words
    else:
        return question_embedding

def searchresults(search_string, num_results):
    search_string = preprocess_text(search_string)
    search_vect = np.array([question_to_vec(search_string, w2v_model)])

    search_results = []

    cosine_similarities = pd.Series(cosine_similarity(search_vect, all_title_embeddings)[0])

    cosine_similarities = cosine_similarities*(1 + 0.4*data.overall_scores_norm + 0.1*(data.sentiment_polarity))

    for i,j in cosine_similarities.nlargest(int(num_results)).iteritems():
        output = ''
        for t in data.question_content[i][:200].split():
            if t.lower() in search_string:
                output += " <b style='color: #464646'>"+str(t)+"</b>"
            else:
                output += " "+str(t)
        temp = {
            'title': str(data.original_title[i]),
            'url': str(data.question_url[i]),
            'similarity_score': str(j)[:5],
            'votes': str(data.overall_scores[i]),
            'body':str(output)
        }
        search_results.append(temp)
    return search_results
