from nltk.tokenize import sent_tokenize
from graph.libraries import pd


def text_segmentation(text_summarized):
    """Permette di tokenizzare un testo passato come parametro

           Parametri
           ----------
           text_summarized : testo da tokenizzare

           Restituisce
           -------
           un array monodimensionale etichettato con all'interno il testo tokenizzato
        """
    separation_sentences = sent_tokenize(text_summarized, language='english')
    sentences = pd.Series(separation_sentences)

    return sentences

