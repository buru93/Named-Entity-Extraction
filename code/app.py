from flask import Flask, render_template, request
import spacy
from spacy_langdetect import LanguageDetector
from spacy.language import Language

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
        print(entities)
    
    return render_template("index.html", num_of_results=len(results), results=results)

if __name__ ==  '__main__':
    app.run(debug = True)