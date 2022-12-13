from graph.libraries import nlp, Matcher


def get_relation(sent):
    """Estrae i predicati da una frase

           Parametri
           ----------
           sent : frase da cui estrarre il predicato

           Restituisce
           -------
           il predicato estratto dalla frase
    """
    doc = nlp(sent)

    # il matcher permette di trovare i componenti di una frase specificando un pattern da seguire
    matcher = Matcher(nlp.vocab)

    # definizione del pattern
    pattern = [{'DEP': 'ROOT'},
            {'DEP': 'prep', 'OP': "?"},
            {'DEP': 'agent', 'OP': "?"},
            {'POS': 'ADJ', 'OP': "?"}]

    # aggiunge le regole da seguire al matcher
    matcher.add("matching_1", [pattern])


    matches = matcher(doc)
    k = len(matches) - 1

    span = doc[matches[k][1]:matches[k][2]]

    return (span.text)