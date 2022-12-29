# From-audio-to-concept-map (working in progress)

L'obiettivo di questo progetto è quello di trasformare un file audio in una mappa concettuale (per il momento l'output finale è un "knowledge graph" abbastanza impreciso)
avvalendosi di diversi strumenti che sfruttano le tecnologie NLP. Utilizza Amazon AWS per la trascrizione del file audio, modelli di OpenAI e Hugging Face per la 
sintetizzazione della trascrizione, Spacy e nltk per la suddivisione delle frasi e l'individuazione dei nodi e delle relazioni tra di essi e infine Networkx e Matplotlib
per la creazione del grafo. Il knowledge graph può essere utilizzato solo se l'audio è in inglese.

Per utilizzare il progetto:
1. Caricare il file rootkey.csv (contenente le chiavi del proprio account Amazon AWS) all'interno della directory From-audio-to-concept-map/transcription/key
2. Inserire la chiave del proprio account OpenAI all'interno del file routes.py nella riga 21
3. Avviare il server e utilizzare PostMan (o un'altra piattaforma API) per l'utilizzo della web app (i parametri di ogni view sono in formato JSON e vanno impostati 
   all'interno del body su PostMan)
4. *Passare al punto 5 se il file è stato già caricato sul bucket Amazon* Utilizzare la view upload_file per caricare un file audio all'interno del proprio bucket Amazon 
   specificando i parametri: file_name (nome del file) e bucket (nome del bucket)
5. Per iniziare la trascrizione avviare la view launch_transcribe specificando i parametri: file_name, bucket_name, job_name e language (esempio "en-US")
6. Dopo la trascrizione è possibile avviare la sintetizzazione attraverso la view summarization, i parametri sono: model (può essere "GPT-3" o "Hugging Face" altrimenti
   da un errore) e "max_tokens" (numero massimo di token che può contenere il riassunto)
7. Ora è possibile avviare main_topic che estrae l'argomento principale dal testo
8. Infine l'ultimo step è quello di avviare concept_map per ottenere in output il knowledge graph in formato png
