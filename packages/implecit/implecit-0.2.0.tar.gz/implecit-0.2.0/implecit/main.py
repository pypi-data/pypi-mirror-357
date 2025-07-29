import pyperclip


class ClipboardHelper:
    def __init__(self):
        self.methods_info = {
            "weighted_rating": "",
            "item_properties": "",
            "svd_ratings": "SVD on ml-small",
            "svd_1000": "SVD on IMDB-1000",
            "IB_UB": "Item-based + User-based",
            "plot_desc": "Plot Description Based Recommende",
            "hyp_cas": "Реализует гибридную каскадную фильтрацию (svd+Контентная фильтрация)",
            "ALS_BPR": "",
            "light_fw_warp": "",
            "imp_retail": "ALS+BPR on retail",
            "light_gcn_ml": "Light GCN на MovieLens",

        }

    def weighted_rating(self):
        """Построение простой рекомендательной системы."""

        code = """
import pandas as pd
import numpy as np


df = pd.read_csv("C://Users/Cristin/Documents/Рек_сист/data/movies_metadata2.csv", encoding='latin-1')
df.head()

m = df['vote_count'].quantile(0.80)
q_movies = df[(df['runtime'] >= 45) & (df['runtime'] <= 300)]

q_movies = q_movies[q_movies['vote_count'] >= m]

q_movies.shape

C = df['vote_average'].mean()

def weighted_rating(x, m=m, C=C):
    v = x['vote_count']
    R = x['vote_average']
    # Compute the weighted score
    return (v/(v+m) * R) + (m/(m+v) * C)
    
q_movies['score'] = q_movies.apply(weighted_rating, axis=1)
q_movies = q_movies.sort_values('score', ascending=False)
q_movies[['title', 'vote_count', 'vote_average', 'score', 'runtime']].head(25)
"""

        pyperclip.copy(code)

    def light_fw_warp(self):
        """Построение простой рекомендательной системы."""

        code = """
from lightfm import LightFM
from lightfm.datasets import fetch_movielens
from lightfm.evaluation import precision_at_k, recall_at_k, auc_score
import numpy as np
import matplotlib.pyplot as pltq_movies[['title', 'vote_count', 'vote_average', 'score', 'runtime']].head(25)

data_rating_5 = fetch_movielens(min_rating=5.0)
data_rating_4 = fetch_movielens(min_rating=4.0)
data_rating_3 = fetch_movielens(min_rating=3.0)

data_rating_5['item_features'].shape,data_rating_5['test'].shape
model_rating_5 = LightFM(loss='warp')
model_rating_5.fit(data_rating_5['train'], epochs=30, num_threads=2)
n = data_rating_5['train'].shape[1]
user_id = 0
rec = model_rating_5.predict(user_id, np.arange(n))
top_10 = np.argsort(-rec)[:10]

print(f"\nТоп-10 рекомендаций для пользователя {user_id}:")
print(top_10)

# k = 10
train_precision_5_10 = np.mean(precision_at_k(model_rating_5, data_rating_5['train'], k=10, num_threads=2))
train_auc_5 = np.mean(auc_score(model_rating_5, data_rating_5['train'], num_threads=2))
test_precision_5_10 = np.mean(precision_at_k(model_rating_5, data_rating_5['test'], k=10, num_threads=2))
test_auc_5 = np.mean(auc_score(model_rating_5, data_rating_5['test'], num_threads=2))

# k = 5
train_precision_5_5 = np.mean(precision_at_k(model_rating_5, data_rating_5['train'], k=5, num_threads=2))
test_precision_5_5 = np.mean(precision_at_k(model_rating_5, data_rating_5['test'], k=5, num_threads=2))

print('Train precision (k=10): {:.2f}'.format(train_precision_5_10))
print('Train precision (k=5): {:.2f}'.format(train_precision_5_5))
print('Train AUC: {:.2f}'.format(train_auc_5))
print('Test precision (k=10): {:.2f}'.format(test_precision_5_10))
print('Test precision (k=5): {:.2f}'.format(test_precision_5_5))
print('Test AUC: {:.2f}'.format(test_auc_5))
    """

        pyperclip.copy(code)

    def imp_retail(self):
        """implicit om retail rocket"""

        code = """
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import implicit
from scipy.sparse import coo_matrix, csr_matrix
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

events = pd.read_csv('events.csv')

events.head()
print(f"\nРазмер датасета: {events.shape}")

event_weights = {'view': 1.0,'addtocart': 1.5,'transaction': 3}

events['weight'] = events['event'].map(event_weights)

user_item_interactions = events.groupby(['visitorid', 'itemid']).agg({
    'weight': 'sum',
    'event': 'count'
}).reset_index()

user_item_interactions.columns = ['user_id', 'item_id', 'rating', 'interaction_count']

user_encoder = LabelEncoder()
item_encoder = LabelEncoder()

user_item_interactions['user_encoded'] = user_encoder.fit_transform(user_item_interactions['user_id'])
user_item_interactions['item_encoded'] = item_encoder.fit_transform(user_item_interactions['item_id'])

train_data, test_data = train_test_split(user_item_interactions, 
                                         test_size=0.2, random_state=42,shuffle=True)


def create_interaction_matrix(data, n_users, n_items):
    return coo_matrix((
        data['rating'].values,
        (data['user_encoded'].values, data['item_encoded'].values)
    ), shape=(n_users, n_items)).tocsr()

n_users = user_item_interactions['user_encoded'].nunique()
n_items = user_item_interactions['item_encoded'].nunique()

train_matrix = create_interaction_matrix(train_data, n_users, n_items)
test_matrix = create_interaction_matrix(test_data, n_users, n_items)

def get_precision_recall(true_matrix, pred_matrix, k=10):
    true_items = true_matrix.tolil().rows
    pred_items = np.argsort(-pred_matrix, axis=1)[:, :k]
    
    precisions = []
    recalls = []
    
    for user_id in range(len(true_items)):
        true_set = set(true_items[user_id])
        pred_set = set(pred_items[user_id])
        
        if len(true_set) > 0:
            precision = len(true_set & pred_set) / k
            recall = len(true_set & pred_set) / len(true_set)
            
            precisions.append(precision)
            recalls.append(recall)
    
    return np.mean(precisions), np.mean(recalls)

def get_coverage(pred_matrix, n_items, k=10):
    pred_items = np.argsort(-pred_matrix, axis=1)[:, :k]
    unique_items = np.unique(pred_items.flatten())
    return len(unique_items) / n_items

als_model = implicit.als.AlternatingLeastSquares(factors=100, 
    regularization=0.01, iterations=25,random_state=42)
als_model.fit(train_matrix)

als_model.recommend_all(test_matrix)

bpr_model = implicit.bpr.BayesianPersonalizedRanking(factors=100, regularization=0.01, 
    iterations=25,random_state=42)
bpr_model.fit(train_matrix)

bpr_model.recommend_all(test_matrix)

als_predictions = als_model.recommend_all(test_matrix)
bpr_predictions = bpr_model.recommend_all(test_matrix)

k_values = [5, 10, 15, 20]
results = []

for k in k_values:
    als_precision, als_recall = get_precision_recall(test_matrix, als_predictions, k)
    als_coverage = get_coverage(als_predictions, n_items, k)
    
    bpr_precision, bpr_recall = get_precision_recall(test_matrix, bpr_predictions, k)
    bpr_coverage = get_coverage(bpr_predictions, n_items, k)
    
    results.append({'k': k,'ALS_Precision': als_precision,'ALS_Recall': als_recall,
                    'BPR_Precision': bpr_precision,'BPR_Recall': bpr_recall,})

results_df = pd.DataFrame(results)

fig, axes = plt.subplots(1, 2)

axes[0].plot(results_df['k'], results_df['ALS_Precision'], 'o-', label='ALS', linewidth=2, markersize=8)
axes[0].plot(results_df['k'], results_df['BPR_Precision'], 's-', label='BPR', linewidth=2, markersize=8)
axes[0].set_title('Precision@K', fontsize=14, fontweight='bold')
axes[0].set_xlabel('K')
axes[0].set_ylabel('Precision')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

axes[1].plot(results_df['k'], results_df['ALS_Recall'], 'o-', label='ALS', linewidth=2, markersize=8)
axes[1].plot(results_df['k'], results_df['BPR_Recall'], 's-', label='BPR', linewidth=2, markersize=8)
axes[1].set_title('Recall@K', fontsize=14, fontweight='bold')
axes[1].set_xlabel('K')
axes[1].set_ylabel('Recall')
axes[1].legend()
axes[1].grid(True, alpha=0.3)
    """

        pyperclip.copy(code)

    def item_properties(self):
        """item_properties"""

        code = """
import numpy as np 
import pandas as pd 
import seaborn as sns
import matplotlib.pyplot as plt

items1 = pd.read_csv('2/item_properties_part1.csv')
items2 = pd.read_csv('2/item_properties_part2.csv')
items = pd.concat([items1, items2])
items.head(10)
import datetime

times =[]
for i in items['timestamp']:
    times.append(datetime.datetime.fromtimestamp(i//1000.0)) 
items['timestamp'] = times
items.head()

events = pd.read_csv('2/events.csv')
times =[]
for i in events['timestamp']:
    times.append(datetime.datetime.fromtimestamp(i//1000.0)) 
events['timestamp'] = times
events.head(10)

events['event'].value_counts()

shop = events.groupby(['itemid', 'event']).size().unstack(fill_value=0)


shop['total_interactions'] = shop.sum(axis=1)
popular_items = shop.sort_values(by='total_interactions', ascending=False)

print("топ-10 товаров по количеству взаимодействий")
popular_items.head(10)
print("топ-10 товаров по количеству покупок")
popular_items.sort_values(by='transaction', ascending=False).head(10)
def recommend(data, top_n=10):
    return data.sort_values(by='transaction').head(top_n).index.tolist()

print('рекомендует наиболее популярные товары на основе количества продаж')
recommend(popular_items)
"""
        pyperclip.copy(code)

    def svd_ratings(self):
        """svd"""
        code = """
from surprise import SVD, Dataset, Reader, accuracy
from surprise.model_selection import cross_validate, train_test_split
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

df = pd.read_csv('ml-latest-small/ratings.csv')
df.head(5)

 ratings_df = pd.read_csv('ml-latest-small/ratings.csv')
rating_matrix = ratings_df.pivot(index='userId', columns='movieId', values='rating')
plt.figure(figsize=(8, 6))
ratings_df['rating'].hist(bins=10)
plt.xlabel('Рейтинг')
plt.ylabel('Количество')
plt.title('Распределение рейтингов')
plt.show()

rating_matrix = df.pivot(index='userId', columns='movieId', values='rating')
rating_matrix.head()

reader = Reader(line_format='user item rating timestamp', sep=',', skip_lines=1)
data = Dataset.load_from_file('ml-latest-small/ratings.csv', reader=reader)

trainset, testset = train_test_split(data, test_size=0.25, random_state=42)
algo = SVD()
algo.fit(trainset)
predictions = algo.test(testset)
predictions[:5]

accuracy.rmse(predictions, verbose=True)
accuracy.mae(predictions, verbose=True)
cv_results = cross_validate(algo, data, measures=['RMSE', 'MAE'], cv=5, verbose=True)

print("CV RMSE:", sum(cv_results['test_rmse']) / len(cv_results['test_rmse']))
print("CV MAE:", sum(cv_results['test_mae']) / len(cv_results['test_mae']))

pred = []

for uid, iid, true_r, est, _ in predictions:
    pred.append([uid, iid, true_r, est, abs(true_r - est)])

pred_df = pd.DataFrame(pred, columns=['userId', 'movieId', 'true_rating', 'pred_rating', 'abs_error'])
scs = pred_df[pred_df['abs_error'] < 0.5].sort_values(by='abs_error')
unscs = pred_df[pred_df['abs_error'] > 1.0].sort_values(by='abs_error', ascending=False)

print("Удачные рекомендации (примеры):")
print(scs.head(5))

print("Неудачные рекомендации (примеры):")
print(unscs.head(5))

acc = successful.shape[0] / (successful.shape[0] + unsuccessful.shape[0])
acc
    """
        pyperclip.copy(code)

    def svd_1000(self):
        """svd on imdb_top_1000"""

        code = """
from sklearn.decomposition import TruncatedSVD
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler


scaler = MinMaxScaler()
data = pd.read_csv('imdb_top_1000.csv')
genres = data['Genre'].str.get_dummies(sep=', ')
data = pd.concat([data, genres], axis=1)
ratings_matrix = data.groupby('Series_Title')[genres.columns].mean()
ratings_matrix = ratings_matrix.fillna(0)
train_data, test_data = train_test_split(data, test_size=0.2, random_state=42)
common_movies = list(ratings_matrix.index.intersection(test_data['Series_Title']))
filtered_data = test_data[test_data['Series_Title'].isin(common_movies)].reset_index(drop=True)
filtered_data = filtered_data
filtered_ratings_matrix = ratings_matrix.loc[common_movies]
svd = TruncatedSVD(n_components=10, random_state=42)
tfidf = TfidfVectorizer(stop_words='english')
latent_factors = svd.fit_transform(filtered_ratings_matrix)
normalized_latent_factors = scaler.fit_transform(latent_factors)
content_matrix = tfidf.fit_transform(filtered_data['Overview'].fillna(''))
svd_similarity = cosine_similarity(normalized_latent_factors)
similarity = cosine_similarity(content_matrix)
cosine_similarity(content_matrix).shape, filtered_data['Overview'].shape

from sklearn.preprocessing import MinMaxScaler


scaler = MinMaxScaler()
latent_factors = svd.fit_transform(filtered_ratings_matrix)
normalized_latent_factors = scaler.fit_transform(latent_factors)
cosine_similarity(normalized_latent_factors).shape

alpha = 0.5
combined_scores = alpha * svd_similarity + (1 - alpha) * similarity

def recommend_movies(movie_title, top_n=10):
    movie_idx = filtered_data.index[filtered_data['Series_Title'] == movie_title].tolist()[0]
    movie_scores = list(enumerate(combined_scores[movie_idx]))
    sorted_scores = sorted(movie_scores, key=lambda x: x[1], reverse=True)
    
    print(f"\nTop {top_n} recommended movies similar to '{movie_title}':")
    for idx, score in sorted_scores[1:top_n + 1]:
        print(f"{filtered_data.iloc[idx]['Series_Title']} (Similarity Score: {score:.3f})")

recommend_movies('12 Years a Slave', top_n=10)

from sklearn.metrics import mean_squared_error, mean_absolute_error
import numpy as np


def rmse_mae(true_ratings, predicted_ratings):
    rmse = np.sqrt(mean_squared_error(true_ratings, predicted_ratings))
    mae = mean_absolute_error(true_ratings, predicted_ratings)
    return rmse, mae

def scoring(model, train_data, test_data):
    stor = []
    for idx, row in test_data.iterrows():
        movie_idx = train_data.index[train_data['Series_Title'] == row['Series_Title']].tolist()
        if movie_idx:
            predicted_score = model[movie_idx[0]].mean() 
        else:
            predicted_score = 0 
        stor.append(predicted_score)
    return stor
    

test_svd_ratings = scoring(svd_similarity, train_data, test_data)
test_content_ratings = scoring(similarity, train_data, test_data)
test_hybrid_ratings = scoring(combined_scores, train_data, test_data)


true_ratings = test_data['IMDB_Rating'].values
rmse_svd, mae_svd = rmse_mae(true_ratings, test_svd_ratings)
rmse_content, mae_content = rmse_mae(true_ratings, test_content_ratings)
rmse_hybrid, mae_hybrid = rmse_mae(true_ratings, test_hybrid_ratings)


print(f"SVD Model: RMSE = {rmse_svd:.3f}, MAE = {mae_svd:.3f}")
print(f"Content-Based Model: RMSE = {rmse_content:.3f}, MAE = {mae_content:.3f}")
print(f"Hybrid Model: RMSE = {rmse_hybrid:.3f}, MAE = {mae_hybrid:.3f}")

def prk(predicted_scores, true_scores, k=10):
    top_k_indices = np.argsort(predicted_scores)[-k:][::-1]
    relevant = np.sum(true_scores[top_k_indices] >= 8)
    precision = relevant / k
    recall = relevant / np.sum(true_scores >= 8)
    return precision, recall

precision_svd, recall_svd = prk(np.array(test_svd_ratings), true_ratings, k=10)
precision_content, recall_content = prk(np.array(test_content_ratings), true_ratings, k=10)
precision_hybrid, recall_hybrid = prk(np.array(test_hybrid_ratings), true_ratings, k=10)


print(f"SVD Model: Precision = {precision_svd:.3f}, Recall = {recall_svd:.3f}")
print(f"Content-Based Model: Precision = {precision_content:.3f}, Recall = {recall_content:.3f}")
print(f"Hybrid Model: Precision = {precision_hybrid:.3f}, Recall = {recall_hybrid:.3f}")
    """

        pyperclip.copy(code)

    def IB_UB(self):
        """Item_based + User_based"""

        code = """
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from sklearn.model_selection import train_test_split

df = pd.read_csv('ml-latest-small/ratings.csv')
df.head()

df.dropna(inplace=True)
user_item_matrix = df.pivot_table(index='userId', columns='movieId', 
                                  values='rating', fill_value=0)
user_similarity = cosine_similarity(user_item_matrix)
user_similarity_df = pd.DataFrame(user_similarity, index=user_item_matrix.index, columns=user_item_matrix.index)
def find_similar_users(user_id, top_n=5):
    sim_users = user_similarity_df[user_id].sort_values(ascending=False)
    sim_users = sim_users.drop(user_id)
    top_sim_users = sim_users.head(top_n)

    return top_sim_users
    
item_similarity = cosine_similarity(user_item_matrix.T)
item_similarity_df = pd.DataFrame(item_similarity, index=user_item_matrix.columns, columns=user_item_matrix.columns)

def IB_rec(user_id, num_rec=5):
    user_movies = user_item_matrix.loc[user_id]
    watched_movies = user_movies[user_movies > 0].index
    rec = {}

    for movie in watched_movies:
        sim_movies = item_similarity_df[movie].sort_values(ascending=False)[1:6]
        for sim_movie, sim_score in sim_movies.items():
            if sim_movie not in watched_movies:
                rec[sim_movie] = rec.get(sim_movie, 0) + sim_score * user_movies[movie]

    rec_movies = sorted(rec.items(), key=lambda x: x[1], reverse=True)[:num_rec]
    return [movie for movie, score in rec_movies]     
    
def predict_user_ratings(user_id):
    user_ratings = user_item_matrix.loc[user_id]
    pred_ratings = user_ratings.copy()

    for movie in user_item_matrix.columns:
        if user_ratings[movie] == 0:  
            sim_users = user_similarity_df[user_id].sort_values(ascending=False)[1:]
            weighted_sum, sim_sum = 0, 0

            for sim_user, sim_score in sim_users.items():
                rating = user_item_matrix.loc[sim_user, movie]
                if rating > 0:
                    weighted_sum += sim_score * rating
                    sim_sum += sim_score

            if sim_sum > 0:
                pred_ratings[movie] = weighted_sum / sim_sum

    return pred_ratings  
    
def rec_items(user_id):
    user_ratings = user_item_matrix.loc[user_id]
    pred_ratings = user_ratings.copy()

    for movie in user_item_matrix.columns:
        if user_ratings[movie] == 0:
            sim_movies = item_similarity_df[movie].sort_values(ascending=False)[1:]
            weighted_sum, sim_sum = 0, 0

            for sim_movie, sim_score in sim_movies.items():
                rating = user_ratings[sim_movie]
                if rating > 0:
                    weighted_sum += sim_score * rating
                    sim_sum += sim_score

            if sim_sum > 0:
                pred_ratings[movie] = weighted_sum / sim_sum

    return pred_ratings.sort_values(ascending=False)                 
    """

        pyperclip.copy(code)

    def plot_desc(self):
        code = """
import pandas as pd
import numpy as np

df = pd.read_csv('./data/metadata_clean.csv')
df.head()

orig_df = pd.read_csv('./data/movies_metadata.csv', low_memory=False)
df['overview'], df['id'] = orig_df['overview'], orig_df['id']
df.head()

from sklearn.feature_extraction.text import TfidfVectorizer

tfidf = TfidfVectorizer(stop_words='english')
df['overview'] = df['overview'].fillna('')
tfidf_matrix = tfidf.fit_transform(df['overview'])
tfidf_matrix.shape

from sklearn.metrics.pairwise import linear_kernel

cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
indices = pd.Series(df.index, index=df['title']).drop_duplicates()
def content_recommender(title, cosine_sim=cosine_sim, df=df, indices=indices):
    idx = indices[title]

    sim_scores = list(enumerate(cosine_sim[idx]))

    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:11]

    movie_indices = [i[0] for i in sim_scores]

    precision = df.iloc[movie_indices]['vote_average'].sum() / 10.0
    score = round(precision, 2)
    print(f"Precision: {score}")

    return df['title'].iloc[movie_indices]
    
content_recommender('The Lion King')
    """

        pyperclip.copy(code)

    def hyp_cas(self):

        code = """
def hybrid_cascade_filtering(data, n_clusters=3, content_data=None, item_id_col=None, content_cols=None):

    if content_data is not None and item_id_col is not None and content_cols is not None:
        content_data = content_data.set_index(item_id_col)
    knn = KNNBasic(k=50, sim_options={'name': 'pearson_baseline', 'user_based': True})  # Ориентируемся на пользователей
    trainset = data.build_full_trainset()  # Обучаем на всем датасете для кластеризации
    knn.fit(trainset)


    user_embeddings = []
    for user_id in trainset.all_users():
        user_inner_id = user_id
        neighbors = knn.get_neighbors(user_inner_id, k=50) # Находим ближайших соседей, k можно настроить
        user_embedding=[]
        for neighbor_inner_id in neighbors:
            temp=list(map(list, knn.trainset.ur[neighbor_inner_id]))
            user_embedding.extend(temp)    

        user_embedding = np.mean(user_embedding, axis=0)
        user_embeddings.append(user_embedding)

    user_embeddings = np.array(user_embeddings)

    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10) # Явно указываем n_init
    user_clusters = kmeans.fit_predict(user_embeddings)


    results = {}

    for cluster_id in range(n_clusters):
        print(f"Обработка кластера: {cluster_id}")
        cluster_user_ids = [trainset.to_raw_uid(i) for i, cluster in enumerate(user_clusters) if cluster == cluster_id]
        cluster_data = data.build_full_trainset().build_testset()
        cluster_data = [x + (None,) for x in cluster_data if x[0] in cluster_user_ids] # Оставляем только взаимодействия пользователей из этого кластера
        cluster_data = pd.DataFrame(data.construct_testset(cluster_data))

        reader = Reader(rating_scale=(1,5))
        cluster_data = DatasetAutoFolds.load_from_df(cluster_data, reader=reader)
        
        cluster_trainset, cluster_testset = train_test_split(cluster_data, test_size=0.2, random_state=42) # Теперь разделяем на train/test

        svd = SVD(n_factors=50, random_state=42)  # Настраиваем параметры SVD
        svd.fit(cluster_trainset)
        svd_predictions = svd.test(cluster_testset)
        rmse_svd = accuracy.rmse(svd_predictions, verbose=False)
        mae_svd = accuracy.mae(svd_predictions, verbose=False)
        print(f"  SVD: RMSE = {rmse_svd:.4f}, MAE = {mae_svd:.4f}")

        if content_data is not None and item_id_col is not None and content_cols is not None:
            # Создаем матрицу контентных признаков
            content_matrix = cosine_similarity(content_data[content_cols])
            content_matrix = pd.DataFrame(content_matrix, columns=content_data.index, index=content_data.index)
            
            # Функция для улучшения предсказания с помощью контентной фильтрации
            def refine_prediction(user_id, item_id, svd_prediction):
                try:
                    similar_items_indices = np.argsort(content_matrix[item_id])[::-1][1:11] # 10 наиболее похожих
                    similar_items = content_data.iloc[similar_items_indices].index.tolist()
                            
                    relevant_predictions = [svd.predict(user_id, item).est for item in similar_items if item in dict(cluster_trainset.ur[cluster_trainset.to_inner_uid(user_id)])] # Проверяем, что пользователь оценил фильм
                    if relevant_predictions:
                        content_based_estimate = np.mean(relevant_predictions)
                        # Комбинируем предсказания (можно настроить вес)
                        refined_prediction = 0.7 * svd_prediction + 0.3 * content_based_estimate
                        return refined_prediction
                    else:
                        return svd_prediction # Если нет оценок похожих фильмов, возвращаем SVD предсказание
                except:
                    return svd_prediction # В случае ошибки возвращаем SVD предсказание


            refined_predictions = []
            for uid, iid, r_true, est, _ in svd_predictions:
                refined_est = refine_prediction(uid, iid, est)
                refined_predictions.append((uid, iid, r_true, refined_est, None))  # Создаем кортеж в формате Surprise

            rmse_refined = accuracy.rmse(refined_predictions, verbose=False)
            mae_refined = accuracy.mae(refined_predictions, verbose=False)
            print(f"  SVD + Content: RMSE = {rmse_refined:.4f}, MAE = {mae_refined:.4f}")
        else:
            rmse_refined = rmse_svd
            mae_refined = mae_svd
            refined_predictions = svd_predictions
            print("  Контентная фильтрация не применена (недостаточно данных).")

        results[cluster_id] = {
            'rmse_svd': rmse_svd,
            'mae_svd': mae_svd,
            'rmse_refined': rmse_refined,
            'mae_refined': mae_refined,
            'predictions': refined_predictions
        }

    return results
if __name__ == '__main__':
    
    ratings = pd.read_csv('./ml-latest-small/ratings.csv')
    movies = pd.read_csv('./ml-latest-small/movies.csv')
    
    reader = Reader(rating_scale=(1, 5))  # Шкала оценок

    data = DatasetAutoFolds.load_from_df(ratings[['userId', 'movieId', 'rating']], reader)

    trainset = data.build_full_trainset()
    
    movies['genres'] = movies['genres'].apply(lambda x: x.split('|'))
    movies = movies.explode('genres')
    movies = pd.get_dummies(movies, columns=['genres'])
    movies = movies.groupby('movieId').max().reset_index()

    results = hybrid_cascade_filtering(
        data,
        n_clusters=3,
        content_data=movies,
        item_id_col='movieId',
        content_cols=[col for col in movies.columns if col.startswith('genres_')]
    )

    # # 3. Вывод результатов
    for cluster_id, cluster_results in results.items():
        print(f"\nРезультаты для кластера {cluster_id}:")
        print(f"  SVD: RMSE = {cluster_results['rmse_svd']:.4f}, MAE = {cluster_results['mae_svd']:.4f}")
        print(f"  SVD + Content: RMSE = {cluster_results['rmse_refined']:.4f}, MAE = {cluster_results['mae_refined']:.4f}")
    """

        pyperclip.copy(code)

    def RNN_pred(self):
        code = """
import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader


corpus = df['text'].str.cat(sep=" ")
chars = sorted(list(set(corpus)))
vocab_size = len(chars)
char2idx = {ch: i for i, ch in enumerate(chars)}
idx2char = {i: ch for i, ch in enumerate(chars)}
encoded = np.array([char2idx[ch] for ch in corpus], dtype=np.int64)

seq_len = 100
step = 1

class NextTokenDataset(Dataset):
    def __init__(self, data, seq_len, step):
        self.data = data
        self.seq_len = seq_len
        self.step = step
        self.num_samples = (len(data) - seq_len) // step
    def __len__(self):
        return self.num_samples
    def __getitem__(self, idx):
        i = idx * self.step
        x = self.data[i:i+self.seq_len]
        y = self.data[i+1:i+self.seq_len+1]
        return torch.tensor(x, dtype=torch.long), torch.tensor(y, dtype=torch.long)

dataset = NextTokenDataset(encoded, seq_len, step)
dataloader = DataLoader(dataset, batch_size=64, shuffle=True)

class RNNModel(nn.Module):
    def __init__(self, vocab_size, embed_dim, hidden_dim):
        super(RNNModel, self).__init__()
        self.embed = nn.Embedding(vocab_size, embed_dim)
        self.rnn = nn.GRU(embed_dim, hidden_dim, batch_first=True)
        self.fc = nn.Linear(hidden_dim, vocab_size)
    def forward(self, x, hidden=None):
        x = self.embed(x)
        out, hidden = self.rnn(x, hidden)
        logits = self.fc(out)
        return logits, hidden

model = RNNModel(vocab_size, 64, 128)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
optimizer = optim.Adam(model.parameters(), lr=1e-3)
criterion = nn.CrossEntropyLoss()

epochs = 3
model.train()
for epoch in range(epochs):
    total_loss = 0
    for x, y in dataloader:
        x, y = x.to(device), y.to(device)
        optimizer.zero_grad()
        logits, _ = model(x)
        loss = criterion(logits.view(-1, vocab_size), y.view(-1))
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
    print("Epoch", epoch+1, "Loss", total_loss/len(dataloader))

def predict_next_token(model, input_seq, temperature=1.0):
    model.eval()
    x = torch.tensor([char2idx[ch] for ch in input_seq], dtype=torch.long).unsqueeze(0).to(device)
    with torch.no_grad():
        logits, _ = model(x)
    last_logits = logits[0, -1, :] / temperature
    probs = torch.softmax(last_logits, dim=-1)
    token = torch.multinomial(probs, 1).item()
    return idx2char[token]

input_seq = "The"

predict_next_token(model, input_seq)
    """

        pyperclip.copy(code)

    def ALS_BPR(self):

        code = """
import random
import numpy as np
import pandas as pd

import implicit

seed = 123
random_state = 123

random.seed(seed)
np.random.seed(seed)

from watermark import watermark

print(watermark(python=True, watermark=True, iversions=True, globals_=globals()))

import implicit
from scipy.sparse import coo_matrix
from pprint import pprint

df = pd.read_csv("./ml100k/u.data", sep="\t", names=["user_id", "item_id", "rating", "timestamp"])
rows = df["user_id"].astype(int)
cols = df["item_id"].astype(int)
values = df["rating"].astype(float)

df.head()

R = coo_matrix((values, (rows, cols)))
R = R.tocsr()

model = implicit.als.AlternatingLeastSquares(factors=20, regularization=0.1, iterations=50)
model.fit(R)


U = model.user_factors
I = model.item_factors


print(U.round(2))
print(I.round(2))

import implicit
from scipy.sparse import coo_matrix
from pprint import pprint

df = pd.read_csv("./ml100k/u.data", sep="\t", names=["user_id", "item_id", "rating", "timestamp"])
rows = df["user_id"].astype(int)
cols = df["item_id"].astype(int)
values = df["rating"].astype(float)

df.head()

R = coo_matrix((values, (rows, cols)))

R = R.tocsr()

model = implicit.bpr.BayesianPersonalizedRanking(factors=20, regularization=0.1, iterations=50)
model.fit(R)

U = model.user_factors
I = model.item_factors

print(U.round(2))
print(I.round(2))

import implicit
import pandas as pd
import numpy as np

from scipy.sparse import coo_matrix
from sklearn.model_selection import train_test_split

df = pd.read_csv("./ml100k/u.data", sep="\t", names=["user_id", "item_id", "rating", "timestamp"])

train, test = train_test_split(df, test_size=0.2, stratify=df["user_id"], shuffle=True, random_state=seed)

train_matrix = coo_matrix((train["rating"], (train["user_id"], train["item_id"])))
test_matrix = coo_matrix((test["rating"], (test["user_id"], test["item_id"])))

train_matrix = train_matrix.tocsr()
test_matrix = test_matrix.tocsr()

def get_precision(true_matrix, pred_matrix, k=10):
    true_items = true_matrix.tolil().rows

    pred_items = np.argsort(-pred_matrix, axis=1)[:, :k]

    precisions = []
    for user_id in range(len(true_items)):
        true_set = set(true_items[user_id])
        pred_set = set(pred_items[user_id])

        if len(true_set) > 0:
            precision = len(true_set & pred_set) / min(len(true_set), k)
            precisions.append(precision)

    return np.mean(precisions)
    
als_model = implicit.als.AlternatingLeastSquares(factors=20, regularization=0.1, iterations=50)
als_model.fit(train_matrix)

test_predictions = als_model.recommend_all(test_matrix)

true_matrix = test_matrix  # Матрица фактической оценки тестовых данных
pred_matrix = als_model.recommend_all(test_matrix)  # Предсказание по модели ALS

precision = get_precision(true_matrix, pred_matrix)
print(f"ALS Model Precision: {precision:.3f}")

bpr_model = implicit.bpr.BayesianPersonalizedRanking(factors=20, regularization=0.1, iterations=50)
bpr_model.fit(train_matrix)

test_predictions = bpr_model.recommend_all(test_matrix)

precision = get_precision(test_matrix, test_predictions)
print(f"BPR-модель Precision : {precision:.3f}")
    """

        pyperclip.copy(code)

    def light_gcn_ml(self):
        code = """
import pandas as pd
import torch
from sklearn.model_selection import train_test_split
from torch_geometric.data import Data
import numpy as np

df = pd.read_csv("https://files.grouplens.org/datasets/movielens/ml-100k/u.data",
                 sep="\t", names=["user", "item", "rating", "timestamp"])
df = df[df["rating"] >= 4]

user2id = {u: i for i, u in enumerate(df["user"].unique())}
item2id = {i: j for j, i in enumerate(df["item"].unique())}
df["user"] = df["user"].map(user2id)
df["item"] = df["item"].map(item2id)

num_users = df["user"].nunique()
num_items = df["item"].nunique()
num_nodes = num_users + num_items

train_df, test_df = train_test_split(df, test_size=0.2, stratify=df["user"])

# Граф: пользователь->фильм + фильм->пользователь (bidirectional)
def build_edge_index(df, num_users):
    user_nodes = df["user"].values
    item_nodes = df["item"].values + num_users

    edge_u2i = np.vstack([user_nodes, item_nodes])
    edge_i2u = np.vstack([item_nodes, user_nodes])
    edge_index = np.hstack([edge_u2i, edge_i2u])
    return torch.LongTensor(edge_index)

edge_index = build_edge_index(train_df, num_users)
data = Data(edge_index=edge_index, num_nodes=num_nodes)

import torch.nn as nn
from torch_geometric.utils import degree

class LightGCN(torch.nn.Module):
    def __init__(self, num_users, num_items, emb_dim=64, num_layers=3):
        super().__init__()
        self.num_users = num_users
        self.num_items = num_items
        self.embedding = nn.Embedding(num_users + num_items, emb_dim)
        nn.init.xavier_uniform_(self.embedding.weight)
        self.num_layers = num_layers

    def forward(self, edge_index):
        x = self.embedding.weight
        all_emb = [x]

        deg = degree(edge_index[0], num_nodes=x.size(0)).clamp(min=1)
        norm = deg[edge_index[0]].pow(-0.5) * deg[edge_index[1]].pow(-0.5)

        for _ in range(self.num_layers):
            row, col = edge_index
            m = x[col] * norm.unsqueeze(1)
            agg = torch.zeros_like(x).index_add_(0, row, m)
            x = agg
            all_emb.append(x)

        final_emb = sum(all_emb) / (self.num_layers + 1)
        return final_emb[:self.num_users], final_emb[self.num_users:]

    def predict(self, user_emb, item_emb):
        return torch.matmul(user_emb, item_emb.t())

import torch.nn.functional as F
from tqdm import trange

def sample_bpr(df, num_users, num_items, n_samples=512):
    users = torch.randint(0, num_users, (n_samples,))
    pos_items = []
    neg_items = []

    user_pos = df.groupby("user")["item"].apply(set).to_dict()

    for u in users:
        u = u.item()
        pos = np.random.choice(list(user_pos[u]))
        while True:
            neg = np.random.randint(0, num_items)
            if neg not in user_pos[u]:
                break
        pos_items.append(pos)
        neg_items.append(neg)

    return users, torch.LongTensor(pos_items), torch.LongTensor(neg_items)

model = LightGCN(num_users, num_items)
optimizer = torch.optim.Adam(model.parameters(), lr=0.01)

for epoch in trange(10):
    model.train()
    user_emb, item_emb = model(data.edge_index)

    users, pos_items, neg_items = sample_bpr(train_df, num_users, num_items)

    u_emb = user_emb[users]
    pos_emb = item_emb[pos_items]
    neg_emb = item_emb[neg_items]

    pos_scores = (u_emb * pos_emb).sum(dim=1)
    neg_scores = (u_emb * neg_emb).sum(dim=1)
    loss = -F.logsigmoid(pos_scores - neg_scores).mean()

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
    print(f"Loss: {loss.item():.4f}")

def evaluate(model, train_df, test_df, K=10):
    model.eval()
    user_emb, item_emb = model(data.edge_index)
    scores = model.predict(user_emb, item_emb).detach().cpu().numpy()

    train_user_items = train_df.groupby("user")["item"].apply(set).to_dict()
    test_user_items = test_df.groupby("user")["item"].apply(set).to_dict()

    precs, recalls, ndcgs = [], [], []
    for u in test_user_items:
        true_items = test_user_items[u]
        score = scores[u]
        score[list(train_user_items.get(u, []))] = -np.inf
        recs = np.argsort(score)[::-1][:K]

        hits = np.isin(recs, list(true_items))
        precs.append(hits.sum() / K)
        recalls.append(hits.sum() / len(true_items))
        ndcgs.append((hits / np.log2(np.arange(2, 2 + K))).sum())

    return {
        "Precision@K": np.mean(precs),
        "Recall@K": np.mean(recalls),
        "NDCG@K": np.mean(ndcgs)
    }

metrics = evaluate(model, train_df, test_df, K=10)
print(metrics)

user_id = 0
model.eval()
user_emb, item_emb = model(data.edge_index)
scores = model.predict(user_emb, item_emb)
top_items = torch.topk(scores[user_id], k=10).indices
print("Top-10 рекомендации:", top_items.tolist())
"""

        pyperclip.copy(code)

    def help(self):
        """Выводит справку о всех доступных методах."""
        help_message = "Справка по методам:\n"
        for method, description in self.methods_info.items():
            help_message += f"- {method}: {description}\n"
        pyperclip.copy(help_message)


a = ClipboardHelper()
a.ALS_BPR()
