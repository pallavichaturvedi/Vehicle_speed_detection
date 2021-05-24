
# import the necessary packages
import time
import math
import datetime
import cv2
import os
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk

# Defined Variables
HEIGHT = 10
DISTANCE = 20 # enter your distance-to-road value here
ACTUAL_DISTANCE = 0
MIN_SPEED = 10  # enter the minimum speed for saving images
SAVE_CSV = False  # record the results in .csv format in carspeed_(date).csv
THRESHOLD = 15
MIN_AREA = 20
BLURSIZE = (15,15)
FOV_H = 65    # Field of view
SHOW_BOUNDS = True
SHOW_IMAGE = True
VIEW = 'Video'
FILELOCATON = r'C:\Users\Adi\Desktop\pics'
mtperpixel = 0

#UI
view_select = [
'Horizontal'
'Vertical'
]

def show_entry_fields():
    global DISTANCE,FOV_H,MIN_SPEED,VIEW,HEIGHT,MIN_AREA
    DISTANCE=float(e3.get())
    #HEIGHT=float(E2.get())
    FOV_H=float(e1.get())
    MIN_SPEED=float(e2.get())
    VIEW=tkvar.get()
    MIN_AREA=float(e4.get())
    HEIGHT=float(e5.get())
    print("FOV: %s\n MIN SPEED: %s\n DIST FROM ROAD: %s\n MAX AREA OF VEHICLE: %s\n VIEW: %s\n HEIGHT: %s " % (FOV_H, MIN_SPEED,DISTANCE,MIN_AREA,VIEW,HEIGHT))
    #print("FOLDER LOCATION :" FOLDER_LOACTION)
    messagebox.showinfo("Message","Data Submitted")

def click():
    view_select=entry.get()


def folder_location():
    global FILELOCATON
    FILELOCATON = filedialog.askdirectory()
    print(FILELOCATON)

# on change dropdown value
def change_dropdown(*args):
    print( tkvar.get() )


window = Tk()

window.title('SPEED DETECTOR')

window.configure(bg='floral white')

gui_style = ttk.Style()
#gui_style.configure('My.TButton', foreground='#334353')
gui_style.configure('My.TFrame', background='floral white')

frame = ttk.Frame(window, style='My.TFrame')
frame.grid(column=1, row=1)


Label(window, text="FOV :",fg="blue").grid(row=0,sticky=W)
Label(window, text="MIN SPEED :",fg="blue").grid(row=0,column=5,sticky=W)
Label(window, text="DIST FROM ROAD :",fg="blue").grid(row=4,sticky=W,rowspan=4)
Label(window, text="MAX AREA OF VEHICLE :",fg="blue").grid(row=4,column=5,sticky=W,rowspan=4)
Label(window, text="FOLDER LOCATION :",fg="blue").grid(row=8,sticky=W,rowspan=4)
Label(window,text='FOOTAGE VIEW:',fg="blue").grid(row=12,column=0,sticky=W,rowspan=4)
Label(window,text='HEIGHT',fg="blue").grid(row=8,column=5,sticky=W,rowspan=4)



e1 = Entry(window,bd=5,bg="lavender blush")
e2 = Entry(window,bd=5,bg="lavender blush")
e3 = Entry(window,bd=5,bg="lavender blush")
e4 = Entry(window,bd=5,bg="lavender blush")
e5 = Entry(window,bd=5,bg="lavender blush")


e1.grid(row=0, column=1)
e2.grid(row=0, column=6)
e3.grid(row=4, column=1,rowspan=4)
e4.grid(row=4, column=6,rowspan=4)
e5.grid(row=8, column=6,rowspan=4)


window.grid_rowconfigure(200, minsize=200)
window.grid_columnconfigure(200, minsize=200)  

Button(window,text='Choose destinaton location',command=folder_location).grid(row=8, column=1,rowspan=4)

Button(window, text='Close', command=window.quit,fg="blue").grid(row=16, column=2, sticky=W, pady=4,rowspan=4)

Button(window, text='Submit', command=show_entry_fields,fg="blue").grid(row=16, column=4, sticky=W, pady=4,rowspan=4)

tkvar = StringVar(window)

# Dictionary with options
choices = { 'Camera','Video'}
tkvar.set('Video') # set the default option
 
popupMenu = OptionMenu(window, tkvar, *choices)
#Label(window).grid(row = 8, column = 5,sticky=E,rowspan=4)
popupMenu.grid(row = 12, column =1,sticky=W,rowspan=4)
 
# link function to change dropdown
tkvar.trace('w', change_dropdown)

window.mainloop( )

# Camera Variables
if VIEW== 'Video':
	camera = cv2.VideoCapture(r'C:\Users\Adi\Desktop\Hackathon\NumPlate\cv.mp4')
elif VIEW=='Camera':
	camera = cv2.VideoCapture(0)

IMAGEWIDTH = camera.get(3)
IMAGEHEIGHT = camera.get(4)
RESOLUTION = [IMAGEWIDTH,IMAGEHEIGHT]
print(RESOLUTION)
FPS = camera.get(5)
print(FPS)

# text on image
def prompt_on_image(txt):
    global image
    cv2.putText(image, txt, (10, 35),cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
     
# calculate speed
def get_speed(pixels, mtperpixel, secs):
    if secs > 0.0:
        return ((pixels * mtperpixel)/ secs) * 3.6 
    else:
        return 0.0
 
# calculate elapsed seconds
def secs_diff(endTime, begTime):
    diff = (endTime - begTime).total_seconds()
    return diff

# record speed in .csv format
def record_speed(res):
    global csvfileout
    f = open(csvfileout, 'a')
    f.write(res+"\n")
    f.close

# mouse callback function for drawing capture area
def draw_rectangle(event,x,y,flags,param):
    global ix,iy,fx,fy,drawing,setup_complete,image, org_image, prompt
 
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix,iy = x,y
 
    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing == True:
            image = org_image.copy()
            prompt_on_image(prompt)
            cv2.rectangle(image,(ix,iy),(x,y),(0,255,0),2)
  
    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        fx,fy = x,y
        image = org_image.copy()
        prompt_on_image(prompt)
        cv2.rectangle(image,(ix,iy),(fx,fy),(0,255,0),2)
        
# the following enumerated values are used to make the program more readable
WAITING = 0
TRACKING = 1
SAVING = 2
UNKNOWN = 0
LEFT_TO_RIGHT = 1
RIGHT_TO_LEFT = 2
BOTTOM_TO_TOP = 3
TOP_TO_BOTTOM = 4


# calculate actual distance

ACTUAL_DISTANCE = ((DISTANCE**2)+(HEIGHT**2))**0.5

# calculate the width of the image at the distance specified
frame_height_mt = 2*(math.tan(math.radians(FOV_H*0.5))*ACTUAL_DISTANCE)
print(frame_height_mt)
mtperpixel = frame_height_mt / float(IMAGEHEIGHT)
print("Image height in meter {} at {} from camera".format("%.0f" % frame_height_mt,"%.0f" % ACTUAL_DISTANCE))

"""
 state maintains the state of the speed computation process
 if starts as WAITING
 the first motion detected sets it to TRACKING
"""
"""
 if it is tracking and no motion is found or the x value moves
 out of bounds, state is set to SAVING and the speed of the object
 is calculated
 initial_x holds the x value when motion was first detected
 last_x holds the last x value before tracking was was halted
 depending upon the direction of travel, the front of the
 vehicle is either at x, or at x+w 
 (tracking_end_time - tracking_start_time) is the elapsed time
 from these the speed is calculated and displayed 
"""
 
state = WAITING
direction = UNKNOWN
initial_x = 0
last_x = 0
 
# other values used in program
base_image = None
abs_chg = 0
kmph = 0
secs = 0.0
ix,iy = -1,-1
fx,fy = -1,-1
drawing = False
setup_complete = False
tracking = False
text_on_image = 'No cars'
prompt = ''

# create an image window and place it in the upper left corner of the screen
cv2.namedWindow("Speed Camera")
cv2.moveWindow("Speed Camera", 0, 0)

# call the draw_rectangle routines when the mouse is used
cv2.setMouseCallback('Speed Camera',draw_rectangle)
 
# grab a reference image to use for drawing the monitored area's boundry

ret, image = camera.read()
org_image = image.copy()

if SAVE_CSV:
    csvfileout = "carspeed_{}.cvs".format(datetime.datetime.now().strftime("%Y%m%d_%H%M"))
    record_speed('Date,Day,Time,Speed,Image')
else:
    csvfileout = ''

prompt = "Define the monitored area - press 'c' to continue" 
prompt_on_image(prompt)
 
# wait while the user draws the monitored area's boundry
while not setup_complete:
    cv2.imshow("Speed Camera",image)
 
    #wait for for c to be pressed  
    key = cv2.waitKey(1) & 0xFF
  
    # if the `c` key is pressed, break from the loop
    if key == ord("c"):
        break

# the monitored area is defined, time to move on
prompt = "Press 'q' to quit" 
 
# since the monitored area's bounding box could be drawn starting 
# from any corner, normalize the coordinates
 
if fx > ix:
    upper_left_x = ix
    lower_right_x = fx
else:
    upper_left_x = fx
    lower_right_x = ix
 
if fy > iy:
    upper_left_y = iy
    lower_right_y = fy
else:
    upper_left_y = fy
    lower_right_y = iy
     
monitored_width = lower_right_x - upper_left_x
monitored_height = lower_right_y - upper_left_y
 
print("Monitored area:")
print(" upper_left_x {}".format(upper_left_x))
print(" upper_left_y {}".format(upper_left_y))
print(" lower_right_x {}".format(lower_right_x))
print(" lower_right_y {}".format(lower_right_y))
print(" monitored_width {}".format(monitored_width))
print(" monitored_height {}".format(monitored_height))
print(" monitored_area {}".format(monitored_width * monitored_height))
 

while (True):
    ret, frame = camera.read();

    #initialize the timestamp
    timestamp = datetime.datetime.now()
 
    # grab the raw NumPy array representing the image 
    image = frame
    if image is None:
        break;
    # crop area defined by [y1:y2,x1:x2]
    gray = image[upper_left_y:lower_right_y,upper_left_x:lower_right_x]
 
    # convert the fram to grayscale, and blur it
    gray = cv2.cvtColor(gray, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, BLURSIZE, 0)
 
    # if the base image has not been defined, initialize it
    if base_image is None:
        base_image = gray.copy().astype("float")
        lastTime = timestamp
        cv2.imshow("Speed Camera", image)
    """
     compute the absolute difference between the current image and
     base image and then turn eveything lighter gray than THRESHOLD into
     white
     """
    frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(base_image))
    thresh = cv2.threshold(frameDelta, THRESHOLD, 255, cv2.THRESH_BINARY)[1]
    
    # dilate the thresholded image to fill in any holes, then find contours
    # on thresholded image
    thresh = cv2.dilate(thresh, None, iterations=2)
    (_, cnts, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

    # look for motion 
    motion_found = False
    biggest_area = 0

    for c in cnts:
    # compute the center of the contour
        M = cv2.moments(c)
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])

 
    # examine the contours, looking for the largest one
    for c in cnts:
        (x1, y1, w1, h1) = cv2.boundingRect(c)
        # get an approximate area of the contour
        found_area = w1*h1 
        # find the largest bounding rectangle
        if (found_area > MIN_AREA) and (found_area > biggest_area):  
            biggest_area = found_area
            motion_found = True
            x = x1
            y = y1
            h = h1
            w = w1
            print(x,y,h,w)

    if motion_found:
        if state == WAITING:
            # intialize tracking
            state = TRACKING
            initial_x = x
            last_x = x
            initial_y = y
            last_y = y
            initial_time = timestamp
            last_kmph = 0
            text_on_image = 'Tracking'
            print(text_on_image)
            print("x-chg    Secs      KMPH  x-pos width")
        else:
            # compute the lapsed time
            secs = secs_diff(timestamp,initial_time)

            if secs >= 15:
                state = WAITING
                direction = UNKNOWN
                text_on_image = 'No Car Detected'
                motion_found = False
                biggest_area = 0
                base_image = None
                print('Resetting')
                continue             

            if state == TRACKING:       
                if y >= last_y:
                    direction = BOTTOM_TO_TOP
                    abs_chg = y + h - initial_y
                else:
                    direction = TOP_TO_BOTTOM  
                    abs_chg = initial_y - y
                kmph = get_speed(abs_chg,mtperpixel,secs)
                print("{0:4d}  {1:7.2f}  {2:7.0f}   {3:4d}  {4:4d}".format(abs_chg,secs,kmph,x,w))
                real_y = upper_left_y + y
                real_x = upper_left_x + x
                # is front of object outside the monitired boundary? Then write date, time and speed on image
                # and save it 
                if ((y <= 2) and (direction == TOP_TO_BOTTOM)) or ((y+h >= monitored_height - 2) and (direction == BOTTOM_TO_TOP)):
                    if (last_kmph > MIN_SPEED):    # save the image
                        # timestamp the image
                        cv2.putText(image, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),(10, image.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 1)
                        # write the speed: first get the size of the text
                        size, base = cv2.getTextSize( "%.0f kmph" % last_kmph, cv2.FONT_HERSHEY_SIMPLEX, 2, 3)
                        # then center it horizontally on the image
                        cntr_x = int((IMAGEWIDTH - size[0]) / 2) 
                        cv2.putText(image, "%.0f kmph" % last_kmph,(cntr_x , int(IMAGEHEIGHT * 0.5)), cv2.FONT_HERSHEY_SIMPLEX, 2.00, (0, 255, 0), 3)
                        # and save the image to disk
                        imageFilename = "car_at_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + ".jpg"
                        path = FILELOCATON
                        cv2.imwrite(os.path.join(path , imageFilename), image)
                        if SAVE_CSV:
                            cap_time = datetime.datetime.now()
                            record_speed(cap_time.strftime("%Y.%m.%d")+','+cap_time.strftime('%A')+','+cap_time.strftime('%H%M')+','+("%.0f" % last_kmph) + ','+imageFilename)
                    state = SAVING
                # if the object hasn't reached the end of the monitored area, just remember the speed 
                # and its last position
                last_kmph = kmph
                last_y = y
    else:
        if state != WAITING:
            state = WAITING
            direction = UNKNOWN
            text_on_image = 'Car Detected'
            print(text_on_image)
            
    # only update image and wait for a keypress when waiting for a car
    # This is required since waitkey slows processing.
    if (state == WAITING):    
 
        # draw the text and timestamp on the frame
        cv2.putText(image, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
            (10, image.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 1)
        cv2.putText(image, "Road Status: {}".format(text_on_image), (10, 20),
            cv2.FONT_HERSHEY_SIMPLEX,0.35, (0, 0, 255), 1)
     
        if SHOW_BOUNDS:
            #define the monitored area right and left boundary
            cv2.line(image,(upper_left_x,upper_left_y),(lower_right_x,upper_left_y),(0, 255, 0))
            cv2.line(image,(upper_left_x,lower_right_y),(lower_right_x,lower_right_y),(0, 255, 0))

       
        # show the frame and check for a keypress
        if SHOW_IMAGE:
            prompt_on_image(prompt)  
            cv2.imshow("Speed Camera", image)
            
        # Adjust the base_image as lighting changes through the day
        if state == WAITING:
            last_x = 0
            cv2.accumulateWeighted(gray, base_image, 0.25)
 
        state=WAITING;
        key = cv2.waitKey(1) & 0xFF
      
        # if the `q` key is pressed, break from the loop and terminate processing
        if key == ord("q"):
            break
  
# cleanup the camera and close any open windows
camera.release()
cv2.destroyAllWindows()
import prediction
