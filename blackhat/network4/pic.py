import cv2

pic_dir = "Pictures/sniff/pics"
face_dir = "Pictures/sniff/faces"
file_name = open("lake.jpg","wb")

def face_detect(path, file_name):

	img		= cv2.imread(path)
	cascade = cv2.CascadeClassifier("haarcascade_fronyalface_aly.xml")
	rects	= cascade.detectMultiScale(img, 1.3, 4, cv2.cv.CV_HAAR_SCALE_IMAGE, (20, 20))

	if len(rects) == 0:
		return False

	rects[:, 2:] += rects[:, 2:]

	# hightlight the faces in the image
	for x1,y1,x2,y2 in rects:
		cv2.rectangle(img,(x1,y1), (x2,y2), (127,255,0), 2)

	cv2.imwrite("%s/%s-%s" % (face_dir,pcap_file,file_name),img)
	
	return True

if '__name__' == '__main__':
	try:
		face_detect("%s/%s" % (pic_dir,file_name), file_name)
	except:
		pass

