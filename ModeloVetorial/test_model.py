from ModeloVetorial.vector_model import PreProcessor, VectorModel
import unittest

class ModelTest(unittest.TestCase):
    documents = [
        'O peã e o caval são pec de xadrez. O caval é o melhor do jog.',
        'A jog envolv a torr, o peã e o rei.',
        'O peã lac o boi',
        'Caval de rodei!',
        'Polic o jog no xadrez.'
    ]

    delimiters = ',.!? '
    stopwords = ['a', 'o', 'e', 'é', 'de', 'do', 'no', 'são']

    def setUp(self):
        pp = PreProcessor(delims=self.delimiters, stopwords=self.stopwords)
        self.vm = VectorModel(preprocessor=pp, documents=self.documents)

    def test_empty_query(self):
        q = ''
        self.assertEqual(
            self.vm.query(q), 
            [(doc_idx, 0) for doc_idx, _ in enumerate(self.documents)]
        )
    
    def test_matching_query(self):
        q = 'xadrez peã caval torr'
        self.assertEqual(
            self.vm.query(q), 
            [(1, 0.4651729931620071), (0, 0.415053375730601), (3, 0.21298960013595078), (4, 0.20532236528436032), (2, 0.052555274134206874)]
        )

    def test_not_matching_query(self):
        q = 'isto eh um teste'
        self.assertEqual(
            self.vm.query(q), 
            [(doc_idx, 0) for doc_idx, _ in enumerate(self.documents)]
        )

    def test_mixed_query(self):
        q = 'xadrez eh um teste de caval'
        self.assertEqual(
            self.vm.query(q), 
            [(0, 0.6177502952884825), (3, 0.3498475928479082), (4, 0.33725372134002063), (1, 0.0), (2, 0.0)]
        )
