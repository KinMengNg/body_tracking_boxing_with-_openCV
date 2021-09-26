import cv2
import time
import PoseModule as pm
import keyboard

cap = cv2.VideoCapture(0)
pTime = 0
detector = pm.poseDetector()
initialization_flag = True

#the problem is that despite the delay, now there may be 6 alphabets in the 0.3 seconds, which still makes it move erraticaly
#so need 2 loops
move_queue = [] #put every action into a queue that will be passed on to unity one at a time that way
time_counter = 0 #i want to calculate my next move only every 30 frames


#then i realised another problem: i move an inch and a whole arm it catches it in 1 frame, so the distance moved is same,
#to fix that, i move in that direction by the number of pixels change in that direction
#(or maybe a portion of it, might take too long since pixels are in 100s)
z_multiplier = 300 #for z since its not technically a coordinate

#function to find distance moved, returns num of pixels moved in that axis, i.e x, y OR z
def distance_moved(previous, current):
    distance = abs(previous - current)
    print(distance//10) #i want to see how are the values like

    return int(distance//10)

    
while True:
    try:
        ########
        #just loading the frame, get fps, and locate the landmarks
        ########
        success, img = cap.read()
        img = detector.findPose(img)
        lmList = detector.findPosition(img, draw=False) #FIND POSITIO OF EVERY POINT OF MY BODY
        #lm stands for landmark
        if len(lmList) != 0:
            #print(lmList[0])
            #lmList[0] is my nose
            #lmList[20] is my left index
            #lmList[19] is my right index
            nose = lmList[0]
            left = lmList[20]
            right = lmList[19] #its mirrored so more confusing
            #print('Left_hand: ', left)
            #print('Right_hand: ', right)
        
            #each of it is a list of id, x,y,z #z is a ratio
            cv2.circle(img, (nose[1], nose[2]), 10, (0, 0, 255), cv2.FILLED)
                            #width         height
            cv2.circle(img, (left[1], left[2]), 10, (0, 0, 255), cv2.FILLED)
            cv2.circle(img, (right[1], right[2]), 10, (0, 0, 255), cv2.FILLED)
            
        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime

        cv2.putText(img, str(int(fps)), (70, 50), cv2.FONT_HERSHEY_PLAIN, 3,
                    (255, 0, 0), 3)

        ##########
        #the game part
        ############
        #if game just started, need to identify initial position of hands first
        if initialization_flag == True:
            #from testing, coordinate of start location should be around:
            #for left (235, 155)
            #for right (430, 155)
            #thus make starting boxes to start the game
            cv2.circle(img, (235, 155), 20, (0, 255, 0), 2)
            cv2.circle(img, (430, 155), 20, (0, 255, 0), 2)

            #if both my fist are in the starting position, can start the game
            #THIS TOO SPECIFIC, HARD TO GETif (left[1], left[2]) == (235,155) and (right[1], right[2]) == (430,155):
            if abs(left[1] - 235) <= 15 and abs(left[2] - 155) <= 15 and abs(right[1] - 430) <= 15 and abs(right[2] - 155) <= 15:
                initialization_flag = False

                #get the current left and right coordinates, and depth ratio ie z
                                #x        y        z
                current_left = (left[1], left[2], left[3])
                current_right = (right[1], right[2], right[3])
                current_nose = (nose[1], nose[2], nose[3])
                print('Game has started')

        #when game has started
        else:
            #i want to calculate my next move only every 30 frames, cause unity too slow
            if time_counter == 10:
                #all the controls part
                #find direction moved by left hand rigt hand and nose
                previous_left = current_left
                previous_right = current_right
                previous_nose = current_nose

                current_left = (left[1], left[2], left[3])
                current_right = (right[1], right[2], right[3])
                current_nose = (nose[1], nose[2], nose[3])

                
                #left hand
                #means went to the right
                if current_left[0] - previous_left[0] > 0:
                    for i in range(distance_moved(current_left[0], previous_left[0])):
                        move_queue.append('d')
                        
                elif current_left[0] - previous_left[0] < 0:#need to do this, if just else itll mess up cause it considers 0 to move right
                    #went to the left
                    for i in range(distance_moved(current_left[0], previous_left[0])):
                        move_queue.append('a')

                #means went up
                if current_left[1] - previous_left[1] < 0: #cause top left corner is (0,0) 
                    counter  = 1
                    for i in range(distance_moved(current_left[1], previous_left[1])):
                        try:
                            move_queue.insert(counter, 'w') #want to insert each one at index 1,3,5,etc
                            counter += 2
                        #if index out of range, just add behind
                        except:
                            move_queue.append('w')
                elif current_left[1] - previous_left[1] > 0:
                    counter = 1
                    #went down
                    for i in range(distance_moved(current_left[1], previous_left[1])):
                        try:
                            move_queue.insert(counter, 's')
                            counter += 2
                        except:
                            move_queue.append('s')

                #means went forward
                if current_left[2] - previous_left[2] < 0: #remember z gets smaller as it gets closer to screen 
                    counter = 2
                    for i in range(distance_moved(current_left[2]*z_multiplier, previous_left[2]*z_multiplier)):
                        try:
                            move_queue.insert(counter, 'r') #add each at every 2,4,6,8,etc index
                            counter += 2
                        except:
                            move_queue.append('r')
                            
                elif current_left[2] - previous_left[2] > 0:
                    #went backwards
                    counter = 0
                    for i in range(distance_moved(current_left[2]*z_multiplier, previous_left[2]*z_multiplier)):
                        try:
                            move_queue.insert(counter, 'f')
                            counter += 2
                        except:
                            move_queue.append('f')


##                #Right hand
##                #means went to the right
##                if current_right[0] - previous_right[0] > 0:
##                    for i in range(distance_moved(current_right[0], previous_right[0])):
##                        move_queue.append('l')
##                elif current_right[0] - previous_right[0] < 0:
##                    #went to the left
##                    for i in range(distance_moved(current_right[0], previous_right[0])):
##                        move_queue.append('j')
##
##                #means went up
##                if current_right[1] - previous_right[1] < 0: #cause top left corner is (0,0) 
##                    for i in range(distance_moved(current_right[1], previous_right[1])):
##                        move_queue.append('i')
##                elif current_right[1] - previous_right[1] > 0:
##                    #went down
##                    for i in range(distance_moved(current_right[1], previous_right[1])):
##                        move_queue.append('k')
##
##                #means went forward
##                if current_right[2] - previous_right[2] < 0: #remember z gets smaller as it gets closer to screen 
##                    for i in range(distance_moved(current_right[2]*z_multiplier, previous_right[2]*z_multiplier)):
##                        move_queue.append('y')
##                elif current_right[2] - previous_right[2] > 0:
##                    #went backwards
##                    for i in range(distance_moved(current_right[2]*z_multiplier, previous_right[2]*z_multiplier)):
##                        move_queue.append('h')
##
##
##                #nose
##                #means went to the right
##                if current_nose[0] - previous_nose[0] > 0:
##                    for i in range(distance_moved(current_nose[0], previous_nose[0])):
##                        move_queue.append('b')
##                elif current_nose[0] - previous_nose[0] < 0:
##                    #went to the left
##                    for i in range(distance_moved(current_nose[0], previous_nose[0])):
##                        move_queue.append('v')
##
##                #means went up
##                if current_nose[1] - previous_nose[1] < 0: #cause top left corner is (0,0) 
##                    for i in range(distance_moved(current_nose[1], previous_nose[1])):
##                        move_queue.append('t')
##                elif current_nose[1] - previous_nose[1] > 0:
##                    #went down
##                    for i in range(distance_moved(current_nose[1], previous_nose[1])):
##                        move_queue.append('g')
##
##                #means went forward
##                if current_nose[2] - previous_nose[2] < 0: #remember z gets smaller as it gets closer to screen
##                    for i in range(distance_moved(current_nose[2]*z_multiplier, previous_nose[2]*z_multiplier)):
##                        move_queue.append('n')
##                elif current_nose[2] - previous_nose[2] > 0:
##                    #went backwards
##                    for i in range(distance_moved(current_nose[2]*z_multiplier, previous_nose[2]*z_multiplier)):
##                        move_queue.append('m')

                #reset
                time_counter = 0

            else:
                time_counter += 1

        #every loop only allow one action to be done
        if len(move_queue) != 0: #cant pop something if its empty
            keyboard.press_and_release(move_queue.pop(0)) #whatever is at the head of the queue

        #FAILSAFE
        #to stop the program, put both my hands at the corners of the screen
        cv2.circle(img, (20, 10), 20, (0, 255, 0), 2)
        cv2.circle(img, (620, 10), 20, (0, 255, 0), 2)

        if abs(left[1] - 20) <= 15 and abs(left[2] - 10) <= 15 and abs(right[1] - 620) <= 15 and abs(right[2] - 10) <= 15:
            break


        ######
        #SHOW THE FRAME
        ######
        cv2.imshow("Image", img)
        if cv2.waitKey(5) & 0xFF == 27:
            break

        #to reduce input lag with unity
        #time.sleep(0.1)
    except Exception as e:
        print(e)
        
#keyboard.wait('esc')#cause it doesnt seem to stop even after breaking
cap.release()

