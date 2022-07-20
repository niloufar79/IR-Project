from information_retrieval.constructor import BSBIIndex

DATASET_PATH = 'F:\Dataset_IR\Dataset_IR\Train'
OUTPUT_DIR = 'F:\Dataset_IR\Dataset_IR'


if __name__ == '__main__':
    BSBI_instance = BSBIIndex(data_dir=DATASET_PATH, output_dir=OUTPUT_DIR)
    # BSBI_instance.index()
    query = input('search >>  ')
    result = BSBI_instance.retrieve(query)
    print(result)