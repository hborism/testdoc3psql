import os
import sys
from PIL import Image
import base64



def createIcon(filename, newname ,size):
    ratio = size, size
    im = Image.open(filename)
    im.thumbnail(ratio)
    im.save(newname+'_ICON.jpg',"JPEG")
    
    with open(newname+'_ICON.jpg', "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())

    s = str(encoded_string)
    s = s.replace(s[:2],'')
    s = s.replace(s[len(s)-1:],'')

    os.remove(newname+'_ICON.jpg')

    f = open(newname+'_ICON', 'w')
    f.write('data:image/png;base64,'+s)
    f.close()
    
    print("SUCCESS")


if __name__ == "__main__":
    filename = str(sys.argv[1])
    newname = str(sys.argv[2])
    size = int(sys.argv[3])
    createIcon(filename, newname, size)
