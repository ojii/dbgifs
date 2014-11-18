import shlex


def search_gifs(database, term):
    results = []
    terms = shlex.split(term)
    terms_count = len(terms)
    if not terms:
        return []
    for gif in database.gifs:
        tmp_score = 0
        for term in terms:
            if term.lower() in gif.path.lower():
                tmp_score += 1
        score = tmp_score / terms_count
        results.append((score, gif))
    return [
        result for score, result in
        sorted(results, key=lambda result: result[0], reverse=True)
    ]
