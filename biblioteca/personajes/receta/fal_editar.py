import os, sys, json, urllib.request, concurrent.futures as cf
import fal_client
for l in open("/home/jav13rrez/VideoStudio/.env"):
    if l.startswith("FAL_KEY="): os.environ["FAL_KEY"] = l.strip().split("=",1)[1]
modelo, src, salida = sys.argv[1], sys.argv[2], sys.argv[3]
pedidos = json.load(open(sys.argv[4]))  # {nombre: prompt}
url = fal_client.upload_file(src)
BASE = "Edit this photo. Keep the exact same man, identity, hair, skin, lighting, camera framing, crop, clothing and background pixel-aligned; change ONLY what is asked. "
def uno(item):
    n, p = item
    args = {"prompt": BASE + p}
    args["image_urls" if "nano-banana" in modelo else "image_url"] = [url] if "nano-banana" in modelo else url
    r = fal_client.subscribe(modelo, arguments=args)
    u = (r.get("images") or [r.get("image")])[0]["url"]
    urllib.request.urlretrieve(u, f"{salida}/{n}.png"); return n
os.makedirs(salida, exist_ok=True)
with cf.ThreadPoolExecutor(4) as ex:
    for n in ex.map(uno, pedidos.items()): print("ok", n)
