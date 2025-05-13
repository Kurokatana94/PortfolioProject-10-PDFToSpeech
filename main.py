import io
from flask import Flask, render_template, jsonify, request
import flask
from flask_bootstrap import Bootstrap5
import pymupdf # PyMuPDF
from zyphra import ZyphraClient
import datetime as dt
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
ZYPHRA_KEY = os.environ.get('ZYPHRA_KEY')
Bootstrap5(app)

# ======== PDF TEXT EXTRACTION ========
def extract_pdf_text(file):
    doc = pymupdf.open(stream=file.read(), filetype='pdf')
    pdf_text = ''
    for page in doc:
        pdf_text += page.get_text()
    print(pdf_text)
    return pdf_text[:50] #add limit [:n] if there is one with the api ---> ADDED LIMIT FOR TESTING PURPOSES SO THAT I WON'T FINISH MY CREDITS IN FEW DAYS - MIGHT EVEN LEAVE IT AS SUCH FOR THE LIVE DEMO

@app.route('/')
def home():
    return render_template('index.html', year=dt.datetime.now().year)

# ======== AUDIO CONVERSION THRU API ========
@app.route('/upload-pdf', methods=['POST'])
def upload_pdf():
    pdf_file = request.files.get('pdf')

    if pdf_file:
        text = extract_pdf_text(pdf_file)
        with ZyphraClient(api_key=ZYPHRA_KEY) as client:
            mp3_data = client.audio.speech.create(
                text=text,
                speaking_rate=15,
                myme_type='audio/mp3',
            )

        mp3_io = io.BytesIO(mp3_data)
        mp3_io.seek(0)

        filename = f"audio_{dt.datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"

        return flask.send_file(mp3_io,
                         mimetype='audio/mpeg',
                         as_attachment=False,
                         download_name=filename)

if __name__ == '__main__':
    app.run(debug=True)