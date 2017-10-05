import re


def _add_hit(hits, wikipath, score):
    hit = hits.get(wikipath.path, {'score': 0, 'obj': wikipath})
    hit['score'] += 1
    hits[wikipath.path] = hit
    return hits


def _search_path(wikipath, regex, hits):
    if regex.search(wikipath.name):
        hits = _add_hit(hits, wikipath, 1)

    if wikipath.is_node:
        for item in wikipath.items():
            hits = _search_path(item, regex, hits)

    if wikipath.is_leaf and (not wikipath.is_binary):
        try:
            file = open(wikipath.abs_path)
            for line in file:
                if regex.search(line):
                    hits = _add_hit(hits, wikipath, 1)
                    break
            file.close()
        except Exception as e:
            print(e)

    return hits


def get_hits_for_term_in_wiki(wiki, term):
    regex = re.compile(term, re.I)
    hits = _search_path(wiki.get_root(), regex, {})
    hitssorted = sorted(hits.values(), key=lambda x: x['score'])

    return [x['obj'] for x in hitssorted]
