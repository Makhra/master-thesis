from stamps.models import ImWords, ImHistograms
import pickle
import numpy
import cv2


class ProcessImg(object):
	def __init__(self):

		#setup of the vocabulary
		with open('/home/thesis/vocabularytest1.pkl', 'rb') as f:
			self.voc = pickle.load(f)

		#preparation features extractors
		self.detector = cv2.FeatureDetector_create("SIFT")
		self.extractor = cv2.DescriptorExtractor_create("SIFT")


	def get_descriptors(self, image):

		#processing of the image, extraction of descriptors
		img = cv2.imread(image)
		keypoints = self.detector.detect(img)
		keypoints, descriptor = self.extractor.compute(img, keypoints)
		return descriptor

	def add_to_index(self,descr,stamp_id):

		#quantize descriptors to the vocabulary visual words
		imwords = self.voc.project(descr)
		nbr_words = imwords.shape[0]

		#save complete histogram
		hi = ImHistograms(stamp_id=stamp_id, histogram=pickle.dumps(imwords), vocname=self.voc.name)
		hi.save()

		#insert project words in database
		words = imwords.nonzero()[0]
		for word in words:
			im = ImWords(stamp_id=stamp_id, wordid=word, vocname=self.voc.name)
			im.save()
		
	def query_db(self,descr):
		
		#quantize descriptors to the vocabulary visual words
		imwords = self.voc.project(descr)
		nbr_words = imwords.shape[0]

		candidates = self.candidates_from_histogram(imwords)
		matchscores = []
		#for each candidate, compare full histogram
		for imid in candidates:
			cand_h = self.get_imhistogram(imid)
			
			#euclidian distance:
			cand_dist = numpy.sqrt( numpy.sum( (imwords-cand_h)**2))
			matchscores.append((cand_dist,imid))

		matchscores.sort()
		#matchscores = [(distance, imid)...]
		return matchscores[:10]

	def candidates_from_word(self,imword):
		c = []
		try:
			candidates = ImWords.objects.filter(wordid=imword)
			for candidate in candidates:
				c.append(candidate.stamp_id)
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
		