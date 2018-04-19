from ModeloBooleano.boolean_model import BooleanModel
import unittest

class ModelTest(unittest.TestCase):
    text = ['O peã e o caval são pec de xadrez. O caval é o melhor do jog.', 'A jog envolv a torr, o peã e o rei.', 'O peã lac o boi', 'Caval de rodei!', 'Polic o jog no xadrez.']
    stopwords = ['a', 'o', 'e', 'é', 'de', 'do', 'no', 'são']

    def setUp(self):
        self.bm = BooleanModel()   
        self.tokens = self.bm.normalize(self.bm.tokenize(self.text), self.stopwords)
        self.fm = self.bm.create_index(self.tokens, self.text)

    def test_empty_query(self):
        q = ['']
        self.assertEqual(
            self.bm.query(q, self.fm, self.stopwords, self.tokens, self.text),
            (set(),set())
        )

    def test_matching_query(self):
        q = ['xadrez peã caval torr']
        self.assertEqual(
            self.bm.query(q, self.fm, self.stopwords, self.tokens, self.text),
            (set(),set(self.text))
        )

    def test_not_matching_query(self):
        q = ['uga buga duga']
        self.assertEqual(
            self.bm.query(q, self.fm, self.stopwords, self.tokens, self.text),
            (set(),set())
        )

    def test_mixed_query(self): 
        q = ['xadrez peã torr buga digdin meit']
        self.assertEqual(
            self.bm.query(q, self.fm, self.stopwords, self.tokens, self.text),
            (set(), set([
                'O peã e o caval são pec de xadrez. O caval é o melhor do jog.', 
                'A jog envolv a torr, o peã e o rei.', 
                'O peã lac o boi', 
                'Polic o jog no xadrez.'
            ]))
        )
