import re
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
    
    text = request.form.get('text')
    
    json_response = {
        'status_code': 200,
        'description': 'Teks yang diproses',
        'data': preProcess(text)
    }
    
    response_data = jsonify(json_response)
    return response_data

@swag_from('docs/fileTextProcessing.yml', methods=['POST'])
@app.route('/filetext-processing', methods=['POST'])
def filetext_processing():
    
    reqFile = request.files['upfile']
    reqFile.save(secure_filename(reqFile.filename))
    with open(r"D:\Belajar\Binar\Gold Challange\challange1\{}".format(reqFile.filename),"r+") as f:
        data = f.read()
        f.seek(0)
        f.write(preProcess(data))
        f.truncate()
    
    json_response = {
        'status_code': 200,
        'description': 'Teks yang diproses',
        'data': preProcess(data)
    }
    
    response_data = jsonify(json_response)
    return response_data

if __name__ == '__main__':
    app.run()
