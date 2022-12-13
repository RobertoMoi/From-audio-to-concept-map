from graph.extract_entities import extract_entities
from graph.libraries import *
from graph.get_relation import *
from graph.text_segmentation import text_segmentation


def extract_nodes(text_summarized):
    """Permette di estrarre i nodi da un testo

       Parametri
       ----------
       text_summarized : testo da cui estrarre i nodi

       Restituisce
       -------
       una dataframe con all'interno il soggetto, l'oggetto e la relazione di una frase
    """

    # segmenta il testo da riassumere in sottostringhe
    sentences = text_segmentation(text_summarized)

    # estrazione delle entità dal testo segmentato
    entity_pairs = extract_entities(sentences)
    # estrazione delle relazioni presenti all'interno del testo segmentato
    relations = [get_relation(i) for i in tqdm(sentences)]

    # estrazione del soggetto
    source = [i[0] for i in entity_pairs]

    # estrazione dell'oggetto
    target = [i[1] for i in entity_pairs]

    # inserimento delle entità e delle relazioni all'interno di un dataframe (una struttura dati tabulare)
    kg_df = pd.DataFrame({'source': source, 'target': target, 'edge': relations})

    return kg_df
