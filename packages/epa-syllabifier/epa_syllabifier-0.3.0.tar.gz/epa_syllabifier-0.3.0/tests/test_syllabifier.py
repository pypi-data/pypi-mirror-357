"""
Tests for the syllabify function using the corpus epa_syllabified.csv
"""

import unittest
import csv
import os
from epa_syllabifier import syllabify


class TestSyllabifier(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """Load the corpus once for all tests"""
        cls.corpus_data = []
        corpus_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 'corpus', 'epa_syllabified.csv'
        )
        
        with open(corpus_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                word = row['word']
                expected_syllables = row['syllabified'].split('-')
                cls.corpus_data.append((word, expected_syllables))
    
    def test_corpus_cases(self):
        """Test each case of the corpus"""
        failed_cases = []
        
        for word, expected_syllables in self.corpus_data:
            with self.subTest(word=word):
                try:
                    result = syllabify(word)
                    self.assertEqual(result, expected_syllables, 
                                   f"Para la palabra '{word}': esperado {expected_syllables}, obtenido {result}")
                except AssertionError as e:
                    failed_cases.append(f"Palabra: {word} - {str(e)}")
        
        if failed_cases:
            self.fail(f"Fallaron {len(failed_cases)} casos:\n" + "\n".join(failed_cases))
    
    def test_empty_word(self):
        """Test empty word"""
        self.assertEqual(syllabify(""), [])
    
    def test_single_vowel(self):
        """Test single vowel"""
        self.assertEqual(syllabify("a"), ["a"])
        self.assertEqual(syllabify("e"), ["e"])
        self.assertEqual(syllabify("i"), ["i"])
        self.assertEqual(syllabify("o"), ["o"])
        self.assertEqual(syllabify("u"), ["u"])


def generate_individual_tests():
    """Generate individual tests for each case of the corpus (for better debugging)"""
    corpus_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'corpus', 'epa_syllabified.csv')
    
    with open(corpus_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for i, row in enumerate(reader):
            word = row['word']
            expected_syllables = row['syllabified'].split('-')
            
            def make_test(word, expected):
                def test_method(self):
                    result = syllabify(word)
                    self.assertEqual(result, expected, 
                                   f"Para '{word}': esperado {expected}, obtenido {result}")
                return test_method
            
            test_name = f'test_corpus_{i:02d}_{word.replace("-", "_")}'
            test_method = make_test(word, expected_syllables)
            test_method.__name__ = test_name
            test_method.__doc__ = f'Test para la palabra "{word}" -> {expected_syllables}'
            setattr(TestSyllabifier, test_name, test_method)


# Generate individual tests
generate_individual_tests()


if __name__ == "__main__":
    unittest.main()
