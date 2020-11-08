from tifffile import TiffFile,imwrite
import cv2 as cv

import numpy as np

import matplotlib.pyplot as plt

dataPath="/home/facu/Desktop/HackathonMcGill2020/"

def addFlaggedPixelsToImg(img, flaggedPixels,color,alpha):
    for iFlag in flaggedPixels:
        x=iFlag[0]
        y=iFlag[1]
        img[x,y,:]=np.array(np.array(img[x,y,:],np.float)*(1.-alpha)+np.array(color,np.float)*alpha,np.uint8)


def imshowoverlay(binaryMap,grayImg_hist, title=None,color=[200,20,50],makePlot=True,alpha=0.7):
    x,y=np.where(binaryMap==255)
    flaggedPixels=[]
    for iPix in range(len(x)):
        flaggedPixels.append((x[iPix],y[iPix]))

    # attenuate grayImg_hist to make it more readable
    
    oldRange=[0,255]
    newRange=[0,120]
    
    grayImg_hist=np.array(np.round(np.interp(grayImg_hist,oldRange,newRange)),np.uint8)

    imgComp = np.stack([grayImg_hist,grayImg_hist,grayImg_hist],axis=2)

    addFlaggedPixelsToImg(imgComp,flaggedPixels,color=color,alpha=alpha)

    if makePlot:
        plt.figure(figsize=[18,18])
        plt.imshow(imgComp,cmap="ocean")
        plt.title(title,fontsize=28)
        plt.tight_layout()

    return imgComp

with TiffFile(dataPath+"afghanistanProcessed.tif") as tif:

    # tags=tif.pages[0].tags._dict
    # for field in tags.keys():
    #     if tags[field].name != "TileOffsets" and tags[field].name != "TileByteCounts":
    #         print(tags[field].name,": ",tags[field].value)
        
    afghanMap=np.array(tif.asarray())
    globalMax=np.max(afghanMap)
    # print("max global:",globalMax)

    # print("max R: ",np.max(afghanMap[:,:,0]))
    # print("max G: ",np.max(afghanMap[:,:,1]))
    # print("max B: ",np.max(afghanMap[:,:,2]))

    afghanMap=np.array(afghanMap,np.uint8)

im=afghanMap[6000:7000,6000:7000,:]

imGray=cv.cvtColor(im, cv.COLOR_RGB2GRAY)

im_hist=cv.equalizeHist(imGray)


edges= cv.Canny(cv.GaussianBlur(im_hist,ksize=(5,5),sigmaX=1,sigmaY=1),
    0.1*1024, 0.25*1024 )

imshowoverlay(edges,im_hist, title=f"Canny from cv2",color=[255,50,50],makePlot=True)


print('reading from disc complete')


plt.figure(figsize=[12,12])
plt.imshow(im_hist,cmap="Greys")
plt.tight_layout()

plt.show()

# imwrite(dataPath+'afghanistan_uint8.tif',
#     afghanMap,
#     compress=True
#     )

print('Done')