from typing import List

from .judges import RelevanceJudge, OverlapJudge, InterpretabilityJudge
from .scoring import compute_topics_set_score

def evaluate(
        topics_set: List[str],
        docs: List[str],
        model_name: str = "openai/gpt-4o-mini",
        max_rate: int = 100,
        expert_temperatures: List[float] = None,
        agg_weights: List[float] = None
):
    """
    Evaluate the quality of a given set of topics based on a set of documents.

    Parameters:
        topics_set (list): A list of topic names to be evaluated.
        docs (list): A list of document texts to compare against.
        model_name (str): The name of the language model to be used by the judges. Default is "openai/gpt-4o-mini".
        max_rate (int): The maximum rating score that can be assigned by the judges. Default is 100.
        expert_temperatures (list or None): Optional list specifying temperature settings for expert evaluations.
        agg_weights (Dict or None): Optional dict specifying weight of each aspect in the aggregate score.

    Returns:
        float: Aspect scores and aggregate score for the topics set and documents set.
    """
    assert len(topics_set) > 0, "topics_set must not be empty."
    assert len(docs) > 0, "docs must not be empty."

    relevance_judge = RelevanceJudge(model_name=model_name, max_rate=max_rate, expert_temperatures=expert_temperatures)
    overlap_judge = OverlapJudge(model_name=model_name, max_rate=max_rate)
    interpretability_judge = InterpretabilityJudge(model_name=model_name, max_rate=max_rate)

    R = relevance_judge.compute_matrix(topics_set, docs)
    O = overlap_judge.compute_matrix(topics_set)
    I = interpretability_judge.compute_matrix(topics_set)

    return compute_topics_set_score(R, O, I, agg_weights)