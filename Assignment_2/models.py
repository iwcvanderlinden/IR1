import numpy as np
from collections import Counter
import utils

def tf_idf(tf, idf):
    return (np.log(1 + tf).T * idf.T).T  # tf-idf

def tf_idf_score(tf_idf, query_indices):
    return tf_idf[query_indices[0:None], :].sum(axis=0)

def tf_idf_score_cosine(tf_idf, query_indices, idf):
    query_counts_per_index = Counter(query_indices)
    query_tf = np.array(query_counts_per_index.values())
    query_tf_idf = (np.log(1 + query_tf).T * idf[query_counts_per_index.keys()[0:None], :].T).T
    return utils.cosine_similarity(tf_idf[query_counts_per_index.keys()[0:None], :], query_tf_idf)


# add k3 term?
def bm25(tf, idf, k, b):
    doc_normalization = np.divide(np.sum(tf, axis=0), np.average(np.sum(tf, axis=0)))
    return (np.divide(((k+1) * tf), (k * ((1-b)+b*doc_normalization) + tf)).T * idf.T).T

def bm25_score(bm25, query_indices):
    return bm25[query_indices[0:None], :].sum(axis=0)


def query2indices(query, term2index):
    query_indices = []
    query_tokens = query.lower().split(' ')
    for term in query_tokens:
        if term in term2index:
            term_index = term2index[term]
            query_indices.append(term_index)
    return query_indices

def query2word_ids(query, token2id):
    query_word_ids = []
    query_tokens = query.lower().split(' ')
    for term in query_tokens:
        if term in token2id:
            word_id = token2id[term]
            query_word_ids.append(word_id)
    return query_word_ids

def construct_tf(topics, index, max_query_terms=0, max_documents=0):
    token2id, id2token, _ = index.get_dictionary()
    query_term_ids = collect_query_terms(topics, token2id)

    n_docs = index.document_count()
    # Take small sample for debugging purposes
    if max_query_terms > 0:
        query_term_ids = list(query_term_ids)[0:max_query_terms]
    if max_documents > 0:
        n_docs = max_documents

    # Count term frequencies per query term for each document
    tf = np.zeros([len(query_term_ids), n_docs])
    for doc_id in range(n_docs):  # doc_id is shifted to the right in tf matrix (1 -> 0)
        for term_id, term in enumerate(query_term_ids):
            if term in index.document(doc_id + 1)[1]:
                tf[term_id, doc_id] = index.document(doc_id + 1)[1].count(term)

    # Create dictionary to retrieve index of term in tf matrix
    term2index = {id2token[term_id]: index for index, term_id in enumerate(query_term_ids)}
    return tf, term2index


def collect_query_terms(topics, token2id):
    query_term_ids = set()
    for query_id, query_tokens in topics.items():
        query_tokens = query_tokens.lower().split(' ')
        query_id_tokens = [token2id.get(query_token, 0) for query_token in query_tokens]
        query_id_tokens = [word_id for word_id in query_id_tokens if word_id > 0]
        query_term_ids |= set(query_id_tokens)
    return list(query_term_ids)

