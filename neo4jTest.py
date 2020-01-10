from Neo4jDao import Neo4jDao
from Anime import Anime

if __name__ == "__main__":
    dao = Neo4jDao()
    shiki = dao.get_one_by_attr(Anime(), "Anime", "name", "Shiki")
    higurashi = dao.get_one_by_attr(Anime(), "Anime", "name", "Higurashi")
    results = dao.get_related_nodes(shiki, "related", Anime())
    print(results)





