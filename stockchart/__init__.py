import cv2
import numpy as np
import pandas as pd

pos_color = (0,255,0)
neg_color = (0,0,255)
black = (0,0,0)
gray = (211, 211, 211)

def intround(x):
    return int(round(x))

def _translate_height(price, high, low, height):
    return intround(height*(high - price)/(high - low))

def _translate_width(day, days, width):
    #day begins with 0
    units = 2*days + (days-1) + 2
    unit_width = 1.0*width/units
    left = (3*day + 1)*unit_width
    center = left + unit_width
    right = center + unit_width
    return intround(left), intround(center), intround(right)

def basicChart(stock, height, width):
    #https://stackoverflow.com/questions/10465747/how-to-create-a-white-image-in-python
    img = np.zeros([height+1,width+1,3],dtype=np.uint8)
    img.fill(255) # or img[:] = 255
    days = len(stock)
    for i in range(0,days):
        columns = [c.lower() for c in stock.columns]
        stock.columns = columns
        left, center, right = _translate_width(i, days, width)
        boxtopprice = max(stock['open'].iloc[i], stock['close'].iloc[i])
        boxbottomprice = min(stock['open'].iloc[i], stock['close'].iloc[i])
        highprice = max(stock['high'])
        lowprice = min(stock['low'])
        boxtop = _translate_height(boxtopprice, highprice, lowprice, height)
        boxbottom = _translate_height(boxbottomprice, highprice, lowprice, height)
        linetop = _translate_height(stock['high'].iloc[i], highprice, lowprice, height)
        linebottom = _translate_height(stock['low'].iloc[i], highprice, lowprice, height)
        if stock['open'].iloc[i] > stock['close'].iloc[i]:
            color = neg_color
        else:
            color = pos_color
        cv2.rectangle(img, (left, boxtop), (right, boxbottom), color, -1)
        cv2.line(img, (center, boxtop), (center, linetop), black)
        cv2.line(img, (center, boxbottom), (center, linebottom), black)
    return img

def defaultChart(stock, height = 350, width = 600, upbull = None, downbull = None, headtext = None):
    legend = 75
    header = 40
    footer = 40
    v_partitions = 4
    img = np.zeros([height+header+footer+1,width+legend+1,3],dtype=np.uint8)
    img.fill(255)
    chart = basicChart(stock, height, width)
    if upbull == 1:
        upcolor = pos_color
    elif upbull == 0:
        upcolor = neg_color
    else:
        upcolor = gray
    if downbull == 1:
        downcolor = pos_color
    elif downbull == 0:
        downcolor = neg_color
    else:
        downcolor = gray
    cv2.line(chart, (0,0), (width,0), upcolor)
    cv2.line(chart, (0, height), (width, height), downcolor)
    
    dv = 1.0*height/v_partitions
    highprice = max(stock['high'])
    lowprice = min(stock['low'])
    fontsize = 0.5
    cv2.putText(img, str(round(highprice,2)), (width + 3, header),cv2.FONT_HERSHEY_SIMPLEX, fontsize, upcolor)
    cv2.putText(img, str(round(lowprice,2)), (width + 3, header+height),cv2.FONT_HERSHEY_SIMPLEX, fontsize, downcolor)
    dp = (highprice - lowprice)/v_partitions
    for i in range(1, v_partitions):
        hite = intround(i*dv)
        cv2.line(chart, (0, hite), (width, hite), gray)
        price = str(round(highprice - i*dp,2))
        cv2.putText(img, price, (width + 3, hite+header),cv2.FONT_HERSHEY_SIMPLEX, fontsize, black)
    img[header:height+header+1,0:width+1,:] = chart
    if headtext is not None:
        cv2.putText(img, headtext, (3, header - 3),cv2.FONT_HERSHEY_SIMPLEX, 2*fontsize, black)
    cv2.putText(img, stock.index[0], (3, height + header + 15),cv2.FONT_HERSHEY_SIMPLEX, fontsize, black)                                
    cv2.putText(img, stock.index[-1], (round(width*0.9), height + header + 10),cv2.FONT_HERSHEY_SIMPLEX, fontsize, black)    
    return img

def load_yahoo_csv(csvfile):
    return pd.read_csv(csvfile, index_col = 0)

def save(img, filename):
    cv2.imwrite(filename, img)

def show(img):
    """
Displays the image using OpenCV's imshow
    """
    flag = cv2.WINDOW_NORMAL
    #https://github.com/opencv/opencv/issues/7343
    wname = ""
    cv2.namedWindow(wname, flag) 
    cv2.imshow(wname, img)
    key = cv2.waitKey()
    cv2.destroyWindow(wname)
    return key