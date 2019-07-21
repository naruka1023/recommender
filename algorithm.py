from flask import Flask, request, g
import sqlite3 as sql
import pandas as pd
import json

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
s = 'sometfhing'
t = ''
@app.route('/buildAlgorithm')
def buildAlgorithm():
    global s, t
    if 'flag' in request.args:
        if request.args['flag'] == 'related':
            con = sql.connect("eComDB.db")
            cur = con.cursor()
            cur.execute("SELECT title, ingredients FROM items")
            rows = cur.fetchall()
            con.close()
            df = pd.DataFrame(rows, columns=['name', 'ingredients'])
            df['ingredients'] = df['ingredients'].str.split(',')
            df['ingredients'] = df['ingredients'].astype('str')
            tf = TfidfVectorizer(analyzer='word',ngram_range=(1,2),min_df=0, use_idf=True,stop_words='english')
            tfidf_matrix = tf.fit_transform(df['ingredients']) 
            cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
            s = cosine_sim
            t = df
            return 'algorithm created!'
    #     elif request.args['flag'] == 'userPicks':
    # else:
    return 'error 404'


@app.route('/getFoodRecommendations')
def getFoodRecommendations():
    # return request.args['title']
    # return str(t.astype(str).shape)
    global s, t
    indices = pd.Series(t.index, index=t['name'])
    titles = t['name']
    if 'title' in request.args:
        title = request.args['title']
        idx = indices[title]
        sim_scores = list(enumerate(s[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = sim_scores[1:21]
        food_indices = [i[0] for i in sim_scores]
        result = titles.iloc[food_indices].drop_duplicates()[0:10].values
        for i in range(len(result)):
            result[i] = '\"' + result[i] + '\"'
        result = ",".join(result)
        con = sql.connect("eComDB.db")
        cur = con.cursor()
        cur.execute("SELECT title, ingredients, thumbnail FROM items where title in (" + result + ')')
        rows = cur.fetchall()
        final_result = json.dumps(rows)
        con.close()
        return final_result
    else:
        return 'please include title'


if __name__ == '__main__':
   app.run(debug = True)