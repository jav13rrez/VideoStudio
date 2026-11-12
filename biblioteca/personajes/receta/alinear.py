import sys, glob, os, cv2, numpy as np
base = cv2.imread(sys.argv[1]); out = sys.argv[3]; os.makedirs(out, exist_ok=True)
H,W = base.shape[:2]
def prep(im): g=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY); return cv2.GaussianBlur(g,(5,5),0)
gb = prep(base)
for f in sorted(glob.glob(sys.argv[2]+"/*.png")):
    v = cv2.imread(f); v = cv2.resize(v,(W,H),interpolation=cv2.INTER_AREA)  # mismo tamaño
    warp = np.eye(2,3,dtype=np.float32)
    # ECC en dos escalas, sobre el contorno del pelo/hombros (zona sin expresión: tercio superior y hombros)
    mask = np.zeros((H,W),np.uint8); mask[:int(H*0.22),:]=255; mask[int(H*0.75):,:]=255
    try:
        cc,warp = cv2.findTransformECC(gb, prep(v), warp, cv2.MOTION_AFFINE, (cv2.TERM_CRITERIA_EPS|cv2.TERM_CRITERIA_COUNT,200,1e-6), mask, 5)
    except cv2.error as e: print("ECC falla", f, e); cc=0
    al = cv2.warpAffine(v, warp, (W,H), flags=cv2.INTER_LINEAR+cv2.WARP_INVERSE_MAP, borderMode=cv2.BORDER_REPLICATE)
    cv2.imwrite(os.path.join(out,os.path.basename(f)), al)
    d = np.abs(al.astype(int)-base.astype(int)).mean(axis=2)
    print(os.path.basename(f), "ecc=%.3f"%cc, "dif_pelo=%.1f"%d[:int(H*.2)].mean(), "dif_cara=%.1f"%d[int(H*.3):int(H*.5)].mean())
