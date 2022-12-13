# 'rootkey.csv' è il file che contiene la chiavi d'accesso all'account AWS

# va a leggere ogni riga del file 'rootkey.csv' e salva il contenuto all'interno di content
with open('transcription/key/rootkey.csv', 'r') as f:
    content = f.readlines()

# inserisce le chiavi d'accesso AWS all'interno del dizionario keys eliminando tutti gli spazi
keys = {}
for line in content:
    pair = line.strip().split('=')
    keys.update({pair[0]: pair[1]})

AWS_ACCESS_KEY_ID = keys['AWSAccessKeyId']
AWS_SECRET_KEY = keys['AWSSecretKey']
