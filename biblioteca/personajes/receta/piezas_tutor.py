import os, json, numpy as np
from PIL import Image, ImageFilter, ImageDraw
T = "/home/jav13rrez/VideoStudio/biblioteca/personajes/_trabajo/"
O = T + "tutor/"; os.makedirs(O+"ojos",exist_ok=True); os.makedirs(O+"bocas",exist_ok=True)
base = Image.open(T+"recortes/tutor_cara.png").convert("RGBA")
orig = Image.open(T+"hojas/tutor_cara.png").convert("RGB")
W,H = base.size
# cabeza: cara + cuello, sin chaqueta (el cuello queda detrás del cuello alto del torso)
CORTE = 1000
m = Image.new("L",(W,H),0); d = ImageDraw.Draw(m)
d.polygon([(0,0),(W,0),(W,780),(665,830),(655,CORTE),(215,CORTE),(205,830),(0,780)],fill=255)
m = m.filter(ImageFilter.GaussianBlur(3))
a = np.minimum(np.array(base.getchannel("A")),np.array(m))
# desvanece los últimos 40 px
fade = np.clip((CORTE-np.arange(H))/40.0,0,1)[:,None]; a = (a*fade).astype(np.uint8)
cab = base.copy(); cab.putalpha(Image.fromarray(a)); cab = cab.crop((0,0,W,CORTE)); cab.save(O+"cabeza.png")
OJOS=(200,455,700,645); BOCA=(245,695,655,885); PLUMA=22
def parche(var, caja, destino):
    v = Image.open(T+"variantes_tutor_alineadas/"+var+".png").convert("RGB")
    x0,y0,x1,y1 = caja; w,h = x1-x0,y1-y0
    mk = Image.new("L",(w,h),0); ImageDraw.Draw(mk).rounded_rectangle((PLUMA,PLUMA,w-PLUMA,h-PLUMA),radius=PLUMA*2,fill=255)
    mk = mk.filter(ImageFilter.GaussianBlur(PLUMA/1.6))
    p = v.crop(caja).convert("RGBA"); p.putalpha(mk); p.save(destino)
man = {"cabeza":{"archivo":"cabeza.png","tam":cab.size},"ojos":{},"bocas":{}}
ojos = {"neutros":None,"cerrados":"ojos_cerrados","muy_abiertos":"ojos_muy_abiertos","entornados":"ojos_entornados","mirada_izq":"ojos_mirada_izq","mirada_der":"ojos_mirada_der"}
bocas = {"cerrada":None,"abierta_pequena":"boca_abierta_pequena","abierta_grande":"boca_abierta_grande","o":"boca_o","ceno":"boca_ceno","sonrisa":"boca_sonrisa"}
os.makedirs(T+"variantes_tutor_alineadas",exist_ok=True)
orig.save(T+"variantes_tutor_alineadas/_base.png")
for n,v in ojos.items():
    parche(v or "_base",OJOS,O+f"ojos/{n}.png"); man["ojos"][n]={"archivo":f"ojos/{n}.png","caja":OJOS}
for n,v in bocas.items():
    parche(v or "_base",BOCA,O+f"bocas/{n}.png"); man["bocas"][n]={"archivo":f"bocas/{n}.png","caja":BOCA}
json.dump(man,open(O+"piezas.json","w"),indent=1)
# vista previa: cabeza con cada parche
def montar(oj,bo):
    im = cab.copy()
    for n,k in ((oj,"ojos"),(bo,"bocas")):
        p = Image.open(O+man[k][n]["archivo"]); im.alpha_composite(p,tuple(man[k][n]["caja"][:2]))
    return im
tiles=[montar(o,"cerrada") for o in ojos]+[montar("neutros",b) for b in bocas]
s=Image.new("RGB",(6*300,2*520),(255,0,255))
for i,t in enumerate(tiles):
    t=t.resize((300,int(300*t.height/t.width))); bg=Image.new("RGBA",t.size,(255,0,255,255)); bg.alpha_composite(t); s.paste(bg.convert("RGB"),((i%6)*300,(i//6)*520))
s.save("/tmp/claude-1000/-home-jav13rrez-VideoStudio/519c1b21-58af-4471-ab0d-be1e6182a8b6/scratchpad/chk6.png")
