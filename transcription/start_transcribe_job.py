def start_transcribe_job(transcribe, job_name, bucket, file, language):
    """Avvia un processo di trascrizione AWS

    Parametri
    ----------
    transcribe : Istanza del servizio client AWS `transcribe`
    job_name : nome del "job" AWS
    bucket : nome del bucket AWS
    file : nome del file audio da trascrivere
    language : lingua del file audio da trascrivere

    Restituisce
    -------
    True: se il "job" viene avviato con successo

    """
    # percorso dov'è allocato il file audio da trascrivere
    file_uri = f'https://s3.amazonaws.com/{bucket}/{file}'

    # avvia il processo di trascrizione e rilascia un messaggio di errore in caso di problemi
    try:
        transcribe.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={'MediaFileUri': file_uri},
            MediaFormat='mp3',
            LanguageCode=language)
        return True
    except Exception as e:
        return e

