from urllib.request import Request
from flask import Flask, render_template, request
import spacy
from spacy_langdetect import LanguageDetector
from spacy.language import Language
from classifier import SentimentClassifier
from nltk.sentiment.vader import SentimentIntensityAnalyzer
# only use the first time.
# import nltk
# nltk.download('vader_lexicon') ## Line needed to correct error https://github.com/nltk/nltk/issues/1296

app = Flask(__name__)

def get_lang_detector(nlp, name):
    return LanguageDetector()

def checkEntity(data):
    # Cargo el modelo
    nlp = spacy.load("es_core_news_md")

    # Se pasa la funcion que nos permitira saber que idioma detecta
    Language.factory("language_detector", func=get_lang_detector)
    nlp.add_pipe('language_detector', last=True)

    # Procesamos el texto
    doc = nlp(data)

    # Dependiendo del idioma que haya detectado, si es Ingles carga la correspondiente libreria
    # Vuelve a procesar el texto para que asi lo haga con el modelo en Ingles
    if doc._.language['language'] == 'en':
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(data)

    # # Obtenemos todas las entidades
    all_entitys = [(ent.label_, ent.text) for ent in doc.ents]

    return all_entitys, doc._.language['language']

def getSentiment(language, data):
    if language == 'en':
        ia = SentimentIntensityAnalyzer()
        sentiment = ia.polarity_scores(data)['compound']
        cla = ""
        if sentiment >= 0.05:
            cla = "alert-success"
        elif sentiment <= -0.05:
            cla = "alert-danger"
        else:
            cla = "alert-warning"
    else:
        cla = ""
        if sentiment >= 0.6:
            cla = "alert-success"
        elif sentiment <= 0.4:
            cla = "alert-danger"
        else:
            cla = "alert-warning"
        ia = SentimentClassifier()
        sentiment = ia.predict(data)

    print(sentiment, cla)
    return sentiment, cla

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/processTxt", methods = ['POST'])
def procces_text():
    if request.method == 'POST':
        data_dropdown = request.form['taskoption']
        entities, language = checkEntity(request.form['rawtext'])
        
        if data_dropdown == "organization":
            entity_kind = "ORG"
        elif data_dropdown == "person":
            if language == 'en':
                entity_kind = "PERSON"
            else:
                entity_kind = "PER"
        elif data_dropdown == "location":
            entity_kind = "LOC"
        elif data_dropdown == "gpe":
            entity_kind = "GPE"
        elif data_dropdown == "product":
            entity_kind = "PRODUCT"
        elif data_dropdown == "money":
            entity_kind = "MONEY"
        elif data_dropdown == "date":
            entity_kind = "DATE"
        else:
            entity_kind = ""

        results = [dato for dato in entities if dato[0] == entity_kind]
    
        compound, cla = getSentiment(language, request.form['rawtext'])

    return render_template("index.html", num_of_results=len(results), results=results, sentiment=compound, cla=cla)

if __name__ ==  '__main__':
    app.run(debug = True)