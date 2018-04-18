import string
import numpy as np

class PreProcessor(object):
    def __init__(self, delimiters=' ', stopwords=[]):
        self.__delims    = str.maketrans(delimiters, ' '*len(delimiters))
        self.__stopwords = stopwords

    def tokenize(self, text):
        return [string for string in text.translate(self.__delims).split() if string != ' ']

    def normalize(self, text):
        return [string.lower() for string in text if string.lower() not in self.__stopwords]

class ProbabilisticModel(object):
    def __init__(self, preprocessor, documents):
        self.__preprocessor = preprocessor
        self.__documents = [doc.lower() for doc in documents]
        self.__tokens = np.unique(np.hstack([preprocessor.normalize(preprocessor.tokenize(doc)) for doc in documents]))
        self.__inverted_file = self.__create_index()

    def __create_index(self):
        return {token: np.char.count(self.__documents, token) for token in self.__tokens}

    def bim(self, query, total_reps=1):
        q_tokens = self.__preprocessor.normalize(self.__preprocessor.tokenize(query))

        def estimate(rep, docs, terms):
            N = len(self.__documents)
            D = len(docs)

            if rep == total_reps:
                p = {token: 0.5 for token in terms}
                q = {token: (len(self.__inverted_file[token].nonzero()[0])+0.5)/(N+1) for token in terms}
            else:
                Di = lambda token: len(np.array([doc.count(token) for doc in docs]).nonzero()[0])
                ni = lambda token: len(self.__inverted_file[token].nonzero()[0])

                p = {token: (Di(token)+(ni(token)/N))/(D+1) for token in terms}
                q = {token: (ni(token)-Di(token)+(ni(token)/N))/(N-D+1) for token in terms}

            rank = [
                (doc, np.sum([np.log2(p[token]/(1-p[token])) + np.log2((1-q[token])/q[token]) for token in terms if token in doc])) 
                for doc in docs
            ]

            rank.sort(reverse=True, key=lambda x: x[1])
            return estimate(rep-1, [doc for doc, ranking in rank if ranking > 0], terms) if rep-1 > 0 else rank

        return estimate(total_reps, self.__documents, [token for token in self.__tokens if token in q_tokens])

    def bm25(self, query, K=1, b=0.75):
        q_tokens = self.__preprocessor.normalize(self.__preprocessor.tokenize(query))
        
        num_docs = len(self.__documents)
        terms = [token for token in self.__tokens if token in q_tokens]
        num_docs_term = {token: len(self.__inverted_file.get(token,[0*num_docs]).nonzero()[0]) for token in terms}

        avg_doclen = np.mean([len(doc) for doc in self.__documents])
        calc_B = lambda freq, doc: ((K+1)*freq)/(K*((1-b+b*(len(doc)/avg_doclen)))+freq)

        B = [
            {token : calc_B(self.__inverted_file.get(token,[0*num_docs])[doc_idx], doc) for token in terms} 
            for doc_idx, doc in enumerate(self.__documents)
        ]

        rank = [
            (
                doc,
                np.sum([
                    B[doc_idx][token] * np.log2((num_docs-num_docs_term[token]+0.5)/(num_docs_term[token]+0.5))
                    for token in terms
                ])
            )
            for doc_idx, doc in enumerate(self.__documents)
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
    pp = PreProcessor(delimiters=delimiters, stopwords=stopwords)

    q = 'xadrez peã caval torr'
    pm = ProbabilisticModel(preprocessor=pp, documents=documents)
    print("BIM:", pm.bim(q))
    print("BM25:", pm.bm25(q))

if __name__ == '__main__':
    main()
