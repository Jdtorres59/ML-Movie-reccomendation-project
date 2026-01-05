import numpy as np
import pandas as pd
import difflib
from sklearn.feature_extraction.text import TfidfVectorizer #convert letters to number (Title-># for example)
from sklearn.metrics.pairwise import cosine_similarity #Calculates similarity between movies


#DATA COLLECTION AND PRE-PROCESSING

movies_data = pd.read_csv("movies.csv")
movies_data = movies_data.set_index("index", drop=False)

print(movies_data.shape) #4803 rows, 24 columns

#Selecting relevant features
selected_features = ['keywords', 'genres', 'tagline', 'cast', 'director']

#Replacing null values with null string
for feature in selected_features:
    movies_data[feature] = movies_data[feature].fillna('')
    
#Combining all the 5 selected features
combined_features = movies_data['genres'] + ' ' + movies_data['keywords'] + ' ' + movies_data['tagline'] + ' ' + movies_data['cast'] + ' ' + movies_data['director']
#print(combined_features)

#Convert text to feature vectors
vectorizer = TfidfVectorizer()  
feature_vectors = vectorizer.fit_transform(combined_features)



#COSINE SIMILARITY

#Getting similarity score
similarity = cosine_similarity(feature_vectors)

#Getting the movie name from the user
movie_name = input(" Enter your favorite movie name: ")

#Creating a list with all the movie names given in the dataset
list_of_all_titles = movies_data['title'].tolist()

#Finding the close match for the movie name given by the user
find_close_match = difflib.get_close_matches(movie_name, list_of_all_titles, n=1, cutoff=0.6)
if not find_close_match:
    print("No close match found. Try another title.")
    exit()
close_match = find_close_match[0]

#Finding the index of the movie
index_of_the_movie = movies_data[movies_data.title == close_match]['index'].values[0]

#Getting a list of similar movies
similarity_score = list(enumerate(similarity[index_of_the_movie]))# -> List with [(index, similarity score), (index, similarity score), ...]

#Sorting the movies based on their similarity score
sorted_similar_movies = sorted(similarity_score, key = lambda x:x[1], reverse=True) #Sort by the second value in each element of the list (similarity score)

#Print the name of similar movies using index
print('Movies suggested for you: \n')

i=1
for movie in sorted_similar_movies:
    index = movie[0]
    title_from_index = movies_data.loc[index, "title"]    
    if (i<30):
        print(i, '.', title_from_index)
        i+=1

