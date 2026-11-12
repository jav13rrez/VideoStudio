import os, sys, urllib.request
import fal_client
for l in open("/home/jav13rrez/VideoStudio/.env"):
    if l.startswith("FAL_KEY="): os.environ["FAL_KEY"] = l.strip().split("=",1)[1]
src, dst = sys.argv[1], sys.argv[2]
url = fal_client.upload_file(src)
r = fal_client.subscribe("fal-ai/birefnet/v2", arguments={"image_url": url, "output_format":"png"})
urllib.request.urlretrieve(r["image"]["url"], dst)
print(r["image"].get("width"), r["image"].get("height"))
