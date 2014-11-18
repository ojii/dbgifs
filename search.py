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
            if term.lower() in gif.name.lower():
                tmp_score += 1
        score = tmp_score / terms_count
        if score:
            results.append((score, gif))
    return [
        result for score, result in
        sorted(results, key=lambda result: result[0], reverse=True)
    ]
