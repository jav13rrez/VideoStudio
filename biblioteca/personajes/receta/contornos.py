import os, shutil, json, cv2, numpy as np
from PIL import Image
R="/home/jav13rrez/VideoStudio/biblioteca/personajes/"; T=R+"_trabajo/"
COLOR=(24,18,16)
def contorno(src,dst,r):
    im=Image.open(src).convert("RGBA"); pad=r+2
    c=Image.new("RGBA",(im.width+2*pad,im.height+2*pad),(0,0,0,0)); c.paste(im,(pad,pad)); a=np.array(c.getchannel("A"))
    k=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2*r+1,2*r+1)); d=cv2.dilate((a>40).astype(np.uint8)*255,k); d=cv2.GaussianBlur(d,(3,3),0)
    base=np.zeros((*a.shape,4),np.uint8); base[...,:3]=COLOR; base[...,3]=d
    out=Image.fromarray(base); out.alpha_composite(c); out.save(dst); return pad
for ch in ("tutor","perro"): os.makedirs(R+f"{ch}/piezas",exist_ok=True)
pads={}
# Tutor
pads["tutor_cabeza"]=contorno(T+"tutor/cabeza.png",R+"tutor/piezas/cabeza.png",20)
pads["tutor_cuerpo_sentado_frente"]=contorno(T+"recortes/tutor_sentado_frente.png",R+"tutor/piezas/cuerpo_sentado_frente.png",5)
pads["tutor_cuerpo_sentado_perfil"]=contorno(T+"recortes/tutor_sentado_perfil_izq.png",R+"tutor/piezas/cuerpo_sentado_perfil.png",5)
for k in ("ojos","bocas"):
    os.makedirs(R+f"tutor/piezas/{k}",exist_ok=True)
    for f in os.listdir(T+f"tutor/{k}"): shutil.copy(T+f"tutor/{k}/{f}",R+f"tutor/piezas/{k}/{f}")
shutil.copy(T+"tutor/piezas.json",R+"tutor/piezas/piezas.json")
# Perro
for n in ("sentado_frente","sentado_perfil","de_pie_frente","de_pie_perfil"):
    pads[f"perro_cuerpo_{n}"]=contorno(T+f"perro/cuerpo_{n}.png",R+f"perro/piezas/cuerpo_{n}.png",5)
for f in os.listdir(T+"perro"):
    if f.startswith(("oreja","cola","ojos")) or f=="piezas.json": shutil.copy(T+"perro/"+f,R+"perro/piezas/"+f)
json.dump(pads,open(R+"_trabajo/margenes_contorno.json","w"),indent=1); print(pads)
