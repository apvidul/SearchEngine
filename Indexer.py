from __future__ import division
import json
import re
from struct import pack, unpack

def encode_number(number):

    bytes_list = []
    while True:
        bytes_list.insert(0, number % 128)
        if number < 128:
            break
        number = number // 128
    bytes_list[-1] += 128
    return pack('%dB' % len(bytes_list), *bytes_list)

def encode(numbers):

    bytes_list = []
    for number in numbers:
        bytes_list.append(encode_number(number))
    return b"".join(bytes_list)

def decode(bytestream):
    n=0
    numbers = []
    bytestream = unpack('%dB' % len(bytestream), bytestream)
    for byte in bytestream:
        if byte < 128:
            n = 128 * n + byte
        else:
            n = 128 * n + (byte - 128)
            numbers.append(n)
            n = 0
    return numbers

def get_ctf_dtf(term,offsets):
    start_pos, size, collection_term_frequency, document_term_frequency = offsets[term]
    return [collection_term_frequency,document_term_frequency]


def get_metadata(file):
    with open(file, 'r') as fp:
        data = json.load(fp)
        print "*******************METADATA**********************"
        print "Total number of unique terms",data['vocab_size']
        print "Total number of documents", data['total_docs']
        print "Total number of terms in the entire docs", data['total_terms']
        return data

def get_scene_id(doc_id):
    doc_id = str(doc_id)
    with open('docid_map.json', 'r') as fp:
        data = json.load(fp)
        return data[doc_id]


def average_scene_length(tt,td):
    return (tt/td)

def get_id_positons_ctf(term, file, offsets):
    inv_lst = extract_list(file,offsets[term])
    docs=[]
    pos=[]
    count = 0
    for i in inv_lst:
        docs.append(i[0])
        positions = i[1:]
        pos.append(positions)
        count += len(positions)
    ctf = count
    dtf = len(inv_lst)
    return docs,pos,ctf,dtf


def delta_encoding(lst):
    elst = []                         # Encoded List
    doc_pos_in_lst = 0
    for inner_lst in lst:             # For each list inside the inverted list
        if doc_pos_in_lst == 0:
            updated_id = inner_lst[0]
            new_doc_id = inner_lst[0]
            doc_pos_in_lst = 1        # Just a Flag
        else:
            updated_id = inner_lst[0] - new_doc_id           # Encoding the document_id
            new_doc_id = inner_lst[0]

        temp = []
        temp.append(updated_id)
        temp.append(inner_lst[1])
        if len(inner_lst) > 2:
            for i in range(2, len(inner_lst)):
                temp.append(inner_lst[i] - inner_lst[i-1])   # Encoding the word positions within an inner list
        elst.append(temp)
    return elst


def delta_decoding(lst):
    dlst = []                                                # Decoded list
    doc_pos_in_lst = 0
    for inner_lst in lst:
        if doc_pos_in_lst == 0:
            updated_id = inner_lst[0]
            new_doc_id = inner_lst[0]
            doc_pos_in_lst = 1
        else:
            updated_id = inner_lst[0] + new_doc_id            # Decoding document_ids
            new_doc_id = updated_id

        temp = []
        temp.append(updated_id)
        temp.append(inner_lst[1])

        if len(inner_lst) > 2:                                # Decoding word positions
            value = inner_lst[1]
            for i in range(2, len(inner_lst)):
                value = value + inner_lst[i]
                temp.append(value)
        dlst.append(temp)
    return dlst


def create_indexer(file):
    with open(file) as data_file:
        data = json.load(data_file)

    docid_scene_map = {}  # Maps the scene name with the document_ids/scene_ids
    play_lengths = {}     # Maps play lengths to play_ids
    doc_lengths = []      # Maps document/scene length with document/scene_ids
    vocab = {}            # The actual indexer, indexed by the vocabulary of the entire collection
    doc_id = -1           # the document_id starts from 0
    total_terms = 0
    for scene in data['corpus']:
        doc_id += 1
        docid_scene_map[doc_id] = scene['sceneId']
        counter = 0                                       # Keeps track of the position of a word in the text
        scene_words = re.split("\\s+", scene['text'])
        doc_lengths.append(len(scene_words))              # Tokenizing the text data

        for word in scene_words:
            total_terms += 1
            counter += 1
            if word in vocab:
                if vocab[word][-1][0] == doc_id:           # vocab[word][-1] gives the inverted list of the last doc
                    vocab[word][-1].append(counter)
                else:
                    vocab[word].append([doc_id, counter])
            else:
                vocab[word] = []                           # Adding a new word/key to the indexer table
                vocab[word].append([doc_id, counter])

        if scene['playId'] in play_lengths:
            play_lengths[scene['playId']] += counter
        else:
            play_lengths[scene['playId']] = counter
    return vocab, (doc_id+1), total_terms, docid_scene_map  # Returns indexer, total docs, total terms and doc_id map


# print len(all_doc_size)
#

def save_as_binary(vocab, file):
    offsets ={}
    with open(file, "wb") as binary_file:
        binary_file.seek(0,0)

        for word in vocab:

            inv_lst = vocab[word]
            start_pos = binary_file.tell()
            document_term_frequency = len(inv_lst)
            collection_term_frequency = 0
            for inner_lst in inv_lst:
                collection_term_frequency += (len(inner_lst)-1)
            compp = delta_encoding(vocab[word])

            to_string = str(compp)
            to_string = to_string.encode('utf8')
            size = len(to_string)
            binary_file.write(to_string)
            offsets[word] = [start_pos, size, collection_term_frequency, document_term_frequency] #vocab locations in file
    return offsets #saves and returns lookup table/offsets table

def save_as_binary_uncompressed(vocab, file):
    offsets ={}
    with open(file, "wb") as binary_file:
        binary_file.seek(0,0)

        for word in vocab:

            inv_lst = vocab[word]
            start_pos = binary_file.tell()
            document_term_frequency = len(inv_lst)
            collection_term_frequency = 0
            for inner_lst in inv_lst:
                collection_term_frequency += (len(inner_lst)-1)

            to_string = str(vocab[word])
            size = len(to_string)
            binary_file.write(to_string)
            offsets[word] = [start_pos, size, collection_term_frequency, document_term_frequency] #vocab locations in file
    return offsets #saves and returns lookup table/offsets table



def extract_list(file, offsets_data):
    start_pos, size, collection_term_frequency, document_term_frequency = offsets_data

    with open(file, "rb") as binary_file:
        binary_file.seek(start_pos)
        data = binary_file.read(size)
        data= data.decode('utf8')
        data= eval(data)
        decompp = delta_decoding(data)
    return  decompp

def extract_list_uncompressed(file, offsets_data):
    start_pos, size, collection_term_frequency, document_term_frequency = offsets_data

    with open(file, "rb") as binary_file:
        binary_file.seek(start_pos)
        data = binary_file.read(size)
        data= eval(data)

    return  data


choice= raw_input("Press y for compression and any other key for not compressing")
vocab, total_docs, total_terms, docid_scene_map = create_indexer("shakespeare-scenes.json") #in memory indexer

metadata = {'vocabulary':vocab.keys(),'vocab_size': len(vocab.keys()),'total_docs':total_docs,'total_terms':total_terms}



print "total_docs", total_docs
if choice=='y' or choice=='Y':
    offsets = save_as_binary(vocab, "test_compressed.bin")
    inverted_list = extract_list("test_compressed.bin", offsets['the'])  # retriving only the required term inverted list
         #convert list into string and then save as binary (No compression)
    with open('offsets_compressed.json', 'w') as fp:
        json.dump(offsets, fp)


else:
    offsets = save_as_binary_uncompressed(vocab, "test_uncompressed.bin")
    inverted_list = extract_list_uncompressed("test_uncompressed.bin", offsets['the'])

    with open('offsets_uncompressed.json', 'w') as fp:
        json.dump(offsets, fp)


with open('docid_map.json', 'w') as fp:
    json.dump(docid_scene_map, fp)
with open('metadata.json', 'w') as fp:
    json.dump(metadata, fp)





print "Average Scene Length",average_scene_length(total_terms,total_docs)
enc =encode([1,2,3])
print"vbyte encoding", enc
dec = decode(enc)
print"vbyte decoding", dec

