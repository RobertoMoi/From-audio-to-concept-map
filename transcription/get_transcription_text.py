def get_transcription_text(transcribe, job_name):
    """Restituisce la trascrizione di un file audio

    Parametri
    ----------
    transcribe : Istanza del servizio client AWS `transcribe`
    job_name : nome del "job" AWS

    Restituisce
    -------
    Lo stato del "job" nel caso la trascrizione sia ancora in corso
    Trascrizione del testo se il lavoro è completato
    """
    import urllib.request
    import json
    import time

    # recupera l'istanza del "job"
    job = transcribe.get_transcription_job(TranscriptionJobName=job_name)

    # stato del "job"
    status = job['TranscriptionJob']['TranscriptionJobStatus']

    # controlla lo stato del "job" ogni 5 secondi
    # restituisce la trascrizione del testo se il "job" viene completato correttamente
    # altrimenti non restituisce nulla se il "job" fallisce
    max_tries = 60
    while max_tries > 0:
        max_tries -= 1
        status = job['TranscriptionJob']['TranscriptionJobStatus']
        job = transcribe.get_transcription_job(TranscriptionJobName=job_name)
        if status == 'COMPLETED':
            print(f"Job {job_name} completed")
            with urllib.request.urlopen(job['TranscriptionJob']['Transcript']['TranscriptFileUri']) as r:
                data = json.loads(r.read())
            return data['results']['transcripts'][0]['transcript']
        elif status == 'FAILED':
            print(f"Job {job_name} failed")
            return None
        else:
            print(f"Status of job {job_name}: {status}")
            time.sleep(5)

