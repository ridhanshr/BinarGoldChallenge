import re
from datetime import datetime
import sqlite3
import time
from flask import Flask, jsonify

app = Flask(__name__)

from flask import request
from flasgger import Swagger, LazyString, LazyJSONEncoder
from flasgger import swag_from
from werkzeug.utils import secure_filename

app.json_encoder = LazyJSONEncoder
swagger_template = dict(
    info = {
        'title': LazyString(lambda: 'Text Cleansing API'),
        'version': LazyString(lambda: '1.0.0'),
        'description': LazyString(lambda: 'This API for Text Cleansing'),
    },
    host = LazyString(lambda: request.host),
)
swagger_config = {
    'headers': [],
    'specs': [
        {
        'endpoint': 'docs',
        'route': '/docs.json',
        }
    ],
    'static_url_path': '/flasgger_static',
    'swagger_ui': True,
    'specs_route': '/docs/',
}
swagger = Swagger(app, template=swagger_template, 
                  config=swagger_config)

def get_db_connection():
    conn = sqlite3.connect('D:\Belajar\Binar\Gold Challange\challange1\goldchallenge.db')
    conn.row_factory = sqlite3.Row
    return conn
    
def removePunc(text):
    newText = re.sub(r'[^\w\s]', ' ', text)
    return newText

def removeEmoticon(text):
    newText = re.sub(r'[^\x00-\x7F]+',' ', text)
    return newText

def removeNewLines(text):
    newText = re.sub('\n', ' ', text)
    return newText

def removeMoreSpace(text):
    newText = re.sub('  +', '', text)
    return newText

def preProcess(text): 
    text = removePunc(text)
    text = removeEmoticon(text)
    text = removeNewLines(text)
    text = removeMoreSpace(text)
    return text

@swag_from('docs/text_processing.yml', methods=['POST'])
@app.route('/text-processing', methods=['POST'])
def text_processing():
    
    conn = get_db_connection()
    
    start_time = time.time()
    text = request.form.get('text')
    data = preProcess(text)
    end_time = time.time()

    conn.execute('INSERT INTO cleanText (inputan, bersih) VALUES (?, ?)', (text, data))
    conn.commit()
    conn.close()
        
    json_response = {
        'result': data,
        'execute time': '{} s'.format((end_time - start_time))
    }
    response_data = jsonify(json_response)
    return response_data

@swag_from('docs/fileTextProcessing.yml', methods=['POST'])
@app.route('/filetext-processing', methods=['POST'])
def filetext_processing():
   
    conn = get_db_connection() 
    
    start_time = time.time()
    reqFile = request.files['upfile']
    reqFile.save(secure_filename(reqFile.filename))
    with open(r"D:\Belajar\Binar\Gold Challange\challange1\{}".format(reqFile.filename),"r+") as f:
        data = f.read()
        f.seek(0)
        f.write(preProcess(data))
        f.truncate()
    cleanText = preProcess(data)
    end_time = time.time()
    
    conn.execute('INSERT INTO cleanFileText (inputan, bersih) VALUES (?, ?)', (data, cleanText))
    conn.commit()
    conn.close()
    
    json_response = {
        'result': preProcess(cleanText),
        'execute time': '{} s'.format((end_time - start_time))
    }
    
    response_data = jsonify(json_response)
    return response_data

if __name__ == '__main__':
    app.run()
