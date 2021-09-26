import cv2
import time
import PoseModule as pm
import random

cap = cv2.VideoCapture(0)
##cap.set(3,1280) #width
##cap.set(4,720) #height
pTime = 0
detector = pm.poseDetector()
initialization_flag = True

#function to get a random coordinate
def random_coord():
    x_coord = random.randint(200, 400)
    y_coord = random.randint(50, 300)

    return (x_coord, y_coord)
    
while True:
    #to aboid first frame when nothing is detected from throwing error
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

                #i need a few indicators
                is_duck = random.choice([False, True])
                duck_counter = 0
                is_dodge = random.choice([False, False, False, False, True]) #so 1 in 5 chance to get true
                dodge_couter = 0
                is_punch = random.choice([False, True])
                punch_counter = 0

                print('Game has started')

        #when game has started
        else:
            
            #do one punch first, this later maybe ### punch_list = [] #to store all the locations i should punch but that i have not punc
            if is_punch == True:
                #if its zero, means set new location to punch
                if punch_counter == 0:
                    x_coord, y_coord = random_coord()
                    cv2.circle(img, (x_coord, y_coord), 20, (0, 255, 0), 4)
                    punch_counter += 1

                #the 50 means i have 50 frames to hit the target, so i just keep putting it back on the screen
                elif punch_counter < 50:
                    cv2.circle(img, (x_coord, y_coord), 20, (0, 255, 0), 4)
                    punch_counter += 1

                    #if eithermy left or right hand in that target area, means ive hit the target
                    if (abs(left[1] - x_coord) <= 30 and abs(left[2] - y_coord) <= 30) or (abs(right[1] - x_coord) <= 30 and abs(right[2] - y_coord) <= 30):
                        cv2.putText(img, 'NICE', (x_coord, y_coord), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 3)
                        punch_counter = 0 #reset counter

                        is_punch = False #so itll go to the elif to become back true


                #times up, i didnt get to hit the target on time
                else:
                    punch_counter = 0 #reset counter
                    #tell me i missed
                    cv2.putText(img, 'MISSED', (x_coord, y_coord), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 3)

                    #and see if ill get another punch or not
                    is_punch = random.choice([False, True])

            #just keep asking until i get a true
            elif is_punch == False:
                is_punch = random.choice([False, True])

            #For thoe dodging
            if is_duck == True:
                if duck_counter == 0:
                    #get 2 coordinates which will form the line
                    coord1 = random_coord() #(x.y)
                    coord2 = random_coord()

                    cv2.line(img, coord1, coord2, (0,0,255), 2) #draw the line

                    duck_counter += 1

                #this is the warning phase, to warn where to duck
                elif duck_counter < 30:
                    #just redraw the line           ORANGE
                    cv2.line(img, coord1, coord2, (0,128,255), 5) #draw the line

                    duck_counter += 1

                #TIME TO DUCK
                elif duck_counter == 30:           #VERY RED
                    cv2.line(img, coord1, coord2, (51,51,255), 10) #draw the line

                    #check if im in the line, if i am, means i gothit
                    #just check the nose
                    #this is more complicated than i thought, ill do it later
                    #idea is to find the gradient of the line, get the x coordinate of the line using the y coord of the nose, then if its within 15 pixels, then its a hit
                    #but ll need to create a function to find gradient and a function to compare distance
                    
                    

                    #reset
                    duck_counter = 0
                    is_duck = False

                
            elif is_duck == False:
                is_duck = random.choice([False, False, False, False, True])
                

                    

            


        #FAILSAFE
        #to stop the program, put both my hands at the corners of the screen
        cv2.circle(img, (20, 10), 20, (255, 0, 0), 2)
        cv2.circle(img, (620, 10), 20, (255, 0, 0), 2)

        if abs(left[1] - 20) <= 15 and abs(left[2] - 10) <= 15 and abs(right[1] - 620) <= 15 and abs(right[2] - 10) <= 15:
            break


        ######
        #SHOW THE FRAME
        ######
        cv2.imshow("Image", img)
        if cv2.waitKey(5) & 0xFF == 27:
            break

    except:
        pass
    
cap.release()

