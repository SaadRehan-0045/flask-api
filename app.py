from flask import Flask, jsonify, request, render_template, redirect, url_for
import sqlite3
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

# ==================== Recipe Recommendation System ====================

# Load dataset
data = pd.read_csv("recipe_final (1).csv")

# Preprocess Ingredients using TF-IDF Vectorizer
vectorizer = TfidfVectorizer()
X_ingredients = vectorizer.fit_transform(data['ingredients_list'])

def recommend_recipes(ingredients_text, threshold=0.3):
    """
    Find ALL recipes similar to input ingredients
    threshold: minimum similarity score (0 to 1)
    """
    # Transform input
    input_transformed = vectorizer.transform([ingredients_text])
    
    # Calculate cosine similarity with ALL recipes
    similarities = cosine_similarity(input_transformed, X_ingredients)
    
    # Get indices of all recipes above similarity threshold
    matching_indices = [i for i, score in enumerate(similarities[0]) if score >= threshold]
    
    # Add similarity scores to results
    results = data.iloc[matching_indices][['recipe_name', 'ingredients_list', 'image_url']]
    results['similarity'] = similarities[0][matching_indices]
    
    # Sort by similarity (best matches first)
    return results.sort_values('similarity', ascending=False)

def search_recipes(query):
    """Search recipes by name using SQL-like pattern matching"""
    return data[data['recipe_name'].str.contains(query, case=False, na=False)][['recipe_name', 'ingredients_list', 'image_url']]

def truncate(text, length=150):
    return text[:length] + "..." if len(text) > length else text

# ==================== User Management System ====================

# Initialize database
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# ==================== Programming Languages API ====================



# ==================== Routes ====================

# Home route - Recipe Recommendation System
@app.route('/', methods=['GET', 'POST'])
def index():
    recommendations = []
    search_results = []
    
    if request.method == 'POST':
        # Check which form was submitted
        if 'ingredients' in request.form:
            # Recipe recommendation based on ingredients
            ingredients = request.form['ingredients']
            recommendations = recommend_recipes(ingredients).to_dict(orient='records')
        
        elif 'search_query' in request.form:
            # Search by recipe name
            query = request.form['search_query']
            search_results = search_recipes(query).to_dict(orient='records')
    
    return render_template(
        'index.html', 
        recommendations=recommendations,
        search_results=search_results,
        truncate=truncate
    )



if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', debug=False)  # Disable debug in production