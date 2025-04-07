from flask import Flask, jsonify, request, render_template, redirect, url_for
import sqlite3

app = Flask(__name__)

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

# Initialize with some programming languages data
languages = [
    {"id": 1, "name": "Python", "creator": "Guido van Rossum", "year": 1991, 
     "paradigm": "Object-oriented, Procedural", "description": "High-level general-purpose programming language"},
    {"id": 2, "name": "JavaScript", "creator": "Brendan Eich", "year": 1995, 
     "paradigm": "Event-driven, Functional, Imperative", "description": "Scripting language for web pages"},
    {"id": 3, "name": "Java", "creator": "James Gosling", "year": 1995, 
     "paradigm": "Object-oriented, Class-based, Concurrent", "description": "Popular enterprise language"},
    {"id": 4, "name": "C++", "creator": "Bjarne Stroustrup", "year": 1985, 
     "paradigm": "Procedural, Object-oriented, Generic", "description": "Extension of C with object-oriented features"},
    {"id": 5, "name": "C#", "creator": "Microsoft", "year": 2000, 
     "paradigm": "Object-oriented, Component-oriented", "description": "Microsoft's Java-like language"},
    {"id": 6, "name": "Ruby", "creator": "Yukihiro Matsumoto", "year": 1995, 
     "paradigm": "Object-oriented, Reflective, Dynamic", "description": "Dynamic, reflective language"},
    {"id": 7, "name": "Swift", "creator": "Apple Inc.", "year": 2014, 
     "paradigm": "Object-oriented, Protocol-oriented, Functional", "description": "Apple's language for iOS development"},
    {"id": 8, "name": "Go", "creator": "Robert Griesemer, Rob Pike, Ken Thompson", "year": 2009, 
     "paradigm": "Compiled, Concurrent, Procedural", "description": "Google's systems programming language"},
    {"id": 9, "name": "HTML", "creator": "Tim Berners-Lee", "year": 1993, 
     "paradigm": "Markup language", "description": "Standard markup language for web pages"},
]

# Helper function to find language by ID
def find_language(lang_id):
    return next((lang for lang in languages if lang['id'] == lang_id), None)

# ==================== API Routes ====================

# GET all languages
@app.route("/api/languages", methods=["GET"])
def get_languages():
    return jsonify({"languages": languages, "count": len(languages)})

# GET single language by ID
@app.route("/api/languages/<int:lang_id>", methods=["GET"])
def get_language(lang_id):
    lang = find_language(lang_id)
    if lang:
        return jsonify(lang)
    return jsonify({"error": "Language not found"}), 404

# GET language by name (case-insensitive)
@app.route("/api/languages/name/<string:lang_name>", methods=["GET"])
def get_language_by_name(lang_name):
    lang = next((lang for lang in languages if lang["name"].lower() == lang_name.lower()), None)
    if lang:
        return jsonify(lang)
    return jsonify({"error": "Language not found"}), 404

# POST to add a new language
@app.route("/api/languages", methods=["POST"])
def add_language():
    if not request.json or 'name' not in request.json:
        return jsonify({"error": "Bad request"}), 400
    
    new_lang = {
        "id": languages[-1]["id"] + 1 if languages else 1,
        "name": request.json["name"],
        "creator": request.json.get("creator", ""),
        "year": request.json.get("year", ""),
        "paradigm": request.json.get("paradigm", ""),
        "description": request.json.get("description", "")
    }
    
    languages.append(new_lang)
    return jsonify(new_lang), 201

# PUT to update a language
@app.route("/api/languages/<int:lang_id>", methods=["PUT"])
def update_language(lang_id):
    lang = find_language(lang_id)
    if not lang:
        return jsonify({"error": "Language not found"}), 404
    
    if not request.json:
        return jsonify({"error": "Bad request"}), 400
    
    lang["name"] = request.json.get("name", lang["name"])
    lang["creator"] = request.json.get("creator", lang["creator"])
    lang["year"] = request.json.get("year", lang["year"])
    lang["paradigm"] = request.json.get("paradigm", lang["paradigm"])
    lang["description"] = request.json.get("description", lang["description"])
    
    return jsonify(lang)

# DELETE a language
@app.route("/api/languages/<int:lang_id>", methods=["DELETE"])
def delete_language(lang_id):
    global languages
    lang = find_language(lang_id)
    if not lang:
        return jsonify({"error": "Language not found"}), 404
    
    languages = [lang for lang in languages if lang['id'] != lang_id]
    return jsonify({"result": True})

# ==================== User Management Routes ====================

# Home route - displays all users
@app.route('/')
def index():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    conn.close()
    return render_template('index.html', users=users)

# Add new user
@app.route('/add', methods=['POST'])
def add_user():
    name = request.form['name']
    email = request.form['email']
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (name, email) VALUES (?, ?)', (name, email))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# Edit user
@app.route('/edit/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET name = ?, email = ? WHERE id = ?', (name, email, user_id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return render_template('edit.html', user=user)
    return redirect(url_for('index'))

# Delete user
@app.route('/delete/<int:user_id>')
def delete_user(user_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)