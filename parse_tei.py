from bs4 import BeautifulSoup
import os
from nltk.tokenize import sent_tokenize
import config


def get_grafs(xml_input, min_length):
    grafs_list = []
    soup = BeautifulSoup(xml_input, "lxml")
    grafs = soup.find_all('p')
    for graf in grafs:
        # TODO: clean the output and remove tags
        # DFL
        graf = graf.get_text()
        if len(graf) >= min_length:
            if config.analysis['level'] == 'sentence':
                item = sent_tokenize(str(graf))
                for i in item:
                    if len(i) >= min_length:
                        grafs_list.append(i)
            elif config.analysis['level'] == 'paragraph':
                grafs_list.append(graf)
    return grafs_list


def generate_filelist(data_dir):
    file_list = []
    for root, subdirs, files in os.walk(os.path.abspath(data_dir)):
        for file in files:
            if file[-3:] == "xml":
                file_list.append(os.path.join(root, file))
    return file_list


def process_tei(data_dir, min_length):
    out_dict = {}
    file_list = generate_filelist(data_dir)

    for file in file_list:
        with open(file, 'r') as f:
            data = f.read()
        grafs = get_grafs(data, min_length)
        out_dict[file] = grafs
        
    return out_dict
