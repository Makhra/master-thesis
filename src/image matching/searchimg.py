import pickle
import bow2
from stamps.models import ImList

im = ImList.objects.get(pk=216)
src = bow2.Searcher()
print src.query(im.id)[:10]