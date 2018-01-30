from stamps.models import ImList, ImWords, ImHistograms
import pickle
import numpy
import cv2

class Indexer(object):
	def __init__(self,voc):
		self.voc = voc

	def add_to_index(self,imname,descr):
		#if self.is_indexed(imname): return
		print 'indexing', imname

		#extract words from image which are represented in vocabulary?
		imwords = self.voc.project(descr)
		nbr_words = imwords.shape[0]

		stp = self.get_id(imname)
		hi = ImHistograms(stamp=stp, histogram=pickle.dumps(imwords), vocname=self.voc.name)
		hi.save()
		#insert project words in database
		words = imwords.nonzero()[0]
		for word in words:
			
			#word = imwords[i]
			#print word
			im = ImWords(stamp=stp, wordid=word, vocname=self.voc.name)
			im.save()
		
		
	def is_indexed(self, imname):
		try:
			stp = ImList.objects.get(filename=imname)
		except:
			stp = None
		return stp != None

	def get_id(self, imname):
		try:
			stp = ImList.objects.get(filename=imname)
			return stp
		except:
			#insert stamp
			stp = ImList(filename=imname)
			stp.save()
			return stp


class Searcher(object):
	def candidates_from_word(self,imword):
		c = []
		try:
			candidates = ImWords.objects.filter(wordid=imword)
			for candidate in candidates:
				c.append(candidate.stamp_id)
			#print c
			return c
		except:
			return c

	def candidates_from_histogram(self,imwords):
		words = imwords.nonzero()[0]
		candidates = []
		#for each visual word, call candidates_from_word
		for word in words:
			c = self.candidates_from_word(word)
			candidates+=c

		#sort by number of similaritudes and return list of imid
		tmp = [(w,candidates.count(w)) for w in set (candidates)]
		tmp.sort(cmp=lambda x,y:cmp(x[1],y[1]))
		tmp.reverse()
		return [w[0] for w in tmp]

	def get_imhistogram(self,imid):
		his = ImHistograms.objects.get(stamp_id=imid)
		return pickle.loads(his.histogram)
		#issue storing histogram, check size pickle vs size cell


	def query(self,imid):
		h = self.get_imhistogram(imid)
		
		#should return candidates
		candidates = self.candidates_from_histogram(h)
		print h
		matchscores = []
		#for each candidate, compare full histogram
		for imid in candidates:
			cand_h = self.get_imhistogram(imid)
			#computation of the distance:
			cand_dist = numpy.sqrt( numpy.sum( (h-cand_h)**2))

			matchscores.append((cand_dist,imid))

		matchscores.sort()
		#matchscores = [(distance, imid)...]
		return matchscores