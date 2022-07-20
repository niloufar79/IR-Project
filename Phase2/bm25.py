from information_retrieval.constructor import  BSBIIndex
from typing import List,Tuple
import os
import re
from math import log
class BM25:

    def __init__(self):
        self.TermDocFrequancy=dict()
        self.DoumentLenght=dict()
        self.dicconvert = {
            'ك': 'ک',
            'دِ': 'د',
            'بِ': 'ب',
            'زِ': 'ز',
            'ذِ': 'ذ',
            'شِ': 'ش',
            'سِ': 'س',
            'ى': 'ی',
            'ي': 'ی',
            '١': '۱',
            '٢': '۲',
            '٣': '۳',
            '٤': '۴',
            '٥': '۵',
            '٦': '۶',
            '٧': '۷',
            '٨': '۸',
            '٩': '۹',
            '٠': '۰',
        }
        self.numbers = "۰۱۲۳۴۵۶۷۸۹" + "0123456789"
        self.doc_numbers = 0
        self.avglength = 0
    def read_train_files(self,dir):

        '''
            Description:
                This function reads train files

        '''

        for block_dir_relative in sorted(next(os.walk(dir))[1]):
            file_path = f"{dir}\{block_dir_relative}"
            os.chdir(file_path)
            for file in os.listdir():
                if file.endswith(".txt"):
                    self.doc_numbers += 1
                    path = os.path.join(file_path, file)
                    with open(path, encoding='utf-8') as f:
                        file_lines = f.readlines()
                        for txt in file_lines:
                            for word in txt.split():
                                word = "".join([w if w not in self.dicconvert else self.dicconvert[w] for w in word])
                                word = re.sub(r'[^\w\s]', '', word)
                                word = re.sub(r'ampnbsp', '', word)
                                word = "".join([w for w in word if w not in self.numbers])
                                word = word.strip()
                                if (word != "") and (len(word) > 1):
                                    if file not in self.DoumentLenght:
                                        self.DoumentLenght[file]=0

                                    self.DoumentLenght[file]+=1
                                    if word not in self.TermDocFrequancy:
                                        self.TermDocFrequancy[word]=[[file,1]]
                                    else:
                                        li_file=[f[0] for f in self.TermDocFrequancy[word]]
                                        if file not in li_file:
                                            self.TermDocFrequancy[word].append([file,1])
                                        else:
                                            for i in range(len(self.TermDocFrequancy[word])):
                                                if self.TermDocFrequancy[word][i][0]==file:
                                                    self.TermDocFrequancy[word][i][1]+=1


                        self.avglength += self.DoumentLenght[file]

        self.avglength/=self.doc_numbers

        return self

    def get_term_idf(self, term):

        '''
            Description:
                This function return idf value of a term

        '''
        # number of ducuments that have term 'term'
        df = 0
        if term in self.TermDocFrequancy:
            df = len(self.TermDocFrequancy[term])
        idf = log((self.doc_numbers-df+0.5) / (df + 0.5) +1 )
        return idf
        # raise NotImplementedError

    def calculate_score(self, query):

        '''
            Description:
                This function calculates score of each doc according to
                the query 'query'
        '''
        DATASET_PATH = 'F:\Dataset_IR\Dataset_IR\Train'
        OUTPUT_DIR = 'F:\Dataset_IR\Dataset_IR'
        BSBI_instance = BSBIIndex(data_dir=DATASET_PATH, output_dir=OUTPUT_DIR)
        result = BSBI_instance.retrieve(query)
        doc_scores = list()
        for doc in result:
            value = 0
            for word in query.split():
                word = "".join([w if w not in self.dicconvert else self.dicconvert[w] for w in word])
                word = re.sub(r'[^\w\s]', '', word)
                word = re.sub(r'ampnbsp', '', word)
                word = "".join([w for w in word if w not in self.numbers])
                word = word.strip()
                if (word != "") and (len(word) > 1):
                    if word in self.TermDocFrequancy:
                        if doc in [f[0] for f in self.TermDocFrequancy[word]]:
                            k1 = 1.5
                            b = 0.75
                            tf =[f[1]  for f in self.TermDocFrequancy[word] if f[0] == doc][0]
                            value += (self.get_term_idf(word) * ((tf * (k1+1))/ (tf+k1)*(1-b+b*(self.DoumentLenght[doc]/self.avglength))))

            if value!=0:
                dic_docvalue={"text": doc,"bm25_score":value}
                doc_scores.append(dic_docvalue)

        return doc_scores

    def get_similar_docs(self,query)-> List[Tuple[str,int]]:

        '''
            Description:
                This function gets a query and ranks the dataset based on BM25 score sort by score
            output: a list of dicts [{"text": "document 1", "bm25_score": 1},
                                     {"text": "document 2", "bm25_score": 0.8}]
        '''
        list_doc_scores=self.calculate_score(query)
        list_doc_scores_sorted = sorted(list_doc_scores, key=lambda d: d['bm25_score'],reverse=True)
        return list_doc_scores_sorted

def read_query():
    return input('query >> ')

if __name__ == "__main__":
    dataset_dir = "F:\Dataset_IR\Dataset_IR\Train"
    bm25 = BM25().read_train_files(dataset_dir)
    while True:
        query = read_query()
        print(bm25.get_similar_docs(query))