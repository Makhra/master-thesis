import pickle
import cv2
import bow2
from os import listdir
import time

#path = "/home/thesis/media/full/"
path = "/home/thesis/img_base/"

imlist = listdir(path)

with open('/home/thesis/vocabularysifttest.pkl', 'rb') as f:
	voc = pickle.load(f)

indx = bow2.Indexer(voc)

#preparation features extractors
detector = cv2.FeatureDetector_create("SIFT")
extractor = cv2.DescriptorExtractor_create("SIFT")

#loop on images to upload
for filename in imlist[:200]:
	img = cv2.imread(str(path + filename))
	keypoints = detector.detect(img)
	keypoints, descriptor = extractor.compute(img, keypoints)
	indx.add_to_index(filename, descriptor)
