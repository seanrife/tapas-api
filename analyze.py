import config

analysis_type = config.analysis['analysis_type']

def get_distance(text, item):
    if analysis_type == "lev":
        from similarity.normalized_levenshtein import NormalizedLevenshtein
        normalized_levenshtein = NormalizedLevenshtein()
        distance = normalized_levenshtein.distance(text, item)
        return distance
    if analysis_type == "lcs":
        from similarity.metric_lcs import MetricLCS
        metric_lcs = MetricLCS()
        distance = metric_lcs.distance(text, item)
        return distance
    if analysis_type == "shingle":
        from similarity.qgram import QGram
        qgram = QGram(config.analysis["qgram_val"])
        distance = qgram.distance(text, item)
        return distance
    if analysis_type == "ngram":
        from similarity.ngram import NGram
        ngram = NGram(config.analysis["ngram_val"])
        distance = ngram.distance(text, item)
        return distance
