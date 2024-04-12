from flask import Flask, request, render_template
import pandas as pd
from surprise import Dataset, Reader, SVD

# Load the dataset
result = pd.read_csv("result.csv")

app = Flask(__name__)

# Load the Surprise dataset
reader = Reader(rating_scale=(1, 5))
data = Dataset.load_from_df(result[['userId', 'movieId', 'rating']], reader)

# Train the SVD model
svd_model = SVD(n_factors=60, reg_all=0.04)
trainset = data.build_full_trainset()
svd_model.fit(trainset)

# Function to recommend movies
def recommend_movies(genre, num_ratings):
    selected_columns = result[result['genres'].str.contains(genre)].head(num_ratings)
    user_ratings = pd.DataFrame(columns=['userId', 'movieId', 'rating'])
    for index, row in selected_columns.iterrows():
        rating = input(f'How do you rate "{row["title"]}" on a scale of 1-5? Press n if you have not seen it: ')
        if rating != 'n':
            user_ratings = user_ratings.append({'userId': 100, 'movieId': row['movieId'], 'rating': int(rating)}, ignore_index=True)
    if not user_ratings.empty:
        new_data = Dataset.load_from_df(pd.concat([result[['userId', 'movieId', 'rating']], user_ratings], axis=0), reader)
        svd_model.fit(new_data.build_full_trainset())
        list_of_movies = []
        for m_id in result['movieId'].unique():
            list_of_movies.append((m_id, svd_model.predict(100, m_id)[3]))
        ranked_movies = sorted(list_of_movies, key=lambda x: x[1], reverse=True)
        recommendations = []
        for rec in ranked_movies[:5]:
            movie_title = result[result['movieId'] == int(rec[0])]['title'].iloc[0]
            recommendations.append({'movieId': rec[0], 'title': movie_title})
        return recommendations
    else:
        return []

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        genre = request.form['genre']
        num_ratings = 5
        recommendations = recommend_movies(genre, num_ratings)
        return render_template('recommendations.html', recommendations=recommendations)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
