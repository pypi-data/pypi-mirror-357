import re
import json
import numpy as np

from tqdm import tqdm
from litellm import completion

class Judge:
    """
    Abstract class for a Judge that evaluates topics against documents.
    """

    def __init__(self, model_name, max_rate):
        """
        Init of Abstract Judge class.

        :param model_name: LLM model name to use for querying. See https://docs.litellm.ai/docs/providers for supported models.
        :param max_rate: Judge scores are in the range of [1, max_rate].
        """

        self.model_name = model_name
        self.max_rate = max_rate

        self.missing_comma_regex = re.compile(r'"rate":[ ]*([0-9]+)([\n]*[ ]*)"reasoning":')

    def query_llm(self, prompt, temperature=0):
        response = completion(
            model=self.model_name,
            messages=[{"content": prompt, "role": "user"}],
            temperature=temperature
        )
        return json.loads(self.fix_json(response['choices'][0]['message']['content']))

    def fix_json(self, text):
        """
        Fix common issues in the JSON output from the LLM.
        """
        text = text.strip()

        text = self.missing_comma_regex.sub(r'"rate": \1,\2"reasoning":', text)

        if text[-1] != '}':
            text += '}'

        return text

class RelevanceJudge(Judge):
    """
    Implementation of the Relevance Judge.
    """

    system_prompt = """ 
    You will perform the following instructions as best as you can. 
    You will be presented with a topic and a text. Rate on a scale of 1 to {max_rate} whether the topic describes a part of the text ("1" = does not describe, "{mid_rate}" = somewhat describes, "{max_rate}" = describes well).
    Provide reasoning for the rate in one sentence only. 

    Please output the response in the following json format: {format}
    """
    output_format = """
    {
        "rate": <rate>
        "reasoning": "<reasoning>"
    }
    """
    user_prompt = """
    Topic: "{topic}",

    Text: \"\"\"{content}\"\"\"
    """

    expert_temperatures = [0.0, 0.5, 1.0]

    def __init__(self, model_name="openai/gpt-4o-mini", max_rate=100, expert_temperatures=None):
        """
        :param model_name: LLM model.
        :param max_rate: Maximum rate for the judge scores.
        :param expert_temperatures: Temperature values for the expert LLMs.
            The responses from the different temperatures are averaged to get the final score.
        """
        super().__init__(model_name, max_rate)

        if expert_temperatures:
            self.expert_temperatures = expert_temperatures

    def compose_prompt(self, topic, doc):
        return (
            self.system_prompt.format(
                max_rate=self.max_rate,
                mid_rate=self.max_rate // 2,
                format=self.output_format
            )
            +
            self.user_prompt.format(
                topic=topic,
                content=doc
            ).strip()
        ).strip()

    def measure(self, topic, doc):
        """
        Measure the relevance score and reasoning for a topic against a document.

        :param topic: The topic string.
        :param doc: The document string.
        :return: Tuple of (normalized rate float, list of raw responses).
        """
        prompt = self.compose_prompt(topic, doc)
        responses = [self.query_llm(prompt, temperature) for temperature in self.expert_temperatures]

        rate = np.nanmean([int(resp['rate']) / self.max_rate for resp in responses])
        reason = '\n'.join([f'Temperature={temp}: {resp["reasoning"]}' for temp, resp in zip(self.expert_temperatures, responses)])

        return rate, reason

    def compute_matrix(self, topics_set, doc_set):
        """
        Computes the relevance matrix for all topics against all documents.

        :param topics_set: List of topic strings.
        :param doc_set: List of document strings.
        :return: Tuple of relevance matrix numpy array.
        """
        R = np.zeros((len(topics_set), len(doc_set)))

        for i, topic in enumerate(topics_set):
            for j, doc in tqdm(enumerate(doc_set), total=len(doc_set), desc=f'*RELEVANCE* ~ Topic: "{topic}"'):
                score, reason = self.measure(topic, doc)
                R[i][j] = score

        return R

class OverlapJudge(Judge):
    """
    Implementation of the Overlap Judge.
    """

    system_prompt = """
    You will perform the following instructions as best as you can. 
    You will be presented with two topics: topic_1 and topic_2. Rate on a scale of 1 to {max_rate} whether topic_1 have the same meaning as topic_2 ("0" = different meaning, "{mid_rate}" = somewhat similar meaning, "{max_rate}" = same meaning).
    Provide reasoning for the rate in one sentence only. 

    Please output the response in the following json format: {format}
    """
    output_format = """
    {
        "rate": <rate>
        "reasoning": "<reasoning>"
    }
    """
    user_prompt = """
    topic_1: "{topic1}",
    topic_2: "{topic2}"
    """

    def __init__(self, model_name="openai/gpt-4o-mini", max_rate=100):
        """
        :param model_name: LLM model.
        :param max_rate: Maximum rate for the judge scores.
        """
        super().__init__(model_name, max_rate)

    def compose_prompt(self, topic1, topic2):
        return (
            self.system_prompt.format(
                max_rate=self.max_rate,
                mid_rate=self.max_rate // 2,
                format=self.output_format
            )
            +
            self.user_prompt.format(
                topic1=topic1,
                topic2=topic2
            ).strip()
        ).strip()

    def measure(self, topic_1, topic_2):
        """
        Measure the overlap score and reasoning between two topics.

        :param topic_1: First topic string.
        :param topic_2: Second topic string.
        :return: Tuple of (normalized rate float, reasoning string).
        """
        prompt = self.compose_prompt(topic_1, topic_2)

        resp = self.query_llm(prompt)

        rate = int(resp['rate']) / self.max_rate
        reason = resp['reasoning']

        return rate, reason

    def compute_matrix(self, topics_set):
        """
        Compute the overlap matrix for all pairs of topics.

        :param topics_set: List of topic strings.
        :return: Overlap matrix numpy array.
        """
        O = np.diag([1.0] * len(topics_set))

        for i in range(len(topics_set)):
            topic_i = topics_set[i]
            for j in tqdm(range(i), total=i, desc=f'*OVERLAP* ~ Topic: "{topic_i}"'):
                topic_j = topics_set[j]
                score, reason = self.measure(topic_i, topic_j)
                O[i][j] = score
                O[j][i] = score

        return O

class InterpretabilityJudge(Judge):
    """
    Implementation of the Interpretability Judge.
    """

    system_prompt = """
    You will perform the following instructions as best as you can. 
    You will be presented with a title representing a topic. Rate on a scale of 1 to {max_rate} whether the topic represented by the title is interpretable to humans ("0" = not interpretable, "{mid_rate}" = somewhat interpretable, "{max_rate}" = easily interpretable).
    Provide reasoning for the rate in one sentence only. 

    Please output the response in the following json format: {format}
    """
    output_format = """
    {
        "rate": <rate>
        "reasoning": "<reasoning>"
    }
    """
    user_prompt = """
    title: "{title}",
    """

    def __init__(self, model_name="openai/gpt-4o-mini", max_rate=100):
        """
        :param model_name: LLM model.
        :param max_rate: Maximum rate for the judge scores.
        """
        super().__init__(model_name, max_rate)

    def compose_prompt(self, topic):
        return (
            self.system_prompt.format(
                max_rate=self.max_rate,
                mid_rate=int(self.max_rate / 2),
                format=self.output_format
            )
            +
            self.user_prompt.format(
                title=topic
            ).strip()
        ).strip()

    def measure(self, topic):
        """
        Measure the interpretability score and reasoning for a topic.

        :param topic: Topic string.
        :return: Tuple of (normalized rate float, reasoning string).
        """
        prompt = self.compose_prompt(topic)

        resp = self.query_llm(prompt)

        rate = int(resp['rate']) / self.max_rate
        reason = resp['reasoning']

        return rate, reason

    def compute_matrix(self, topics_set):
        """
        Compute the interpretability scores for all topics.

        :param topics_set: List of topic strings.
        :return: Numpy array of interpretability scores.
        """
        I = np.zeros(len(topics_set))

        for i, topic in tqdm(enumerate(topics_set)):
            score, reason = self.measure(topic)
            I[i] = score

        return I