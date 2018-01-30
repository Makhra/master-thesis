import trainer
import pickle
from os import listdir
import cv2

path = "/home/thesis/media/full/"
#path = "/home/thesis/img_base/"

tests = []
tests.append([1,100,1])
tests.append([2,100,10])
tests.append([3,1000,3])
tests.append([4,5000,1])
tests.append([5,1000,1])



imlist = listdir(path)
featlist = []
detector = cv2.FeatureDetector_create("SIFT")
extractor = cv2.DescriptorExtractor_create("SIFT")
for filename in imlist[:500]:
	img = cv2.imread(str(path + filename))
	keypoints = detector.detect(img)
	keypoints, descriptor = extractor.compute(img, keypoints)
	print filename
	featlist.append(descriptor)


for test in tests:
	tra = trainer.Trainer('stampsbench%s' % test[0])
	tra.train(featlist, test[1], 10,test[2])
	uri = '/home/thesis/vocabularytest%s.pkl' % test[0]

	with open(uri, 'wb') as f:
		pickle.dump(tra,f)
	print 'vocabulary is:', tra.name, tra.nbr_words