#################################
#DOCUMENTATION WAY
##################################
##import cv2
##import mediapipe as mp
##mp_drawing = mp.solutions.drawing_utils
##mp_pose = mp.solutions.pose
##
### For webcam input:
##cap = cv2.VideoCapture(0)
##with mp_pose.Pose(
##    min_detection_confidence=0.5,
##    min_tracking_confidence=0.5) as pose:
##  while cap.isOpened():
##    success, image = cap.read()
##    if not success:
##      print("Ignoring empty camera frame.")
##      # If loading a video, use 'break' instead of 'continue'.
##      continue
##
##    # Flip the image horizontally for a later selfie-view display, and convert
##    # the BGR image to RGB.
##    image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
##    # To improve performance, optionally mark the image as not writeable to
##    # pass by reference.
##    image.flags.writeable = False
##    results = pose.process(image)
##
##    # Draw the pose annotation on the image.
##    image.flags.writeable = True
##    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
##    mp_drawing.draw_landmarks(
##        image,
##        results.pose_landmarks,
##        mp_pose.POSE_CONNECTIONS)
##    cv2.imshow('MediaPipe Pose', image)
##    if cv2.waitKey(5) & 0xFF == 27:
##      break
##cap.release()


####################
#CV ZONE WAY
######################
import cv2
import mediapipe as mp
import time

mpDraw = mp.solutions.drawing_utils
mpPose = mp.solutions.pose
pose = mpPose.Pose()

cap = cv2.VideoCapture(0)
pTime = 0
while True:
    success, img = cap.read()
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = pose.process(imgRGB)
    # print(results.pose_landmarks)
    if results.pose_landmarks:
        mpDraw.draw_landmarks(img, results.pose_landmarks, mpPose.POSE_CONNECTIONS)
        for id, lm in enumerate(results.pose_landmarks.landmark):
            h, w, c = img.shape
            #print(id, lm)
            cx, cy = int(lm.x * w), int(lm.y * h)
            cv2.circle(img, (cx, cy), 5, (255, 0, 0), cv2.FILLED)

    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

    cv2.putText(img, str(int(fps)), (70, 50), cv2.FONT_HERSHEY_PLAIN, 3,
                (255, 0, 0), 3)

    cv2.imshow("Image", img)
    if cv2.waitKey(5) & 0xFF == 27:
        break
cap.release()
