from graph.libraries import *
from graph.get_entities import get_entities


def extract_entities(sentences):
    """Permette di estrarre le entità da un testo tokenizzato

     Parametri
     ----------
     sentences : le frasi divise in sottostringhe da cui estrarre le entità

     Restituisce
     -------
     Coppie di entità inserite all'interno di una lista
     """

    entity_pairs = []

    for i in tqdm(sentences):
        entity_pairs.append(get_entities(i))

    return entity_pairs
