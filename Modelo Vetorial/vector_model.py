import string
import numpy as np


class PreProcessor(object):
    def __init__(self, delims=' ', stopwords=[]):
        self.__delims    = str.maketrans(delims, ' '*len(delims))
        self.__stopwords = stopwords

    def tokenize(self, text):
        return [string for string in text.translate(self.__delims).split() if string != ' ']

    def normalize(self, text):
        return [string.lower() for string in text if string.lower() not in self.__stopwords]


class VectorModel(object):
    def __init__(self, preprocessor, documents):
        self.__preprocessor  = preprocessor
        self.__documents     = documents
        self.__tokens        = np.unique(np.hstack([preprocessor.normalize(preprocessor.tokenize(doc)) for doc in documents]))
        self.__inverted_file = self.__create_index()
        self.__tf_idf        = self.__calc_doc_weights(self.__tokens, lambda x: 0 if x == 0 else 1+np.log2(x), lambda x: np.log2(x))
    
    def __create_index(self):
        return {token : np.char.count([doc.lower() for doc in self.__documents], token) for token in self.__tokens}

    def __calc_doc_weights(self, tokens, calc_tf, calc_idf):
        return {
            idx: [
                calc_tf(self.__inverted_file.get(token,[])[idx]) * calc_idf(len(self.__documents) / len(self.__inverted_file.get(token,[]).nonzero()[0])) 
                for token in tokens
            ]
            for idx, doc in enumerate(self.__documents)
        }

    def __calc_query_weights(self, query, q_tokens, calc_tf, calc_idf):
        return {
            idx: [
                calc_tf(token, query) * calc_idf(len(self.__documents), len(self.__inverted_file.get(token,[]).nonzero()[0])) 
                for token in self.__tokens
            ]
            for idx, doc in enumerate(self.__documents)
        }

    def query(self, q):
        q_tokens = self.__preprocessor.normalize(self.__preprocessor.tokenize(q))
        tf_idf_q = self.__calc_query_weights(q, q_tokens, lambda x, y: 0 if y.count(x) == 0 else 1+np.log2(y.count(x)), lambda x, y: 0 if y == 0 else np.log2(x/y))

        rank = [
            (
                doc_idx, 
                (
                    np.sum([self.__tf_idf[doc_idx][token_idx] * tf_idf_q[doc_idx][token_idx] for token_idx in range(len(self.__tokens))]) 
                    / (
                        np.sqrt(np.sum([self.__tf_idf[doc_idx][token_idx]**2 for token_idx in range(len(self.__tokens))])) 
                        * np.sqrt(np.sum([tf_idf_q[doc_idx][token_idx]**2 for token_idx in range(len(self.__tokens))]))
                    )
                )
            )
            for doc_idx in range(len(self.__documents))
        ]

        rank.sort(reverse=True, key=lambda x: x[1])
        return rank


def main():
    documents = [
        'O peã e o caval são pec de xadrez. O caval é o melhor do jog.',
        'A jog envolv a torr, o peã e o rei.',
        'O peã lac o boi',
        'Caval de rodei!',
        'Polic o jog no xadrez.'
    ]

    delimiters = ',.!? '
    stopwords = ['a', 'o', 'e', 'é', 'de', 'do', 'no', 'são']

    pp = PreProcessor(delims=delimiters, stopwords=stopwords)
    vm = VectorModel(preprocessor=pp, documents=documents)

    q = 'xadrez peã caval torr'
    print(vm.query(q))

if __name__ == '__main__':
    main()
