import sys, os, glob, json
import numpy as np
from PIL import Image, ImageDraw
D = sys.argv[1]
sys.argv = ['fit.py', D, 'instax']
src = open('fit.py', encoding='utf-8-sig').read().split('W = {')[0].replace("phones = load('phone')", '')
exec(src)
P = {f: json.load(open(os.path.join(D, '..', 'fit_%s.json' % f))) for f in ('polaroid', 'instax')}
variants = [('原图', None), ('宝丽来', P['polaroid']), ('宝丽来 蓝减', dict(P['polaroid'], sB=0.25)), ('Instax', dict(P['instax'], k=1.15)), ('Instax 蓝减', dict(P['instax'], k=1.15, sB=0.3))]
files = sorted(glob.glob(os.path.join(D, 'phone', '*.jpg')))
pick = [files[i] for i in (1, 5, 9, 14, 20, 27, 33, 38) if i < len(files)]
T = 230
sheet = Image.new('RGB', (T*len(variants), (T+4)*len(pick)), 'white')
for r, f in enumerate(pick):
    im = Image.open(f).convert('RGB'); im.thumbnail((T, T)); a = np.asarray(im, dtype=np.float64)/255; sh = a.shape
    for c, (nm, p) in enumerate(variants):
        out = a if p is None else apply(a.reshape(-1, 3), [p[k] for k in NAMES]).reshape(sh)
        sheet.paste(Image.fromarray((np.clip(out, 0, 1)*255).astype(np.uint8)), (c*T, r*(T+4)))
sheet.save(os.path.join(D, '..', 'preview.jpg'), quality=85)
print([v[0] for v in variants])
