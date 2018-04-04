# -*- coding: utf-8 -*-

import string
import math
import numpy as np

class Document(object):
    def __init__(self, id, text):
        self.__id   = id
        self.__text = text

    @property
    def id(self):
        return self.__id

    @property
    def text(self):
        return self.__text

class PreProcessor(object):
    def __init__(self, delims, stopwords):
        self.__delims    = str.maketrans(delims, ' '*len(delims))
        self.__stopwords = stopwords

    @property
    def delims(self):
        return self.__delims

    @property
    def stopwords(self):
        return self.__stopwords

    def tokenize(self, text):
        return [string for string in text.translate(self.__delims).split() if string != ' ']

    def normalize(self, text):
        return [string.lower() for string in text if string.lower() not in self.__stopwords]

class BooleanModel(object):
    def __init__(self, documents, preprocessor):
        self.__documents     = documents
        self.__preprocessor  = preprocessor
        self.__tokens        = np.unique(np.hstack([preprocessor.normalize(preprocessor.tokenize(doc.text)) for doc in documents]))
        self.__inverted_file = self.__create_index()
        self.__tf_idf        = self.__calc_weights(self.__tokens)

    @property
    def documents(self):
        return [(doc.id, doc.text) for doc in self.__documents]

    @property
    def tokens(self):
        return self.__tokens

    @property
    def inverted_file(self):
        return self.__inverted_file

    @property
    def tf_idf(self):
        return self.__tf_idf

    def __create_index(self):
        return {token : np.char.count([doc.text.lower() for doc in self.__documents], token) for token in self.__tokens}

    def __calc_weights(self, tokens):
        tf_idf   = {}
        num_docs = len(self.__documents)
        for idx, doc in enumerate(self.__documents):
            weights = []
            for token in tokens:
                term_freq = self.__inverted_file[token]
                inv_freq  = len(term_freq.nonzero()[0])
                if term_freq[idx] > 0:
                    weights.append((1 + math.log(term_freq[idx], 2)) * math.log(num_docs/inv_freq))
                else:
                    weights.append(0)
            tf_idf.update({doc.id:weights})

        print(tf_idf)
        return tf_idf

    def query(self, q):
        q_tokens = self.__preprocessor.normalize(self.__preprocessor.tokenize(q))
        tf_idf_q = self.__calc_weights(q_tokens)

        docs_index = []
        for token in q_tokens:
            docs_index.append(self.__inverted_file[token].nonzero())
        unique, counts = np.unique(np.hstack(docs_index), return_counts=True)

        result = dict(zip(unique, counts))
        and_result = [self.__documents[idx].text for idx in result.keys() if result[idx] == len(q_tokens)]
        or_result  = [self.__documents[idx].text for idx in result.keys() if result[idx] > 0]

        return {'AND' : and_result, 'OR' : or_result}

if __name__ == '__main__':
    docs = [Document(1, 'O peã e o caval são pec de xadrez. O caval é o melhor do jog.'),
            Document(2, 'A jog envolv a torr, o peã e o rei.'),
            Document(3, 'O peã lac o boi'),
            Document(4, 'Caval de rodei!'),
            Document(5, 'Polic o jog no xadrez.')]

    delims    = ',.!?'
    stopwords = ['a', 'o', 'e', 'é', 'de', 'do', 'no', 'são']
    pp        = PreProcessor(delims, stopwords)

    q  = 'xadrez peã caval torr'
    bm = BooleanModel(docs, pp)
    print(bm.query(q))
