from scipy.cluster.vq import *
from os import listdir
from numpy import vstack, zeros, array
import numpy
import random
import time

class Trainer(object):
	def __init__(self,name):
		self.name = name
		self.voc = []
		self.idf = []
		self.trainingdata = []
		self.nbr_words = 0

	def train(self, featurefiles, k=1000, subsampling=10, n=1):
		nbr_images = len(featurefiles)
		
		descr = [] # desc will be on the form [[...[][][][]...][...[][][]...]...] (list of descriptors per image)
		descriptors = [] # descriptor on the form [...[][][][][]...] (list of descriptors)
		for i, img in enumerate(featurefiles):
			descr.append(img)
			if descriptors == []:
				descriptors = descr[0]
			else:
				descriptors = vstack((descriptors,descr[i])) #stack features for k-means / k-majority
		
		#k-means: last number determines numbers of run
		self.voc, distortion = kmeans(descriptors[::subsampling,:],k,n)

		#k-majority: for binary descriptors
		#self.voc = self.kmajority(descriptors, k)

		self.nbr_words = self.voc.shape[0]


		#processing each image and call project function
		imwords = zeros((nbr_images,self.nbr_words), dtype = numpy.int32)
		for i in range (nbr_images):
			imwords[i] = self.project(descr[i])

		#application of tf formula, numpy is needed to avoid using the math.sum function
		nbr_occurences = numpy.sum( (imwords > 0)*1 ,axis=0)

		#application of idf formula
		self.idf = numpy.log((1.0*nbr_images) / (1.0*nbr_occurences+1))
		
		self.trainingdata = featurefiles

	def project(self,descriptors):
		imhist = zeros((self.nbr_words), dtype = numpy.int32)
		words, distance = vq(descriptors,self.voc)
		for w in words:
			imhist[w] += 1
		return imhist

	def kmajority(self, collection, k):
		t1 = time.time()
		print "time: " + str(t1)
		centroids = self.generate(k)
		#centroids = random.sample(collection, k)
		change = 1
		while change == 1:
			change = 0
			vectorb = []
			for vector in collection[:5000]:
				h = 1000
				for cent in centroids:
					#print type(vector)
					#for each vector, we are looking for the closest matching vector
					hamd = self.hamdist(cent,vector)
					if hamd < h:
						h = hamd
						vec = [vector, cent]
				vectorb.append(vec)
			t2 = time.time()
			print "Stage 1: " + str(t2 - t1)
			#for each centroid if closest match of a vector: upvote

			for cent in centroids:
				nb = 0
				v = zeros((32,8), dtype=numpy.int32)
				for vector in vectorb:
					if self.hamdist(vector[1], cent) == 0:
						v = self.accumulate(v, vector[0])
						nb += 1
				if nb != 0:
					cent = self.vote(v, nb)
			t3 = time.time()
			print "Stage 2: " + str(t3 - t2)
			print "Total time: " + str(t3-t1)
		return centroids
#check if possible to get ride of the second for


	def hamdist(self,str1, str2):
		diffs = 0
		for j in range(32):
			bin1 = self.to_bin(str1[j], [0,0,0,0,0,0,0,0])
			bin2 = self.to_bin(str2[j], [0,0,0,0,0,0,0,0])
			for ch1, ch2 in zip(bin1, bin2):
				if ch1 != ch2:
						diffs += 1
		return diffs

	def accumulate(self, accu, value):
		for j in range(32):
			accu[j] = self.to_bin(value[j], accu[j])	
		return accu
	
	def vote(self, accu, nb):
		newcent = zeros(32, dtype=numpy.int32)
		for j in range(32):
			newcent[j] = self.to_int(accu[j], nb/2)
		return newcent

	def generate(self, k):
		gen = []
		for i in range(k):
			number = []
			for j in range(32):
				n = random.randrange(0, 255)
				number.append(n)
			gen.append(number)
		return array(gen)

	def to_bin(self, val, accu):
		i = 256
		for j in range(8):
			i = i/2
			if val >= i:
				val = val-i
				accu[j] += 1
		return accu

	def to_int(self, accu, nb):
		i = 256
		val = 0
		for j in range(8):
			i = i/2
			if accu[j] >= nb:
				val = val + i
		return val