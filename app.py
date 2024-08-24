from flask import Flask, request, jsonify, render_template
from processor import spell_check  # Import your spell_check function

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/spellcheck', methods=['POST'])
def spellcheck():
    data = request.json
    text = data.get('text', '')
    errors = spell_check(text)
    print(errors)  # Debug: print errors to the console
    return jsonify(errors)

if __name__ == '__main__':
    app.run()
