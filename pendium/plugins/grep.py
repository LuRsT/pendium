from pendium.plugins import ISearchPlugin


class Grep(ISearchPlugin):
    search_speed = 2  # Quicker plugins get chosen first

    def _add_hit(self, hits, wikipath, score):
        hit = hits.get(wikipath.path, {"score": 0, "obj": wikipath})
        hit["score"] += 1
        hits[wikipath.path] = hit
        return hits

    def _search_path(self, wikipath, regex, hits):
        if regex.search(wikipath.name):
            hits = self._add_hit(hits, wikipath, 1)

        if wikipath.is_node:
            for item in wikipath.items():
                hits = self._search_path(item, regex, hits)

        if wikipath.is_leaf and (not wikipath.is_binary):
            # match content
            try:
                file = open(wikipath.abs_path)
                for line in file:
                    if regex.search(line):
                        hits = self._add_hit(hits, wikipath, 1)
                        break
                file.close()
            except Exception as e:
                print(e)

        return hits

    def dosearch(self, wiki, term, regex):
        hits = self._search_path(wiki.root(), regex, {})
        hitssorted = sorted(hits.values(), key=lambda x: x["score"])

        return [x["obj"] for x in hitssorted]
