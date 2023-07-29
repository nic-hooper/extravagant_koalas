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
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io



app = Flask(__name__)
current_year = datetime.datetime.now().year

# Get the current working directory
current_path = os.getcwd()
print(current_path)
with open(current_path+'/pkls/tfidf_vectorizer.pkl', 'rb') as file:
        tfidf_vectorizer = pickle.load(file)


with open(current_path+'/pkls/kmeans.pkl', 'rb') as file:
         kmeans =  pickle.load(file)
         
with open(current_path+'/pkls/documents.pkl', 'rb') as file:
         documents =  pickle.load(file)
documents = documents.reset_index().rename(columns={'level_0': 'documentNum'})

with open(current_path+'/pkls/documents_idf.pkl', 'rb') as file:
         tfidf_df =  pickle.load(file)

metadata = pd.read_csv('../episode_data.csv')


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
   
    # input_tfidf_norm = input_tfidf.toarray().reshape(1, -1) / np.linalg.norm(input_tfidf.toarray())
    # matchingClusters_norm = matchingClusters / np.linalg.norm(matchingClusters, axis=1)[:, np.newaxis]
    # matchingClusters_norm['cosine_similarity'] = cosine_similarity(input_tfidf_norm, matchingClusters_norm)[0]
    # matchingClusters = matchingClusters_norm


    matchingClusters['cosine_similarity'] = cosine_similarity(input_tfidf, matchingClusters)[0]
    matchingClusters = matchingClusters.reset_index().rename(columns={'level_0': 'documentNum'})
    matchingClusters = matchingClusters.sort_values(by='cosine_similarity', ascending=False)
    topTenResults = matchingClusters.head(5)
    resultsReturnerPlots = pd.merge(topTenResults, documents, left_on='documentNum', right_on = 'index', how='inner')

    topTenResults = topTenResults[['documentNum','cosine_similarity']]
    resultsReturner = pd.merge(topTenResults, documents, left_on='documentNum', right_on = 'index', how='inner')
    pattern = r'^(.*?)(?=x)'
    resultsReturner['season'] = resultsReturner['number'].str.extract(pattern)
    pattern = r'x(.*)'
    resultsReturner['episode'] = resultsReturner['number'].str.extract(pattern)
    resultsReturner = pd.merge(resultsReturner,metadata,left_on="number",right_on="ep_id")

    input_tfidf_df = pd.DataFrame(input_tfidf.toarray(), columns=tfidf_vectorizer.get_feature_names_out())
    for index, row in resultsReturnerPlots.iterrows():
        resultsReturnerCopy = resultsReturnerPlots.copy()
        tempReturner = resultsReturnerCopy.loc[[index]]
        tempReturner.reset_index(drop=True, inplace=True)
        input_tfidf_df.reset_index(drop=True, inplace=True)
        tempReturner = tempReturner*input_tfidf_df

        numeric_columns = tempReturner.select_dtypes(include='number').drop('documentNum',axis=1).drop('index_y',axis=1)
        columns_to_keep = numeric_columns.sum().nlargest(10).index
        

            # Select the top 10 columns and other relevant columns from the DataFrame
        result_df = tempReturner[['title_y', 'number', 'cosine_similarity'] + columns_to_keep.tolist()]
        #result_rows.append(result_df)
            # Create a new DataFrame containing only the selected columns and their values
        plot_data = tempReturner[columns_to_keep.tolist()]
        plot_data = plot_data.drop(plot_data.columns[plot_data.eq(0).all()], axis=1)

        plot_data_transposed = plot_data.T

        # Plot each column on a bar chart
        plotHold = plot_data_transposed.plot(kind='bar', legend=False)

        #buf = io.BytesIO()

            # Add labels and title
        plt.xlabel('Contributing Words')
        plt.ylabel('Scores')
        plt.title('Retrieval Explanation')
        plt.tight_layout()
        plt.savefig('static/img/plot_image_'+str(index)+'.png')
        #plt.savefig(buf, format='png')
        plt.close()
    

    resultsJson = resultsReturner.to_json(orient='records')
    resultsJson = ast.literal_eval(resultsJson)
    

    

    return render_template('results.html',current_year=current_year,resultsJson=resultsJson)


if __name__ == '__main__':
    app.run(threaded=False,debug=True)