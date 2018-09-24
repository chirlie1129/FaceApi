import cognitive_face as CF
import time,codecs,sys,cv2,os
#import person_group as pg

cascPath = 'haarcascade_frontalface_default.xml'
faceCascade = cv2.CascadeClassifier(cascPath)
def cam_face():
    i=True
    counter=0
    img_number=0
    vcap = cv2.VideoCapture("rtsp://admin:ccimodem@192.168.43.214/play2.sdp")
    while(img_number<6):
        counter=counter+1
        ret, frame = vcap.read()
        #cv2.imshow('VIDEO', frame)
        #cv2.waitKey(1)
        #print counter
        if counter==5:
            timeBegin = time.time()
            #i=False
            counter=0
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            faces = faceCascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30),
                flags=cv2.CASCADE_SCALE_IMAGE
            )
            if len(faces) == 1:
                img_name = 'webcam_'+str(img_number)+'.jpg'
                #print img_name
                cv2.imwrite(img_name,frame)
                img_number = img_number+1            
            img=frame
            for (x, y, w, h) in faces:
                cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.imshow('VIDEO', img)
            print time.time()-timeBegin
            cv2.waitKey(1)
            #cv2.destroyAllWindows()
            """
            if len(faces) == 1:
                img_name = 'webcam_'+str(img_number)+'.jpg'
                #print img_name
                cv2.imwrite(img_name,frame)
                img_number = img_number+1
                #break"""
    #Print 'training data get done'
    
def check_name(person_group_id,input_name,GroupList):
    person_id_list=[]
    #print GroupList
    for i,n in GroupList.iteritems():
        #print n,input_name   
        if n == input_name:
            person_id_list.append(i)  
            #print 'same name found'  
    #print person_id_list        
    for i in person_id_list:
        print i
        try:
            res=CF.person.delete(person_group_id,i)
            #print res
        except:
            print 'delete error'                        

def syn_group_list(person_group_id,wrt):
    result_getList = CF.person.lists(person_group_id)   
    #print  result_getList[0]
    #print type(result_getList[0])
    #print len(result_getList)

    person_dict={}
    if wrt == True:
        os.chdir(path)
        print 'change'+path
        person_list = codecs.open('person_group.py','w','utf-8')
        person_list.write("GroupList={}"+"\n")
        print os.getcwd()
    for i in range(len(result_getList)):
        if wrt == True:
            person_list.write('GroupList[u"'+result_getList[i][u"personId"]+'"]'+'='+'u"'+result_getList[i][u"name"]+'"'+'\n')
        person_dict[result_getList[i][u"personId"]]=result_getList[i][u"name"]
    print 'Build group list'     
    return person_dict    


###user enter new name
person_name = raw_input('Please enter your name:')

###detect and training
try:
    os.mkdir(person_name)
except:
    print 'File exist'    
path = 'C:/Users/Charliewk_chang/Desktop/faceAPI/Add_person_by_cam'
os.chdir(path+'/'+person_name)
print 'Look at the camera and do not move.'

cam_face()
cv2.destroyAllWindows()
print 'training data get done'

KEY = 'fb9315d60e364db9b96e0d2381c4fc83'  # Replace with a valid subscription key (keeping the quotes in place).
CF.Key.set(KEY)
person_group_id = '30f24380-20f1-11e7-acd7-0024210f3e1d'

###Sync web data
person_dict = syn_group_list(person_group_id,False)

###check name, delete duplecate
check_name(person_group_id,person_name,person_dict)

res = CF.person.create(person_group_id,person_name)
person_id = res['personId']

person_path = path+'/'+person_name
dirs=os.listdir(person_path)
os.chdir(person_path)

for path_face in dirs:
    try:
        res_add_face = CF.person.add_face(path_face,person_group_id,person_id)
    except:
        continue    
    print path_face,res_add_face


###sync web data
syn_group_list(person_group_id,True)
##training modle
print 'training modle'
res=CF.person_group.train(person_group_id)
print 'training done',res

"""
result_getList = CF.person.lists(person_group_id)   
print  result_getList[0]
print type(result_getList[0])
#print len(result_getList)
person_list = codecs.open('person_group.py','w','utf-8')
person_list.write("GroupList={}"+"\n")
for i in range(len(result_getList)):
    person_list.write('GroupList[u"'+result_getList[i][u"personId"]+'"]'+'='+'u"'+result_getList[i][u"name"]+'"'+'\n')
print 'Build group list' """    