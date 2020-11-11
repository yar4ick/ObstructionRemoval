from PIL import Image

def image_converting(img):
    if img.size[0] > img.size[1]:
        basewidth = 960
        w_percent = (basewidth / float(img.size[0]))
        h_size = int((float(img.size[1]) * float(w_percent)))
        img_resized = img.resize((basewidth, h_size))
    elif img.size[0] < img.size[1]:
        baseheight = 960
        h_percent = (baseheight / float(img.size[1]))
        w_size = int((float(img.size[0]) * float(h_percent)))
        img_resized = img.resize((w_size, baseheight))
    else:
        img_resized = img.resize((basewidth, baseheight))
    return img_resized