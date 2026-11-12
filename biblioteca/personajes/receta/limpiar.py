import sys, cv2, numpy as np
from PIL import Image
E=lambda r: cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2*r+1,2*r+1))
for f in sys.argv[1:]:
    im=np.array(Image.open(f.replace("recortes/","recortes_originales/")).convert("RGBA")); a=im[...,3]
    m1=cv2.erode((a>150).astype(np.uint8)*255,E(4))                   # silueta algo más cerrada
    inner=cv2.erode(m1,E(9))
    band=(((m1>0)&(inner==0))|(m1==0)).astype(np.uint8)*255; band=cv2.bitwise_and(band,cv2.dilate(m1,E(12)))                      # banda de borde con el blanco del fondo
    rgb=cv2.inpaint(np.ascontiguousarray(im[...,:3]),band,5,cv2.INPAINT_TELEA)
    al=cv2.GaussianBlur(m1,(5,5),0)
    out=np.dstack([rgb,np.minimum(a,al)]); Image.fromarray(out).save(f)
