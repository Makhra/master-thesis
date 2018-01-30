import cv2
import itertools
from os import listdir
import time

detector_types = ["SIFT","SURF","ORB","BRISK","FREAK"]
path = "/home/thesis/img_base/"
files_list = listdir(path)
for det in detector_types:
	#starttimer
	for filename in files_list:
		#selection of original pictures
		if "ori" in filename:
			#(4 sets of 6 pictures including 1 original per set)
			t1 = time.time()
			img = cv2.imread(str(path + filename))
			detector = cv2.FeatureDetector_create(det)
			descriptor = cv2.DescriptorExtractor_create(det)
			ori_keypoints = detector.detect(img)
			print det
			print filename
			ori_keypoints, ori_descriptor = descriptor.compute(img, ori_keypoints)
			#second loop on the folder content, needed to compare each image to the selected one
			for filenm in files_list:
				totest = cv2.imread(str(path + filenm))
				tes_keypoints = detector.detect(totest)
				tes_keypoints, tes_descriptor = descriptor.compute(totest, tes_keypoints)

				#flann algorithm, comparison of keypoints
				if det == "SIFT" or det == "SURF":
					flann_params = dict(algorithm=1, trees=4) #KDTREE
				else:
					flann_params = dict(algorithm = 6,#LSH
                               table_number = 6, # 12
                               key_size = 12,     # 20
                               multi_probe_level = 1) #2

				flann = cv2.flann_Index(ori_descriptor, flann_params)
				index_match, dist = flann.knnSearch(tes_descriptor, 1, params={})
				del flann
				#index_match = list of matches / dist = list of corresponding matching distance (lower = better)
				#sorting of matches
				dist = dist[:,0]/2500.0
				dist = dist.reshape(-1,).tolist()
				index_match = index_match.reshape(-1).tolist()
				indices = range(len(dist))
				indices.sort(key=lambda i: dist[i])
				dist = [dist[i] for i in indices]
				index_match = [index_match[i] for i in indices]
				
				#selection of relevant matches
				final = []
				
				for i, dis in itertools.izip(index_match, dist):
				    if dis < 10 and det == "SIFT":
				        final.append(ori_keypoints[i])
				    elif det == "SURF":
				    	#SURF matching results are represented as really small numbers (e-05)
				    	final.append(ori_keypoints[i])
				    elif dis < 0.025 and det == "ORB":
				    	final.append(ori_keypoints[i])
				    elif dis < 0.06 and det == "BRISK":
				    	final.append(ori_keypoints[i])
				    else:
				        break
				print filenm + ": " + str(len(final))				
			t2 = time.time()
			print t2-t1
				#else:
				#	norm = cv2.NORM_HAMMING
				#	matcher = cv2.BFMatcher(norm)
				#	index_match = matcher.knnMatch(ori_descriptor, tes_descriptor, 2)

				#works with sift, not with surf (still as much results)
				#segfault error with FAST


	#stoptimer