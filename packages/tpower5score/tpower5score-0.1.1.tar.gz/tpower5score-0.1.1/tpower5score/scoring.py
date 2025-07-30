import numpy as np

from scipy.stats import hmean, kendalltau

def interpretability_score(I):
    return I.mean()

def topic_coverage_score(R):
    return R.mean()

def document_coverage_score(R):
    return R.max(axis=1).min()

def non_overlap_score(R, O):
    # Compute actual overlap based on topic-document relevance
    definition_overlap = O
    actual_overlap = ((1 / R.shape[1]) * np.matmul(R, R.T))

    np.fill_diagonal(definition_overlap, 0)
    np.fill_diagonal(actual_overlap, 0)

    overlap = np.maximum(definition_overlap, actual_overlap)

    return (1 - overlap).mean()

def inner_order_score(N, R):
    # Compute ranking of topics based on total document relevance
    ranking = np.zeros(R.shape[0])
    relevancy_score = R.sum(axis=1)
    for rank, idx in enumerate(np.argsort(relevancy_score)[::-1]):
        ranking[idx] = rank
    return np.maximum(0, kendalltau(list(range(N)), ranking).statistic)

def aggregate_score(interpretability, topic_coverage, document_coverage, overlap, rank, w):
    if w:
        assert 'Interpretability' in w, 'Weights must include "Interpretability".'
        assert 'Topic Coverage' in w, 'Weights must include "Topic Coverage".'
        assert 'Document Coverage' in w, 'Weights must include "Document Coverage".'
        assert 'Overlap' in w, 'Weights must include "Overlap".'
        assert 'Rank' in w, 'Weights must include "Rank".'
        assert w.values().sum() == 1, 'Weights must sum to 1.'

        w = [w['Interpretability'], w['Topic Coverage'], w['Document Coverage'], w['Overlap'], w['Rank']]

    return hmean([interpretability, topic_coverage, document_coverage, overlap, rank], weights=w)

def compute_topics_set_score(R, O, I, w=None):
    """
    Computes aspect scores based on Judge scores.

    :param R: Relevance Judge scores.
    :param O: Overlap Judge scores.
    :param I: Interpretability Judge scores.
    :param w: Importance weights for each aspect.
    :return: Tuple of (named component scores dict, aggregate score)
    """
    N = R.shape[0]
    M = R.shape[1]

    if N == 0 or M == 0:
        return 0

    interpretability = interpretability_score(I)
    topic_coverage = topic_coverage_score(R)
    document_coverage = document_coverage_score(R)
    overlap = non_overlap_score(R, O)
    rank = inner_order_score(N, R)

    score = aggregate_score(interpretability, topic_coverage, document_coverage, overlap, rank, w)

    return {
        'Interpretability': round(interpretability, 2),
        'Topic Coverage': round(topic_coverage, 2),
        'Document Coverage': round(document_coverage, 2),
        'Overlap': round(overlap, 2),
        'Rank': round(rank, 2)
    }, np.round(score, 2)
