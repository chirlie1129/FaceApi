import time,codecs,sys,cv2,urllib,urllib2,json,requests
import numpy as np
begin=time.time()
import cognitive_face as CF
from uploadPhoto import UploadPic
import threading
Procees_timer=20
opencv_retry=10
url=''
url_get=False

KEY = 'c6f3f4772e7a441eaaa9906f98e53182'  # Replace with a valid subscription key (keeping the quotes in place).
CF.Key.set(KEY)
person_group_id = '7c2d7e4f-3ab4-11e7-878f-0024210f3e1d'
#vcap = cv2.VideoCapture("rtsp://admin:ccimodem@192.168.43.214/play2.sdp")
cascPath = 'haarcascade_frontalface_default.xml'
faceCascade = cv2.CascadeClassifier(cascPath)


#try:
    #import person_group as PG
    #print "Get group list"
#except:
#import build_group
import person_group as PG
print "Get group list"

def cam_http_face(ID):
    bytes = ''
    counter=0
    det_count=0
    try:
        if ID == 'SN001':
            stream=urllib.urlopen('http://admin:ccimodem@192.168.200.56/cgi/mjpg/mjpg.cgi')
        else:
            stream=urllib.urlopen('http://admin:ccimodem@192.168.200.162/cgi/mjpg/mjpg.cgi')
    except:
        print "camera connection fail"
        time.sleep(10)
        return False
    while True:
        cap_t=time.time()
        #stream=urllib.urlopen('http://192.168.1.1:8080/?action=snapshot&n=999')
        #stream=urllib.urlopen('http://172.20.10.3:8080/?action=snapshot&n=999')
        bytes+=stream.read(1024)
        a = bytes.find('\xff\xd8')
        b = bytes.find('\xff\xd9')
        if a!=-1 and b!=-1:
            jpg = bytes[a:b+2]
            bytes= bytes[b+2:]
            #frme = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8),cv2.CV_LOAD_IMAGE_COLOR)
            #frame = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8),cv2.IMREAD_COLOR)
            counter=counter+1
            print counter
            if counter == 5:
                #jpg = bytes[a:b+2]
                #bytes= bytes[b+2:]
                frame = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8),cv2.IMREAD_COLOR)
                counter =0
                det_count = det_count+1
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = faceCascade.detectMultiScale(
                    gray,
                    scaleFactor=1.1,
                    minNeighbors=5,
                    minSize=(60, 60),
                    flags=cv2.CASCADE_SCALE_IMAGE
                )
                print time.time()-cap_t
                print len(faces)
                if len(faces):
                    cv2.imwrite(ID+'.jpg',frame)
                    return True
                #for (x, y, w, h) in faces:
                    #cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                #cv2.imshow('i',frame)
                #cv2.waitKey(1)
                if det_count == opencv_retry:
                    print 'Reach max detect retry times'
                    #print time.time()-time_20				
                    #break
                    return False
                    #sys.exit()    
                

def cam_face():
    i=True
    counter=0
    vcap = cv2.VideoCapture("rtsp://admin:ccimodem@192.168.43.214/play2.sdp")
    time_20=time.time()
    det_count=0
    while(i):
        time_count_1=time.time()

        counter=counter+1
        ret, frame = vcap.read()
        #print time.time()-time_count_1
        #cv2.imshow('VIDEO', frame)
        #cv2.waitKey(1)
        #print counter
        
        if counter==5:
            det_count = det_count+1
            print det_count
            #ret, frame = vcap.read()
            timeBegin = time.time()
            #i=False
            counter=0
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            faces = faceCascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(60, 60),
                flags=cv2.CASCADE_SCALE_IMAGE
            )
            #img=frame
  
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.imshow('VIDEO', frame)
            print time.time()-timeBegin
            cv2.waitKey(1)
                       
            if len(faces) == 1:
                #return frame
                cv2.imwrite('webcam.jpg',frame)
                vcap.release()
                #break
                return True
            if det_count == opencv_retry:
                print 'Reach max detect retry 20 times'
                print time.time()-time_20				
                #break
                return False
                #sys.exit()
def upload_pic_thread(ID): 
    global url
    url = ''
    global url_get
    try:
        req=urllib2.Request("https://aiportaltest-161002.appspot.com/upload_url")
        r1 = urllib2.urlopen(req,timeout=1)
        decodejson = json.load(r1)
        upload_url=decodejson['uploadURL']
        r=requests.post(upload_url,files={'content':open(ID+'.jpg','rb')})
        Photo_publicURL=r.content
        url=Photo_publicURL
    except:
        print 'url time out'
    if url!='':
        url_get=True
    print url
    #Image_url = 'Image url'
    #Recognized_valid_user_name = 'Recognized valid user name'  

def face_rec(data):
    whole_start=time.time()            
    #thread=threading.Thread(target=upload_pic_thread)
    #thread.start()
    j=True
    ID = data['Event']['id']
    while(j):
        opencv_T=time.time()
        opencv_res = cam_http_face(ID)
        print time.time()-opencv_T
        if opencv_res != True:
            data['Event']['Detect']['parameters']['value']=[]
            data['Event']['Detect']['parameters']['url']=''
            return data #'Detect none'
        thread=threading.Thread(target=upload_pic_thread,args=(ID,))
        thread.start()       

        start = time.time()
        # You can use this example JPG or replace the URL below with your own URL to a JPEG image.
        image_path=ID+'.jpg'
        try:
            result_detect = CF.face.detect(image_path)
        except:
            print 'network issue'
            return
        print result_detect
        #print 
        if len(result_detect) == 0:
            print 'no faces in picture, please try again'
            print time.time()-start 
        else:    
            face_ids=[]
            for i in range(len(result_detect)):
                face_ids.append(result_detect[i][u'faceId'])
            #faceid = result[0][u'faceId']
            try:
                result_identify = CF.face.identify(face_ids,person_group_id)
                print result_identify
            except:
                print 'timeouttimeouttimeouttimeouttimeout'
                return
            print time.time()-start

            #print result_identify
            #try:
            name=[]
                #print result_identify[0][u'candidates'][0][u'personId']
            for i in range(len(result_identify)):
                try:
                    personId = result_identify[i][u'candidates'][0][u'personId']
                    name.append(PG.GroupList[personId])

                    print 'Identified in group : '+PG.GroupList[personId]
                    
                except:
                    name.append('unknow')
            thread.join(2)
            

            while(name):	
                data['Event']['Detect']['parameters']['url']=url
                data['Event']['Detect']['parameters']['value']=name
                return data

    
        if time.time()-whole_start>Procees_timer:
            print 'Reach max working time 30s'
            return #'Overtime'
            #sys.exit() 


