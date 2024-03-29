from tqdm import tqdm

import linkedlist
from preprocessor import Preprocessor
from indexer import Indexer
from collections import OrderedDict
from linkedlist import LinkedList
import inspect as inspector
import sys
import argparse
import json
import time
import random
import flask
from flask import Flask
from flask import request
import hashlib

app = Flask(__name__)


class ProjectRunner:
    def __init__(self):
        self.preprocessor = Preprocessor()
        self.indexer = Indexer()
        self.doc_num = 0

    def _merge(self, post1, post2, skip=False):
        output_post = linkedlist.LinkedList()
        no_of_comparisons = 0
        i, j = post1.start_node, post2.start_node
        while i is not None and j is not None:
            if i.value == j.value:
                output_post.insert_at_end(i.value, None, max(i.tfidf, j.tfidf))
                i = i.next
                j = j.next
            elif i.value < j.value:
                if skip:
                    if i.skip is not None and i.skip.value <= j.value:
                        i = i.skip
                    else:
                        i = i.next
                else:
                    i = i.next
            else:
                if skip:
                    if j.skip is not None and j.skip.value <= i.value:
                        j = j.skip
                    else:
                        j = j.next
                else:
                    j = j.next
            no_of_comparisons += 1
        return output_post, no_of_comparisons

    def _daat_and(self, input_arr):
        input_arr = self.sort_queries(input_arr)
        input = input_arr.copy()
        no_of_comparisons = 0
        no_of_comparisons_skip = 0
        output_post, comp = linkedlist.LinkedList(), 0
        output_post_skip, comp_skip = linkedlist.LinkedList(), 0
        post1 = self.indexer.inverted_index[input[0]]
        post2 = self.indexer.inverted_index[input[1]]
        if len(input) > 1:
            output_post, comp = self._merge(post1, post2, False)
            no_of_comparisons += comp
            input.pop(0)
            input.pop(0)
            while input:
                output_post, comp = self._merge(output_post, self.indexer.inverted_index[input[0]], False)
                no_of_comparisons += comp
                input.pop(0)
            input = input_arr.copy()
            output_post_skip, comp_skip = self._merge(post1, post2, True)
            output_post_skip.add_skip_connections()
            no_of_comparisons_skip += comp_skip
            input.pop(0)
            input.pop(0)
            while input:
                output_post_skip, comp_skip = self._merge(output_post_skip, self.indexer.inverted_index[input[0]], True)
                output_post_skip.add_skip_connections()
                no_of_comparisons_skip += comp_skip
                input.pop(0)
            output_post_sorted = self.sort_tfidf(output_post)
            output_post_skip_sorted = self.sort_tfidf(output_post_skip)
        return output_post.traverse_list(), output_post_skip.traverse_list(), no_of_comparisons, no_of_comparisons_skip, output_post_sorted, output_post_skip_sorted

    def sort_tfidf(self, postings):
        post = postings.traverse_list_tfidf()
        if post:
            post = sorted(post, key=lambda x: x[1], reverse=True)
            post = [x[0] for x in post]
        return post

    def sort_queries(self, input):
        med = []
        for x in input:
            med.append([x, self.indexer.inverted_index[x].length])
        med = sorted(med, key=lambda x: x[1])
        med = [x[0] for x in med]
        return med

    def _get_postings(self, term_):
        postings = []
        skip_postings = []
        if term_ in self.indexer.inverted_index.keys():
            postings = self.indexer.inverted_index[term_].traverse_list()
            skip_postings = self.indexer.inverted_index[term_].traverse_skips()
        return postings, skip_postings

    def _output_formatter(self, op):
        if op is None or len(op) == 0:
            return [], 0
        op_no_score = [int(i) for i in op]
        results_cnt = len(op_no_score)
        return op_no_score, results_cnt

    def run_indexer(self, corpus):
        with open(corpus, 'r') as fp:
            for line in tqdm(fp.readlines()):
                doc_id, document = self.preprocessor.get_doc_id(line)
                tokenized_document = self.preprocessor.tokenizer(document)
                self.indexer.generate_inverted_index(doc_id, tokenized_document)
                self.doc_num += 1
        self.indexer.sort_terms()
        self.indexer.add_skip_connections()
        self.indexer.calculate_tf_idf(self.doc_num)

    def sanity_checker(self, command):

        index = self.indexer.get_index()
        kw = random.choice(list(index.keys()))
        return {"index_type": str(type(index)),
                "indexer_type": str(type(self.indexer)),
                "post_mem": str(index[kw]),
                "post_type": str(type(index[kw])),
                "node_mem": str(index[kw].start_node),
                "node_type": str(type(index[kw].start_node)),
                "node_value": str(index[kw].start_node.value),
                "command_result": eval(command) if "." in command else ""}

    def run_queries(self, query_list, random_command):
        output_dict = {'postingsList': {},
                       'postingsListSkip': {},
                       'daatAnd': {},
                       'daatAndSkip': {},
                       'daatAndTfIdf': {},
                       'daatAndSkipTfIdf': {},
                       'sanity': self.sanity_checker(random_command)}

        for query in tqdm(query_list):

            input_term_arr = [] 
            input_term_arr = self.preprocessor.tokenizer(query)

            for term in input_term_arr:
                postings, skip_postings = self._get_postings(term)

                output_dict['postingsList'][term] = postings
                output_dict['postingsListSkip'][term] = skip_postings

            and_op_no_skip, and_op_skip, and_op_no_skip_sorted, and_op_skip_sorted = None, None, None, None
            and_comparisons_no_skip, and_comparisons_skip, \
            and_comparisons_no_skip_sorted, and_comparisons_skip_sorted = None, None, None, None

            and_op_no_skip, and_op_skip, and_comparisons_no_skip, and_comparisons_skip, and_op_no_skip_sorted, and_op_skip_sorted = self._daat_and(input_term_arr)
            and_comparisons_no_skip_sorted, and_comparisons_skip_sorted = and_comparisons_no_skip, and_comparisons_skip
            and_op_no_score_no_skip, and_results_cnt_no_skip = self._output_formatter(and_op_no_skip)
            and_op_no_score_skip, and_results_cnt_skip = self._output_formatter(and_op_skip)
            and_op_no_score_no_skip_sorted, and_results_cnt_no_skip_sorted = self._output_formatter(
                and_op_no_skip_sorted)
            and_op_no_score_skip_sorted, and_results_cnt_skip_sorted = self._output_formatter(and_op_skip_sorted)

            output_dict['daatAnd'][query.strip()] = {}
            output_dict['daatAnd'][query.strip()]['results'] = and_op_no_score_no_skip
            output_dict['daatAnd'][query.strip()]['num_docs'] = and_results_cnt_no_skip
            output_dict['daatAnd'][query.strip()]['num_comparisons'] = and_comparisons_no_skip

            output_dict['daatAndSkip'][query.strip()] = {}
            output_dict['daatAndSkip'][query.strip()]['results'] = and_op_no_score_skip
            output_dict['daatAndSkip'][query.strip()]['num_docs'] = and_results_cnt_skip
            output_dict['daatAndSkip'][query.strip()]['num_comparisons'] = and_comparisons_skip

            output_dict['daatAndTfIdf'][query.strip()] = {}
            output_dict['daatAndTfIdf'][query.strip()]['results'] = and_op_no_score_no_skip_sorted
            output_dict['daatAndTfIdf'][query.strip()]['num_docs'] = and_results_cnt_no_skip_sorted
            output_dict['daatAndTfIdf'][query.strip()]['num_comparisons'] = and_comparisons_no_skip_sorted

            output_dict['daatAndSkipTfIdf'][query.strip()] = {}
            output_dict['daatAndSkipTfIdf'][query.strip()]['results'] = and_op_no_score_skip_sorted
            output_dict['daatAndSkipTfIdf'][query.strip()]['num_docs'] = and_results_cnt_skip_sorted
            output_dict['daatAndSkipTfIdf'][query.strip()]['num_comparisons'] = and_comparisons_skip_sorted

        return output_dict


@app.route("/execute_query", methods=['POST'])
def execute_query():
    start_time = time.time()

    queries = request.json["queries"]
    random_command = request.json["random_command"]

    output_dict = runner.run_queries(queries, random_command)

    with open(output_location, 'w') as fp:
        json.dump(output_dict, fp)

    response = {
        "Response": output_dict,
        "time_taken": str(time.time() - start_time),
        "username_hash": username_hash
    }
    return flask.jsonify(response)


if __name__ == "__main__":

    output_location = "project2_output.json"
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--corpus", type=str, help="Corpus File name, with path.")
    parser.add_argument("--output_location", type=str, help="Output file name.", default=output_location)
    parser.add_argument("--username", type=str,
                        help="Your UB username. It's the part of your UB email id before the @buffalo.edu. "
                             "DO NOT pass incorrect value here")

    argv = parser.parse_args()

    corpus = argv.corpus
    output_location = argv.output_location
    username_hash = hashlib.md5(argv.username.encode()).hexdigest()

    runner = ProjectRunner()

    runner.run_indexer(corpus)

    app.run(host="0.0.0.0", port=9999)
