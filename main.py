from ppadb.client import Client as AdbClient
import cv2, os
import numpy as np
import pytesseract
from PIL import Image
import requests
import json

def screencap(crop=False,x1=0,x2=0,y1=0,y2=0):
    capture = device.screencap()
    screen = cv2.imdecode(np.frombuffer(capture, np.uint8),cv2.IMREAD_COLOR)
    if crop:
        screen = screen[y1:y2, x1:x2]
    return screen

def saveSnap(image):
    filename = "screencap/{}.png".format(os.getpid())
    cv2.imwrite(filename, image)
    print('Saved.')

def ocr(image,method,l=None,debug=False):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    if method == "thresh":
        gray = cv2.threshold(gray, 0, 255,cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    elif method == "blur":
        gray = cv2.medianBlur(gray, 3)
    elif method == 'adaptive':
        gray = cv2.adaptiveThreshold(gray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY,11,2)

    filename = "temp/tmp.png"
    cv2.imwrite(filename, gray)
    if l == None:
        text = pytesseract.image_to_string(Image.open(filename),lang="jpn")
    else:
        text = pytesseract.image_to_string(Image.open(filename),lang=l)
    os.remove(filename)
    if debug:
        return gray
    else :
        return text

def googleDict(text):
    text = ''.join([line.strip() for line in text]) 
    # print(text)
    url = "https://clients5.google.com/translate_a/t?client=dict-chrome-ex&sl=ja&tl=en"+"&q=" + text
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36'
    }
    request_result = requests.get(url, headers=headers).json()

    merged_text = []
    print(request_result)
    for b in request_result:
        try:
            merged_text.append(b['trans'])
        except:
            pass
    print (merged_text)
    return merged_text

def imageRecognition(image,template,threshold,out,debug = False,multi=False,normalize=False,color=False):
    if color:
        res = cv2.cv2.matchTemplate(image,template,cv2.TM_CCORR_NORMED)
    else: 
        img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        res = cv2.matchTemplate(img_gray,template,cv2.TM_CCOEFF_NORMED)
    if normalize:
        cv2.normalize( res, res, 0, 1, cv2.NORM_MINMAX, -1 )
    if multi:
        w, h = template.shape[::-1]
        loc = np.where( res >= threshold)
        i = 0
        for pt in zip(*loc[::-1]):
            i += 1
            cv2.rectangle(image, pt, (pt[0] + w, pt[1] + h), (0,0,255), 1)
        if out == 'img':
            return image
        if out == 'bool':
            return i
    else:
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        (startX, startY) = max_loc
        endX = startX + template.shape[1]
        endY = startY + template.shape[0]
        if debug :
            print(max_val)
        if max_val > threshold:
            cv2.rectangle(image, (startX, startY), (endX, endY), (255, 0, 0), 3)
        if out == 'img':
            return image
        elif out == 'loc':
            x,y = findCenter(startX, endX, startY, endY)
            return y,x
        elif out == 'locr':
            return startY, endY, startX, endX
        elif out == 'bool':
            return max_val > threshold
        else:
            # put error here
            return None

if __name__ == "__main__":
    client = AdbClient(host="127.0.0.1", port=5037) #connect adb
    devices = client.devices() 
    if len(devices) == 0: # check if any devices is connected
        print('no device attached')
        quit() 
    device = devices[0] # sellect first devices
    # img = screencap()
    raw = ""
    txtbox = cv2.imread(r"assets/coba.png",cv2.TM_CCORR_NORMED)
    while True:
        img = screencap()
        raw_text = ocr(img[830:1020,560:1855], "thresh").replace(".","").replace("…","").replace("、", "").replace("・","")
        if raw != raw_text:
            print(raw_text)
            raw = raw_text
            translate = googleDict(raw_text)
            print(translate)
        
    # img = cv2.imread("screencap/27665.png")
    # img = img[830:1020,560:1855] # Landscape
    # saveSnap(img)

    
    # …...


