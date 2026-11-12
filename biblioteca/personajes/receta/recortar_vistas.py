import sys
from PIL import Image
S = 1.92
D = "docs/documentos/"
O = "biblioteca/personajes/_trabajo/hojas/"
# (archivo, nombre, caja en coordenadas de la imagen mostrada a 2000 px)
CAJAS = [
 ("javier-de-pie-4k-v01.png","tutor_cara",(28,90,447,813)),
 ("javier-de-pie-4k-v01.png","tutor_de_pie_frente",(462,100,785,960)),
 ("javier-de-pie-4k-v01.png","tutor_de_pie_perfil_izq",(1200,100,1525,990)),
 ("javier-sentado-4k-v02.png","tutor_sentado_frente",(462,500,785,960)),
 ("javier-sentado-4k-v02.png","tutor_sentado_perfil_izq",(1200,500,1525,960)),
 ("merlin-de-pie-4k-v01.png","perro_cara",(14,70,568,815)),
 ("merlin-de-pie-4k-v01.png","perro_de_pie_frente",(572,50,1236,555)),
 ("merlin-de-pie-4k-v01.png","perro_de_pie_perfil_izq",(572,575,1236,1105)),
 ("merlin-sentado-4k-v01.png","perro_sentado_frente",(572,50,1258,560)),
 ("merlin-sentado-4k-v01.png","perro_sentado_perfil_izq",(572,575,1258,1105)),
]
for f,n,b in CAJAS:
    im = Image.open(D+f).convert("RGB")
    im.crop(tuple(int(v*S) for v in b)).save(O+n+".png")
    print(n)
