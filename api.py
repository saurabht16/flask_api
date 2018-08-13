from flask import Flask
from flask import jsonify, request, g
import sqlite3
from flask import abort


app = Flask(__name__)
app.config["DEBUG"] = True

books = [
    {'id': 0,
     'title': 'A Fire Upon the Deep',
     'author': 'Vernor Vinge',
     'first_sentence': 'The coldsleep itself was dreamless.',
     'year_published': '1992'},
    {'id': 1,
     'title': 'The Ones Who Walk Away From Omelas',
     'author': 'Ursula K. Le Guin',
     'first_sentence': 'With a clamor of bells that set the swallows soaring, the Festival of Summer came to the city Omelas, bright-towered by the sea.',
     'published': '1973'},
    {'id': 2,
     'title': 'Dhalgren',
     'author': 'Samuel R. Delany',
     'first_sentence': 'to wound the autumnal city.',
     'published': '1975'}
]

@app.route('/hello')
def hello():
    return 'Hello, World!'

@app.route('/', methods= ['GET'])
def home():
    return "<h1>Distant Reading archive </h1><p> This site is a prototype API for distant reading of science fiction " \
           "movies.</p> "


@app.route('/api/v1/resources/books/all', methods=["GET"])
def api_all():
    return jsonify(books)


@app.route('/api/v1/resources/books', methods=["GET"])
def api_id():
    # Check if an ID was provided as part of the URL.
    # If ID is provided, assign it to a variable.
    # If no ID is provided, display an error in the browser.
    if 'id' in request.args:
        id = int(request.args['id'])
    else:
        return "Error!! No id field provided. Please provide an id field"

    #create a empy list for our results
    results = []
    # Loop through the data and match results that fit the requested ID.
    # IDs are unique, but other fields might return many results
    for book in books:
        if book['id'] == id:
            results.append(book)

    # Use the jsonify function from Flask to convert our list of
    # Python dictionaries to the JSON format.

    return jsonify(results)

DATABASE = 'books.db'

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

@app.route('/api/v2/resources/books/all', methods=["GET"])
def api_v2_all():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory  = dict_factory
    cur = conn.cursor()
    all_books = cur.execute("SELECT * FROM books;").fetchall()
    return jsonify(all_books)

@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404

@app.route('/api/v2/resources/books', methods=["GET"])
def api_filter():
    query_parameters = request.args

    id = query_parameters.get('id')
    published = query_parameters.get('published')
    author = query_parameters.get('author')

    query = "SELECT * from books where"
    to_filter = []

    if id:
        query += ' id =? AND'
        to_filter.append(id)
    if published:
        query += ' published =? AND'
        to_filter.append(published)
    if author:
        query += ' author =? AND'
        to_filter.append(author)
    if not(id or published or author):
        return page_not_found(404)
    print(query)
    query = query[:-4] + ';'

    conn = sqlite3.connect('books.db')
    conn.row_factory = dict_factory

    cur = conn.cursor()

    results = cur.execute(query, to_filter).fetchall()
    conn.close()
    if results:
        return jsonify(results)
    else:
        return "<h1>Not Found</h1><p>The search returned 0 results. Please search again.</p>"


@app.route('/api/v2/resources/books/create', methods=['GET','POST'])
def add_book():
    if not request.args or not 'title' in request.args:
         abort(400)
    query_parameters = request.args
    conn = sqlite3.connect('books.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()
    max_id = cur.execute("select max(id) from books").fetchone()
    print(max_id)
    id =  max_id['max(id)'] + 1
    author = query_parameters.get('author')
    first_sentence =  query_parameters.get('first_sentence')
    published = query_parameters.get('published')
    title =  query_parameters.get('title')

    cur.execute("INSERT INTO books (id, author, first_sentence, published, title) VALUES (?, ?, ?, ?, ?)", (id, author, first_sentence, published, title))
    conn.commit()
    conn.close()
    return "Success"

@app.route('/api/v2/resources/books/update', methods=['GET','PUT'])
def update_book():
    if not request.args or not 'id' in request.args:
         abort(400)
    query_parameters = request.args
    conn = sqlite3.connect('books.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()
    id = query_parameters.get('id')
    author = query_parameters.get('author')
    first_sentence =  query_parameters.get('first_sentence')
    published = query_parameters.get('published')
    title =  query_parameters.get('title')
    if published:
        cur.execute("UPDATE books SET PUBLISHED = ? where id = ?",
                    (published, id))
        conn.commit()
    if author:
        cur.execute("UPDATE books SET AUTHOR = ? where id = ?",
                    (author, id))
        conn.commit()
    if title:
        cur.execute("UPDATE books SET TITLE = ? where id = ?",
                    (title, id))
        conn.commit()
    if not (id):
        return page_not_found(404)

    conn.close()
    return "Success"

if __name__ == '__main__':
    app.run()
