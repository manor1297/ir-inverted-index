from linkedlist import LinkedList
from collections import OrderedDict


class Indexer:
    def __init__(self):
        self.inverted_index = OrderedDict({})
        self.token_num = 0

    def get_index(self):
        return self.inverted_index

    def generate_inverted_index(self, doc_id, tokenized_document):
        self.token_num = len(tokenized_document)
        for t in tokenized_document:
            self.add_to_index(t, doc_id)

    def add_to_index(self, term_, doc_id_):
        if term_ in self.inverted_index.keys():
            if doc_id_ in self.inverted_index[term_].traverse_list():
                self.inverted_index[term_].increment_tf(doc_id_)
            else:
                self.inverted_index[term_].insert_at_end(doc_id_, self.token_num)
        else:
            self.inverted_index[term_] = LinkedList()
            self.inverted_index[term_].insert_at_end(doc_id_, self.token_num)

    def sort_terms(self):
        sorted_index = OrderedDict({})
        for k in sorted(self.inverted_index.keys()):
            sorted_index[k] = self.inverted_index[k]
        self.inverted_index = sorted_index

    def add_skip_connections(self):
        for k in self.inverted_index.keys():
            self.inverted_index[k].add_skip_connections()

    def calculate_tf_idf(self, doc_num=0):
        for k in self.inverted_index.keys():
            self.inverted_index[k].score(doc_num)
