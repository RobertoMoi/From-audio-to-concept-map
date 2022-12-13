from flask import Flask, session, request, send_file

from transcription import read_key
from transcription.start_transcribe_job import start_transcribe_job
from transcription.get_transcription_text import get_transcription_text

from transformers import pipeline

from graph.libraries import nx, plt
from graph.extract_nodes import extract_nodes


import boto3

import openai
import os


app = Flask(__name__)

openai.api_key = ("")


@app.route('/')
def main():
    # libera il contenuto delle variabili sottostanti poiché se all'interno di esse non viene impostato alcun valore
    # nella sessione corrente rimane salvato il contenuto di quella precedente
    session.pop('audio_transcription', None)
    session.pop('language', None)

    return f"Benvenuto"


@app.route('/upload_file', methods=['POST'])
def upload_file():
    # analizza i dati della richiesta json e li salva all'interno di data
    data = request.get_json()

    file_name = data['filename']
    bucket = data['bucket']

    # fornisce i metodi per connettersi all'account AWS utilizzando la key dell'utente
    s3 = boto3.client('s3',
                      aws_access_key_id=read_key.AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=read_key.AWS_SECRET_KEY,
                      region_name="eu-central-1")

    # carica un file all'interno del proprio bucket
    s3.upload_file(file_name, bucket, file_name)

    return "File caricato correttamente."


@app.route('/delete_file', methods=['POST'])
def delete_file():
    data = request.get_json()

    file_name = data['file_name']
    bucket = data['bucket']

    s3 = boto3.client('s3',
                      aws_access_key_id=read_key.AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=read_key.AWS_SECRET_KEY,
                      region_name="eu-central-1")

    # elimina un file/oggetto all'interno del proprio bucket
    s3.delete_object(Bucket=bucket, Key=file_name)

    return "File eliminato correttamente."


@app.route('/launch_transcribe', methods=['POST'])
def launch_transcribe():
    data = request.get_json()

    file_name = data['file_name']
    bucket_name = data['bucket_name']
    job_name = data['job_name']
    language = data['language']

    # viene salvato il contenuto della variabile language all'interno di una variabile di sessione per poterla
    # riutilizzare nella view dedicata al riepilogo (summarization)
    session['language'] = language

    # fornisce una connessione al proprio account AWS in modalità trascrizione
    transcribe = boto3.client(
        'transcribe',
        aws_access_key_id=read_key.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=read_key.AWS_SECRET_KEY,
        region_name='eu-central-1')

    # inizia la trascrizione
    job_status = start_transcribe_job(transcribe, job_name, bucket_name, file_name, language)

    if job_status:  # se la trascrizione è andata a buon fine
        # il contenuto della trascrizione viene salvato all'interno di text
        text = get_transcription_text(transcribe, job_name)
        # la trascrizione viene salvata in una variabile di sessione per poterla utilizzare all'interno della view
        # summarization
        session['audio_transcription'] = text

        return f'<b>Trascrizione del file {file_name}:</b> <br>{text}'

    else:  # se la trascrizione non è andata buon fine restituisce un messaggio d'errore
        return f'La trascrizione {job_name} è fallita con errore: {job_status}'


@app.route("/summarization", methods=['POST'])
def summarization():
    data = request.get_json()

    model = data['model']
    max_tokens = data['max_tokens']

    # recupera i contenuti delle variabili di sessione e li memorizza all'interno di altre variabili
    transcription_result = session.get('audio_transcription', None)
    transcription_language = session.get('language', None)

    # controlla se è stata salvata correttamente la trascrizione
    if transcription_result:
        # per utilizzare i modelli della GPT-3 o di Hugging Face occorre che lingua sia inglese britannico o americano
        if transcription_language == 'en-US' or transcription_language == 'en-GB':
            if model == 'GPT-3':
                # viene utilizzata l'API openAI per la generazione del testo riassuntivo
                response = openai.Completion.create(
                  model="text-davinci-002",  # il modello utilizzato
                  prompt=f'Summarize this for a second-grade student:{transcription_result}',  # la richiesta effettuata
                  temperature=0.7,  # regola la casualità
                  max_tokens=max_tokens,  # lunghezza massima del testo generato
                  top_p=1,  # controlla la diversità tramite il campionamento del nucleo
                  frequency_penalty=0,  # grado di penalizzazione di nuovi tokens in base alla loro frequenza nel testo
                  presence_penalty=0    # grado di penalizzazione di nuovi tokens in base alla loro presenza nel testo
                )
                #  salva all'interno di una variabile di sessione il testo appena generato dall'API openAI
                session['text_summarized'] = response.choices[0].text
                return response.choices[0].text

            elif model == 'Hugging Face':
                # viene impostata la pipeline per la sommarizzazione
                summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

                # si procede con il riassunto della trascrizione
                result = summarizer(transcription_result, max_length=max_tokens, min_length=30, do_sample=False)

                # il riassunto è una lista di stringhe attraverso il join viene trasformato in una stringa unica
                space = " "
                text_summarized = space.join(result[0].values())

                return text_summarized
            else:
                # se non è stato scelto correttamente il modello tra quelli disponibile viene rilasciato un errore
                return "Errore nella scelta del modello"

        # se l'utente sceglie la lingua italiana verrà utilizzato il modello it5 per la summarization
        elif transcription_language == 'it-IT':
            new_summarization = pipeline("summarization", model='it5/it5-large-news-summarization')
            result = new_summarization(transcription_result)

            space = " "

            text_summarized = space.join(result[0].values())

            return text_summarized
    else:
        return 'Non è presente alcun testo da riassumere'


@app.route("/main-topic", methods=['POST'])
def main_topic():
    # imposta il numero massimo di caratteri per descrivere l'argomento principale
    MAIN_TOPIC_TOKENS = 100

    # ottiene la variabile di sessione che contiene il testo riassunto e viene salvato in una variabile
    text = session.get('text_summarized', None)

    response = openai.Completion.create(
        model="text-davinci-002",
        prompt=f"What is the topic of this text \"{text}\"?",
        temperature=0,
        max_tokens=MAIN_TOPIC_TOKENS,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    # viene eliminata la frase sottostante (e il punto finale) dall'argomento principale per rendere il titolo
    # più elegante all'interno del grafico
    substring = "The topic of this text is"
    point = "."

    topic = response.choices[0].text

    # se la substring è contenuta all'interno del topic allora viene eliminata così come il punto
    if substring in response.choices[0].text:
        topic = topic.replace(substring, "")
        topic = topic.replace(point, "")

    # elimina lo spazio eccessivo che si crea all'inizio della stringa
    topic = topic.lstrip()
    # imposta la prima lettera maiuscola
    topic = topic.capitalize()

    # salva l'argomento principale all'interno di una variabile di sessione per riutilizzarla all'interno del grafico
    session['topic'] = topic

    return response.choices[0].text


@app.route("/concept-map", methods=['POST'])
def concept_map():
    # recuperiamo le variabili di sessione che contengono il testo riassunto e l'argomento principale
    text = session.get('text_summarized', None)
    topic = session.get('topic', None)

    # vengono estratti i nodi dal testo riassunto
    kg_df = extract_nodes(text)

    # restituisce un grafo utilizzando i nodi estratti in precedenza
    G = nx.from_pandas_edgelist(kg_df, "source", "target", edge_attr=True,
                                create_using=nx.MultiDiGraph())
    # crea la forma del grafico, specificando le sue dimensioni
    plt.figure(figsize=(12, 12))

    # specifica la distanza tra i nodi e la loro posizione all'interno del grafo
    pos = nx.spring_layout(G, 10)
    # la funzione gca() viene utilizzata per ottenere l'istanza degli assi sulla figura corrente
    ax = plt.gca()
    # setta il titolo per il grafico
    ax.set_title(topic)
    # disegna il grafico
    nx.draw(G, with_labels=True, node_color='skyblue', edge_cmap=plt.cm.Blues, pos=pos, ax=ax)
    # disegna le etichette del grafico
    nx.draw_networkx_edge_labels(G, pos=pos)

    # salva la figura creata all'interno di un file png
    plt.savefig("image.png")
    # visualizza il grafico creato
    plt.show()

    # Restituisce l'immagine del grafico al client
    return send_file('image.png', mimetype='image/gif')



@app.route("/all-in-one", methods=['POST'])
def all_in_one():
    """attraverso questa view possiamo eseguire tutte le funzioni del servizio in un'unica volta, ovvero:
        - trascrizione
        - riassunto
        - ricerca argomento principale
        - creazione e visualizzazione del grafico
    """
    MAIN_TOPIC_TOKENS = 100

    data = request.get_json()

    file_name = data['file_name']
    bucket_name = data['bucket_name']
    job_name = data['job_name']
    language = data['language']
    max_tokens = data['max_tokens']
    model = data['model']

    # Instantiate a client to the AWS transcribe service
    transcribe = boto3.client(
        'transcribe',
        aws_access_key_id=read_key.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=read_key.AWS_SECRET_KEY,
        region_name='eu-central-1')

    # launch the job
    job_status = start_transcribe_job(transcribe, job_name, bucket_name, file_name, language)

    # if job launched successfully `job_status` will be True
    if job_status:  # and we can start requesting the results from the service
        transcription = get_transcription_text(transcribe, job_name)
        if transcription:
            if language == 'en-US' or language == 'en-GB':
                if model == 'GPT-3':
                    response = openai.Completion.create(
                        model="text-davinci-002",
                        prompt=f'Summarize this for a second-grade student:{transcription}',
                        temperature=0.7,
                        max_tokens=max_tokens,
                        top_p=1,
                        frequency_penalty=0,
                        presence_penalty=0
                    )
                    session['text_summarized'] = response.choices[0].text

                elif model == 'Hugging Face':
                    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

                    result = summarizer(transcription, max_length=max_tokens, min_length=30, do_sample=False)

                    space = " "
                    session['text_summarized'] = space.join(result[0].values())

                else:
                    return "Errore nella scelta del modello"

            elif language == "it-IT":
                new_summarization = pipeline("summarization", model='it5/it5-large-news-summarization')
                result = new_summarization(transcription)

                space = " "

                text_summarized = space.join(result[0].values())

                return text_summarized

            else:
                return "Errore nella scelta del modello"

        else:
            return 'Non è presente alcun testo da riassumere'

        text_summarized = session.get('text_summarized', None)

        response = openai.Completion.create(
            model="text-davinci-002",
            prompt=f"What is the topic of this text \"{text_summarized}\"?",
            temperature=0,
            max_tokens=MAIN_TOPIC_TOKENS,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

        substring = "The topic of this text is"
        point = "."

        topic = response.choices[0].text

        if substring in response.choices[0].text:
            topic = topic.replace(substring, "")
            topic = topic.replace(point, "")

        topic = topic.lstrip()
        topic = topic.capitalize()

        kg_df = extract_nodes(text_summarized)

        G = nx.from_pandas_edgelist(kg_df, "source", "target", edge_attr=True,
                                    create_using=nx.MultiDiGraph())
        plt.figure(figsize=(12, 12))

        pos = nx.spring_layout(G, 10)

        ax = plt.gca()
        ax.set_title(topic)

        nx.draw(G, with_labels=True, node_color='skyblue', edge_cmap=plt.cm.Blues, pos=pos, ax=ax)
        nx.draw_networkx_edge_labels(G, pos=pos)

        plt.savefig("image.png")
        plt.show()

        return send_file('image.png', mimetype='image/gif')

    else:  # in caso di problemi stampa un messaggio con il tipo di errore che si è verificato
        return f'La trascrizione {job_name} è fallita con errore: {job_status}'


@app.route("/clear_session")
def clear_session():
    session.clear()

    return "Sessione ripulita correttamente"
