# Tpower5Score
An automatic evaluation package for assessing the quality of LLM-generated multi-document topic sets.

## 📦 How to install

```cmd
pip install tpower5score
```

## 🚀 How to use

```python
    topics_set = [<topics_set>]
    docs = [<documents>]

    agg_weights = {
        'Interpretability': 0.2,
        'Topic Coverage': 0.2,
        'Document Coverage': 0.2,
        'Overlap': 0.2,
        'Rank': 0.2
    }

    aspects, agg_score = tpower5score.evaluate(topics_set, docs)
```

Or see working example in [examples/main.py]()

## 📖 Citation

If you use this package in your work, please cite:

```bibtex
@article{
  title={$T^5Score$: A Methodology for Automatically Assessing the Quality of LLM Generated Multi-Document Topic Sets},
  author={Trainin Itamar, Omri Abend},
}