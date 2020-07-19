#Code that tracks a bounding box selection made by the user after pressing 's'
#Press 'q' to quit video stream

# import the necessary packages
from imutils.video import VideoStream
from imutils.video import FPS
import imutils
import time
import cv2
import math
from adafruit_servokit import ServoKit


# Initialize servokit
kit = ServoKit(channels=16)

#Trackers in opencv
OPENCV_OBJECT_TRACKERS = {
    "csrt": cv2.TrackerCSRT_create,
    "kcf": cv2.TrackerKCF_create,
    "boosting": cv2.TrackerBoosting_create,
    "mil": cv2.TrackerMIL_create,
    "tld": cv2.TrackerTLD_create,
    "medianflow": cv2.TrackerMedianFlow_create,
    "mosse": cv2.TrackerMOSSE_create
}

# grab the appropriate object tracker using our dictionary of
# OpenCV object tracker objects
tracker = OPENCV_OBJECT_TRACKERS["csrt"]()

# initialize the bounding box coordinates of the object we are going to track
initBB = None

 
print("[INFO] starting video stream...")
vs = VideoStream(src=0).start()
time.sleep(1.0)

# initialize the FPS throughput estimator
fps = None

counter = 0

old_anglex = 45
old_angley= 40

kit.servo[1].angle = old_anglex
kit.servo[0].angle = old_angley

# loop over frames from the video stream
while True:
	# grab the current frame, then handle if we are using a
	# VideoStream or VideoCapture object
	frame = vs.read()
	frame = cv2.flip(frame,1)
	# frame = frame[1] if args.get("video", False) else frame
	# time.sleep(0.03)
     
	# check to see if we have reached the end of the stream
	if frame is None:
		break
 
	# resize the frame (so we can process it faster) and grab the
	# frame dimensions
	frame = imutils.resize(frame, width=700)
	(H, W) = frame.shape[:2]

    # check to see if we are currently tracking an object
	if initBB is not None:
		# grab the new bounding box coordinates of the object
		(success, box) = tracker.update(frame)
 
		# check to see if the tracking was a success
		if success:
			(x, y, w, h) = [int(v) for v in box]
			cv2.rectangle(frame, (x, y), (x + w, y + h),
				(0, 255, 0), 2)
		# update the FPS counter
		fps.update()
		fps.stop()

		# get position of target
		center_pos_hor = x				# 0 - 700 (0 is left)
		center_pos_ver = y				# 0 - 500 (0 is top)
		x_pos = x + (w/2)
		y_pos = y + (h/2)

		#for horizontal
		#Angles from 0 to 90
		#frame from 0 to 700
		servoxangle = abs(90 - (math.floor((x_pos / 700) * 90))) 
	

		#for vertical
		#Angles from 0 to 40
		#frame from 0 to 500
		servoyangle= abs( 40 - (math.floor((y_pos / 500) * 40)))

		kit.servo[1].angle = servoxangle
		kit.servo[0].angle = servoyangle
		
		old_anglex =servoxangle
		old_angley =servoyangle

		# initialize the set of information we'll be displaying on
		    
		info = [
			("Tracker","csrt"),
			("Success", "Yes" if success else "No"),
			("FPS", "{:.2f}".format(fps.fps())),
			("Vertical", "{:.2f}".format(center_pos_ver)),
			("Horizontal", "{:.2f}".format(center_pos_hor)),
		]


		# loop over the info tuples and draw them on our frame
		for (i, (k, v)) in enumerate(info):
			text = "{}: {}".format(k, v)
			cv2.putText(frame, text, (10, H - ((i * 20) + 20)),
				cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

	counter = counter + 1
    # show the output frame
	cv2.imshow("Frame", frame)
	key = cv2.waitKey(1) & 0xFF
 
	# if the 's' key is selected, we are going to "select" a bounding
	# box to track
	if key == ord("s"):
		# select the bounding box of the object we want to track (make
		# sure you press ENTER or SPACE after selecting the ROI)
		initBB = cv2.selectROI("Frame", frame, fromCenter=False,
			showCrosshair=True)
 
		# start OpenCV object tracker using the supplied bounding box
		# coordinates, then start the FPS throughput estimator as well
		tracker.init(frame, initBB)
		fps = FPS().start()

    # if the `q` key was pressed, break from the loop
	elif key == ord("q"):
		break
		
vs.stop()
# close all windows
cv2.destroyAllWindows()
