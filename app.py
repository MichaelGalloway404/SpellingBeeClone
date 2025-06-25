'''
        This is our python server:
        We will run our server from the command line:
            C\:> python -m http.server 8000
            C\:> python ./app.py

        visiting http://localhost:8000 will start the game. as 127.0.0.1 is the default for Flask and we started the server on port 8000
'''

from flask import Flask, request
from flask_restful import Api, Resource
from flask_cors import CORS
import pymysql
import random
import datetime
import json

app = Flask(__name__)     # Create a Flask app instance
api = Api(app)            # Wrap it with Flask-RESTful to define API resources
CORS(app)                 # Enable CORS (Cross-Origin Resource Sharing)


# Database connection
def get_db_connection():
    return pymysql.connect(
        host="localhost",
        user="root",            # your username 
        password="root",        # your password 
        database="spellingbee", 
        cursorclass=pymysql.cursors.DictCursor  # Needed for dictionary-based fetch
    )

# -------------------- HELPER functions start ----------------------------------------------------------

# Used by get_today_letters()
# Get all valid words from DB that are atleast 7 letters long
def get_valid_words_from_db():
    conn = get_db_connection() # connect to Db
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT word FROM valid_words WHERE LENGTH(word) >= 7")  # grab all words from db greater than or = to lenght 7
            # cursor.execute("SELECT word FROM valid_words WHERE word = 'crashed'")  # grab a specific word if wanted
            rows = cursor.fetchall()
            # Go through each row in the list of rows, grab the value at the 'word' key, and put all of those into a new list.
            return [row['word'] for row in rows]
    finally:
        conn.close()


# Used by get_today_letters()
# Check if a word is a pangram (uses all 7 letters)
def is_pangram(word, letters):
    return set(word) >= set(letters)

# Used by get_valid_combinations(letters, words)
# Check if word can be built with given letters
def is_word_possible(word, letters):
    available = list(letters)       # make a copy of list containg todays letters
    for ch in word:                 # We loop through each letter in the word we're trying to validate.
        if ch in available:         # if character can be used
            available.remove(ch)    # remove it so it can't be reused
        else:
            return False            # else we cant use the word
    return True

# Used by get_today_letters()
# checks chosen letters agianst valid words > len(7) to see if at least on pangram can be made
def get_valid_combinations(letters, words):
    center = letters[0]
    valid_words = []
    for word in words: # words come from get_valid_words_from_db() a list of all words len() >= 7
        if center in word:
            if is_word_possible(word, letters): # a bool on if current letter choices can make a valid word
                valid_words.append(word)
    return valid_words

# In-memory cache to store today's letters
today_letters_cache = {}

# Used by CheckWord(Resource) and Game(Resource)
# Generate today's 7-letter set that guarantees at least one pangram
def get_today_letters():
    today = datetime.date.today()
    # if a previouse session loaded todays letter just use those letters
    if today in today_letters_cache:
        return today_letters_cache[today]

    random.seed(today.isoformat())                              # make our random fixed with todays seed
    # random.seed(1)                                                # LUNATIC   
    
    vowels = 'aeiou'
    consonants = 'bcdfghjklmnpqrstvwxyz'
    word_list = get_valid_words_from_db()                       # Get all valid words from DB that are atleast 7 letters long

    while True:
        letters = [random.choice(vowels)]                       # 1 random vowel
        while len(letters) < 7:
            letter = random.choice(vowels + consonants)         # random letter from both vowels + consonants
            if letter not in letters:                           # no duplicate letters
                letters.append(letter)

        valid_words = get_valid_combinations(letters, word_list) # checks chosen letters agianst valid words > len(7) to see if at least on pangram can be made

        # Check if there's at least one pangram
        has_pangram = any(is_pangram(word, letters) for word in valid_words)

        if has_pangram:
            random.shuffle(letters)
            today_letters_cache[today] = letters
            return letters


# Used by CheckWord() and RestartGame()
# Update found words for session
def update_found_words(session_id, new_words):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE user_stats SET found_words = %s WHERE session_id = %s AND date_played = %s",
                   (json.dumps(new_words), session_id, datetime.date.today()))
    conn.commit()
    conn.close()

# Used by CheckWord(Resource) and GetFoundWords(Resource)
# Get or create session info
def get_session(session_id):
    today = datetime.date.today()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_stats WHERE session_id = %s AND date_played = %s", (session_id, today))
    user = cursor.fetchone()
    if not user:
        cursor.execute("INSERT INTO user_stats (session_id, found_words, date_played) VALUES (%s, %s, %s)",
                       (session_id, json.dumps([]), today))
        conn.commit()
        cursor.execute("SELECT * FROM user_stats WHERE session_id = %s AND date_played = %s", (session_id, today))
        user = cursor.fetchone()
    conn.close()
    return user

# Used by CheckWord(Resource)
# Check if word is valid via DataBase
def is_valid_word(word):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM valid_words WHERE word = %s", (word.lower(),))
    result = cursor.fetchone()
    conn.close()
    # Return True if result is not None; otherwise, return False
    return result is not None

# -------------------- HELPER functions end ----------------------------------------------------------


# 1.
# API   game/today

# path "/api/game/today"
class Game(Resource):
    def get(self):
        letters = get_today_letters() # get letters from DataBase when user goes to URL path ending in "/api/game/today"
        center_letter = letters[0]
        return {"letters": letters, "center": center_letter} # return data to app.js for use
    
# Flask-RESTful to register an API resource class (Game) with a specific route (/api/game/today).
api.add_resource(Game, '/api/game/today')


# 2.
# API   check_word

# path '/api/check_word'
class CheckWord(Resource):
    def post(self):
        data = request.get_json()
        word = data.get("word", "").lower()
        session_id = data.get("session_id")

        if len(word) < 4:
            return {"result": "too short"}

        letters = get_today_letters()
        center_letter = letters[0]

        if center_letter not in word:
            return {"result": "missing center"}

        for ch in word:
            if ch not in letters:
                return {"result": "invalid"}

        if not is_valid_word(word):
            return {"result": "invalid"}

        session = get_session(session_id)
        found_words = json.loads(session["found_words"])
        if word in found_words:
            return {"result": "already found"}

        found_words.append(word)
        update_found_words(session_id, found_words)

        # 1pt for words of length 4 and n points for words of lenght n > 4
        total_points = sum(1 if len(w) == 4 else len(w) for w in found_words)
        # For every word in found_words, if that word uses exactly 7 unique letters, then add 7 points to the total for each such word.
        total_points += sum(7 for w in found_words if len(set(w)) == 7)

        if total_points >= 100:
            rank = "Genius"
        elif total_points >= 75:
            rank = "Amazing"
        elif total_points >= 50:
            rank = "Great"
        elif total_points >= 10:
            rank = "Good"
        else:
            rank = "Beginner"

        response = {"result": "ok", "total_points": total_points, "rank": rank}
        if len(set(word)) == 7:
            response["pangram"] = True

        return response
api.add_resource(CheckWord, '/api/check_word')


# 3.
# API found_words

# path '/api/found_words'
class GetFoundWords(Resource):
    def get(self):
        session_id = request.args.get("session_id")
        if not session_id:
            return {"found_words": [], "total_points": 0, "rank": "Beginner"}

        session = get_session(session_id) # use custom saved session
        # This accesses the "found_words" key in Flask's session storage 
        # (which stores data for the duration of a user's session).
        found_words = json.loads(session["found_words"])

        # 1pt for words of length 4 and n points for words of lenght n > 4
        total_points = sum(1 if len(w) == 4 else len(w) for w in found_words)
        # "For every word in found_words, if that word uses exactly 7 unique letters, then add 7 points to the total for each such word."
        total_points += sum(7 for w in found_words if len(set(w)) == 7)

        if total_points >= 100:
            rank = "Genius"
        elif total_points >= 75:
            rank = "Amazing"
        elif total_points >= 50:
            rank = "Great"
        elif total_points >= 10:
            rank = "Good"
        else:
            rank = "Beginner"

        return {
            "found_words": found_words,
            "total_points": total_points,
            "rank": rank
        }

api.add_resource(GetFoundWords, '/api/found_words')


# 4.
# API restart

# path '/api/restart'
class RestartGame(Resource):
    def post(self):
        data = request.get_json()
        session_id = data.get("session_id")
        update_found_words(session_id, [])
        return {"result": "restarted"}
api.add_resource(RestartGame, '/api/restart')




# run on port 5000 as app.js will be fetching, posting, getting from URLs like 'http://localhost:5000/api/game/today' ect...
if __name__ == '__main__':
    app.run(threaded=True, debug=True, port=5000)
    # app.run(host="127.0.0.1", port=5000)
