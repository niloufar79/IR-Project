import contextlib
from .inverted_index import InvertedIndexIterator, InvertedIndexWriter, InvertedIndexMapper
import pickle as pkl
import os
from .helper import IdMap
from typing import *
from hazm import *
import re
class BSBIIndex:
    """
    Attributes
    ----------
    term_id_map IdMap: For mapping terms to termIDs
    doc_id_map(IdMap): For mapping relative paths of documents (eg path/to/docs/in/a/dir/) to docIDs
    data_dir(str): Path to data
    output_dir(str): Path to output index files
    index_name(str): Name assigned to index
    postings_encoding: Encoding used for storing the postings.
        The default (None) implies UncompressedPostings
    """

    def __init__(self, data_dir, output_dir, index_name="BSBI",
                 postings_encoding=None):
        self.term_id_map = IdMap()
        self.doc_id_map = IdMap()
        self.data_dir = data_dir
        self.output_dir = output_dir
        self.index_name = index_name
        self.postings_encoding = postings_encoding
        self.docs = []



        # Stores names of intermediate indices
        self.intermediate_indices = []

        self.dicconvert= {
        'ك' :'ک',
        'دِ': 'د',
        'بِ': 'ب',
        'زِ': 'ز',
        'ذِ': 'ذ',
        'شِ': 'ش',
        'سِ': 'س',
        'ى' :'ی',
        'ي' :'ی',
        '١' :'۱',
        '٢' :'۲',
        '٣' :'۳',
        '٤' :'۴',
        '٥' :'۵',
        '٦' :'۶',
        '٧' :'۷',
        '٨' :'۸',
        '٩' :'۹',
        '٠' :'۰',
    }

    def save(self):
        """Dumps doc_id_map and term_id_map into output directory"""

        with open(os.path.join(self.output_dir, 'terms.dict'), 'wb') as f:
            pkl.dump(self.term_id_map, f)
        with open(os.path.join(self.output_dir, 'docs.dict'), 'wb') as f:
            pkl.dump(self.doc_id_map, f)

    def load(self):
        """Loads doc_id_map and term_id_map from output directory"""

        with open(os.path.join(self.output_dir, 'terms.dict'), 'rb') as f:
            self.term_id_map = pkl.load(f)
        with open(os.path.join(self.output_dir, 'docs.dict'), 'rb') as f:
            self.doc_id_map = pkl.load(f)

    def index(self):
        """Base indexing code

        This function loops through the data directories,
        calls parse_block to parse the documents
        calls invert_write, which inverts each block and writes to a new index
        then saves the id maps and calls merge on the intermediate indices
        """
        for block_dir_relative in sorted(next(os.walk(self.data_dir))[1]):
            td_pairs = self.parse_block(block_dir_relative)
            index_id = 'index_' + block_dir_relative
            self.intermediate_indices.append(index_id)
            with InvertedIndexWriter(index_id, directory=self.output_dir,
                                     postings_encoding=
                                     self.postings_encoding) as index:
                self.invert_write(td_pairs, index)
                td_pairs = None
        self.save()
        with InvertedIndexWriter(self.index_name, directory=self.output_dir,
                                 postings_encoding=
                                 self.postings_encoding) as merged_index:
            with contextlib.ExitStack() as stack:
                indices = [stack.enter_context(
                    InvertedIndexIterator(index_id,
                                          directory=self.output_dir,
                                          postings_encoding=
                                          self.postings_encoding))
                    for index_id in self.intermediate_indices]
                self.merge(indices, merged_index)

    def parse_block(self, block_dir_relative):
        """Parses a tokenized text file into termID-docID pairs

        Parameters
        ----------
        block_dir_relative : str
            Relative Path to the directory that contains the files for the block

        Returns
        -------
        List[Tuple[Int, Int]]
            Returns all the td_pairs extracted from the block

        Should use self.term_id_map and self.doc_id_map to get termIDs and docIDs.
        These persist across calls to parse_block
        """
        ### Begin your code
        file_path = f"{self.data_dir}\{block_dir_relative}"
        os.chdir(file_path)
        numbers = "۰۱۲۳۴۵۶۷۸۹" + "0123456789"
        term_doc_id = []
        for file in os.listdir():
            if file.endswith(".txt"):
                id_d = self.doc_id_map._get_id(file)
                path = os.path.join(file_path, file)
                with open(path,encoding='utf-8') as f:
                    file_lines = f.readlines()

                    for txt in file_lines:

                        for word in txt.split():

                            word ="".join([w if w not in self.dicconvert else self.dicconvert[w] for w in word])
                            word = re.sub(r'[^\w\s]', '', word)
                            word = re.sub(r'ampnbsp', '', word)
                            word = "".join([w for w in word if w not in numbers])
                            word = word.strip()
                            if (word != "") and (len(word) > 1):
                                id_t = self.term_id_map._get_id(word)
                                term_doc_id.append((id_t, id_d))
        return term_doc_id
        ### End your code

    def invert_write(self, td_pairs, index):
        """Inverts td_pairs into postings_lists and writes them to the given index

        Parameters
        ----------
        td_pairs: List[Tuple[Int, Int]]
            List of termID-docID pairs
        index: InvertedIndexWriter
            Inverted index on disk corresponding to the block
        """
        ### Begin your code
        posting_list = set()
        td_pairs.sort()
        temp = td_pairs[0][0]
        for item in td_pairs:
            if item[0] == temp:
                posting_list.add(item[1])
            else:
                if len(posting_list) > 0:
                    index.append(temp,posting_list)
                    temp = item[0]
                    posting_list = set()
                    posting_list.add(item[1])

        index.append(temp, posting_list)
        ### End your code

    def merge(self, indices, merged_index):
        """Merges multiple inverted indices into a single index

        Parameters
        ----------
        indices: List[InvertedIndexIterator]
            A list of InvertedIndexIterator objects, each representing an
            iterable inverted index for a block
        merged_index: InvertedIndexWriter
            An instance of InvertedIndexWriter object into which each merged
            postings list is written out one at a time
        """
        ### Begin your code
        merged_dic = {}
        for intermediate_indices in indices:
            for i in range(len(intermediate_indices.terms)):
               posting_list = intermediate_indices.__next__()
               item = intermediate_indices.terms[i]
               if item in merged_dic:
                   merged_dic[item].extend(posting_list)
               else:
                   merged_dic[item] = posting_list

        for k, v in merged_dic.items():
            merged_index.append(k, v)
        ### End your code

    def retrieve(self, query: AnyStr):
        """
        use InvertedIndexMapper here!
        Retrieves the documents corresponding to the conjunctive query

        Parameters
        ----------
        query: str
            Space separated list of query tokens

        Result
        ------
        List[str]
            Sorted list of documents which contains each of the query tokens.
            Should be empty if no documents are found.

        Should NOT throw errors for terms not in corpus
        """
        self.index()
        # if len(self.term_id_map) == 0 or len(self.doc_id_map) == 0:
        #     self.load()

        ### Begin your code

        query_list = query.split()
        invertedindexmapper = InvertedIndexMapper(self.index_name, directory=self.output_dir,
                                                  postings_encoding=
                                                  self.postings_encoding)
        query_postings = []
        for word in query_list:
            word = "".join([w if w not in self.dicconvert else self.dicconvert[w] for w in word])
            termid = self.term_id_map.__getitem__(word)
            postinglist = invertedindexmapper.__getitem__(termid)
            if (len(postinglist) > 0):
                query_postings.append(postinglist)

        query_postings = sorted(query_postings,key=lambda x : len(x))
        print(query_postings)
        if len(query_postings) > 0:
            final_docs=query_postings[0]
            for li in range(1,len(query_postings)):
                final_docs = sorted_intersect(final_docs,query_postings[li])

            if len(final_docs)>0:
               final_docs_name = []
               for doc in final_docs:
                   final_docs_name.append(self.doc_id_map.__getitem__(doc))
               return final_docs_name
            else:
                return []
        else:
            return []
        ### End your code


def sorted_intersect(list1: List[Any], list2: List[Any]):
    """Intersects two (ascending) sorted lists and returns the sorted result

    Parameters
    ----------
    list1: List[Comparable]
    list2: List[Comparable]
        Sorted lists to be intersected

    Returns
    -------
    List[Comparable]
        Sorted intersection
    """
    ### Begin your code
    # final_doc = set(list1).union(set(list2))
    final_doc = set(list1).intersection(set(list2))
    return list(final_doc)
    ### End your code
