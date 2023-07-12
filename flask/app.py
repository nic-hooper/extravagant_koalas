from flask import Flask, render_template, url_for, request
import datetime
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import re
from sklearn.metrics.pairwise import cosine_similarity
import os
import pandas as pd
import ast


app = Flask(__name__)
current_year = datetime.datetime.now().year

# Get the current working directory
current_path = os.getcwd()
with open(current_path+'/extravagant_koalas/flask/tfidf_vectorizer.pkl', 'rb') as file:
        tfidf_vectorizer = pickle.load(file)


with open(current_path+'/extravagant_koalas/flask/kmeans.pkl', 'rb') as file:
         kmeans =  pickle.load(file)
         
with open(current_path+'/extravagant_koalas/flask/documents.pkl', 'rb') as file:
         documents =  pickle.load(file)
documents = documents.reset_index().rename(columns={'level_0': 'documentNum'})

with open(current_path+'/extravagant_koalas/flask/documents_idf.pkl', 'rb') as file:
         tfidf_df =  pickle.load(file)


@app.route('/')
def index():
    return render_template('index.html',current_year=current_year)

@app.route('/about-us')
def about_us():
    return render_template('about-us.html',current_year=current_year)

@app.route('/mission-statement')
def mission_statement():
    return render_template('mission-statement.html',current_year=current_year)

@app.route('/get-documents', methods=['POST'])
def get_documents():
    document = request.form.get('text_input')
    pattern2 = r"[^\w\s]"
    document_processed = " ".join(document.strip().lower().replace('\n', ' ').split())
    document_processed = re.sub(pattern2, "", document_processed)
    input_tfidf = tfidf_vectorizer.transform([document_processed])
    predicted_cluster = kmeans.predict(input_tfidf)[0]
    matchingClusters = tfidf_df[tfidf_df['cluster']==predicted_cluster]
    matchingClusters['cosine_similarity'] = cosine_similarity(input_tfidf, matchingClusters)[0]

    matchingClusters = matchingClusters.reset_index().rename(columns={'level_0': 'documentNum'})
    matchingClusters = matchingClusters.sort_values(by='cosine_similarity', ascending=False)
    topTenResults = matchingClusters.head(10)
    print(topTenResults)
    topTenResults = topTenResults[['documentNum','cosine_similarity']]
    resultsReturner = pd.merge(topTenResults, documents, left_on='documentNum', right_on = 'index', how='inner')
    resultsJson = resultsReturner.to_json(orient='records')
    resultsJson = ast.literal_eval(resultsJson)
    print(resultsJson)
    print(type(resultsJson))

    

    return render_template('results.html',current_year=current_year,resultsJson=resultsJson)


if __name__ == '__main__':
    app.run(debug=True)