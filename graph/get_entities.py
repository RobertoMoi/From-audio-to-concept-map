from graph.libraries import nlp


def get_entities(sent):
    """Estrae le entità da una frase

           Parametri
           ----------
           sent : frase da cui estrarre le entità

           Restituisce
           -------
           due stringhe con le rispettive entità
    """
    # chunk 1
    ent1 = ""
    ent2 = ""

    prv_tok_dep = ""  # tag di dipendenza del token precedente nella frase
    prv_tok_text = ""  # token precedente nella frase

    # conterranno il testo associato al soggetto e all'oggetto
    prefix = ""
    modifier = ""

    #############################################################

    for tok in nlp(sent):
        # chunk 2
        # se il token è un segno di punteggiatura, passa al token successivo
        if tok.dep_ != "punct":
            # controlla se il token è una parola composta
            if tok.dep_ == "compound":
                prefix = tok.text
                # se anche la parola precedente era una parola composta, viene aggiunta al prefisso
                if prv_tok_dep == "compound":
                    prefix = prv_tok_text + " " + tok.text

            # controlla se il token è un modificatore
            if tok.dep_.endswith("mod") == True:
                modifier = tok.text
                # se anche la parola precedente era una parola "composta", viene aggiunta al modificatore
                if prv_tok_dep == "compound":
                    modifier = prv_tok_text + " " + tok.text

            ## chunk 3
            # controlla se il token è il soggetto, in caso affermativo viene assegnato alla variabile ent 1 e le altre
            # variabili verranno reimpostate
            if tok.dep_.find("subj") == True:
                ent1 = modifier + " " + prefix + " " + tok.text
                prefix = ""
                modifier = ""
                prv_tok_dep = ""
                prv_tok_text = ""

            ## chunk 4
            # se il token è l'oggetto verrà assegnato alla variabile ent2
            if tok.dep_.find("obj") == True:
                ent2 = modifier + " " + prefix + " " + tok.text

            ## chunk 5
            # una volta che abbiamo catturato il soggetto e l'oggetto nella frase,
            # aggiorneremo il token precedente e il suo tag di dipendenza
            prv_tok_dep = tok.dep_
            prv_tok_text = tok.text
    #############################################################

    return [ent1.strip(), ent2.strip()]