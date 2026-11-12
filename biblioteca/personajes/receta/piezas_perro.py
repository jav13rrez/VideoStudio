import os, json, shutil, numpy as np
from PIL import Image, ImageFilter, ImageDraw
T="/home/jav13rrez/VideoStudio/biblioteca/personajes/_trabajo/"; O=T+"perro/"; os.makedirs(O,exist_ok=True)
def recorte(n): return Image.open(T+f"recortes/{n}.png").convert("RGBA")
def pieza(img, poly, pluma=6):
    m=Image.new("L",img.size,0); ImageDraw.Draw(m).polygon(poly,fill=255); m=m.filter(ImageFilter.GaussianBlur(pluma))
    a=np.minimum(np.array(img.getchannel("A")),np.array(m)); p=img.copy(); p.putalpha(Image.fromarray(a))
    box=Image.fromarray(a).getbbox(); return p.crop(box), box[:2]
man={}
# cuerpos
for n,f in (("sentado_frente","perro_sentado_frente"),("sentado_perfil","perro_sentado_perfil_izq"),("de_pie_frente","perro_de_pie_frente"),("de_pie_perfil","perro_de_pie_perfil_izq")):
    im=recorte(f); im=im.crop(im.getchannel("A").getbbox()) if False else im; im.save(O+f"cuerpo_{n}.png"); man[f"cuerpo_{n}"]={"archivo":f"cuerpo_{n}.png","tam":im.size}
# orejas y cola (se rotan alrededor de su base; "origen" = esquina de la pieza en el cuerpo, "pivote" = base de la oreja/cola en el cuerpo)
sf=recorte("perro_sentado_frente")
p,o=pieza(sf,[(440,0),(560,0),(575,120),(540,175),(470,170),(440,120)]); p.save(O+"oreja_izq_sentado_frente.png"); man["oreja_izq_sentado_frente"]={"archivo":"oreja_izq_sentado_frente.png","origen":o,"pivote":(515,140)}
p,o=pieza(sf,[(600,10),(740,10),(735,170),(660,190),(605,150)]); p.save(O+"oreja_der_sentado_frente.png"); man["oreja_der_sentado_frente"]={"archivo":"oreja_der_sentado_frente.png","origen":o,"pivote":(655,160)}
sp=recorte("perro_sentado_perfil_izq")
p,o=pieza(sp,[(320,30),(440,30),(450,130),(420,205),(340,200),(320,120)]); p.save(O+"oreja_sentado_perfil.png"); man["oreja_sentado_perfil"]={"archivo":"oreja_sentado_perfil.png","origen":o,"pivote":(385,175)}
p,o=pieza(sp,[(930,790),(1317,760),(1317,1017),(960,1017),(910,900)],pluma=10); p.save(O+"cola_sentado_perfil.png"); man["cola_sentado_perfil"]={"archivo":"cola_sentado_perfil.png","origen":o,"pivote":(945,860)}
# parpadeo (parche en la cara de sentado_frente), escalado desde el primer plano
v=Image.open(T+"variantes_perro/ojos_cerrados.png").convert("RGB")
cx0,cy0,cx1,cy1=225,375,625,495      # zona de ojos en el primer plano
k=0.514; cen_cara=(422,436); cen_cuerpo=(578,208)
patch=v.crop((cx0,cy0,cx1,cy1)); w,h=patch.size; patch=patch.resize((int(w*k),int(h*k)),Image.LANCZOS).convert("RGBA")
mk=Image.new("L",patch.size,0); ImageDraw.Draw(mk).ellipse((8,6,patch.width-8,patch.height-6),fill=255); mk=mk.filter(ImageFilter.GaussianBlur(9)); patch.putalpha(mk)
pos=(int(cen_cuerpo[0]-(cen_cara[0]-cx0)*k), int(cen_cuerpo[1]-(cen_cara[1]-cy0)*k))
patch.save(O+"ojos_cerrados_sentado_frente.png"); man["ojos_cerrados_sentado_frente"]={"archivo":"ojos_cerrados_sentado_frente.png","origen":pos}
json.dump(man,open(O+"piezas.json","w"),indent=1)
# vista previa del parpadeo
a=sf.copy(); b=sf.copy(); b.alpha_composite(patch,pos)
box=(380,0,830,420); s=Image.new("RGB",(900,420),(255,0,255))
for i,im in enumerate((a,b)):
    bg=Image.new("RGBA",im.size,(255,0,255,255)); bg.alpha_composite(im); s.paste(bg.convert("RGB").crop(box),(i*450,0))
s.save("/tmp/claude-1000/-home-jav13rrez-VideoStudio/519c1b21-58af-4471-ab0d-be1e6182a8b6/scratchpad/chk9.png"); print(man["ojos_cerrados_sentado_frente"])
