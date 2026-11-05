import sys, glob, os, json
import numpy as np
from PIL import Image
def srgb2lin(c): return np.where(c <= 0.04045, c/12.92, ((c+0.055)/1.055)**2.4)
M = np.array([[0.4124,0.3576,0.1805],[0.2126,0.7152,0.0722],[0.0193,0.1192,0.9505]])
def lab(rgb):
    xyz = srgb2lin(rgb) @ M.T / np.array([0.95047,1.0,1.08883])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787*xyz + 16/116)
    L = 116*f[...,1]-16; a = 500*(f[...,0]-f[...,1]); b = 200*(f[...,1]-f[...,2]); return L, a, b
def stats(fn):
    try: Image.open(fn).size
    except Exception: return None
    im = Image.open(fn).convert('RGB'); w, h = im.size
    cw, ch = int(w*0.55), int(h*0.55)
    im = im.crop(((w-cw)//2, (h-ch)//2, (w+cw)//2, (h+ch)//2)).resize((160, 160))
    rgb = np.asarray(im, dtype=np.float64).reshape(-1, 3)/255
    L, a, b = lab(rgb); C = np.hypot(a, b); H = (np.degrees(np.arctan2(b, a)) + 360) % 360
    if C.mean() < 9: return None                       # black-and-white or sepia
    hb = np.histogram(H[C > 15], bins=12, range=(0, 360))[0]
    if hb.sum() > 0 and hb.max() / hb.sum() > 0.62: return None   # duochrome / monochrome tint
    r = {'p1': np.percentile(L, 1), 'p5': np.percentile(L, 5), 'p50': np.percentile(L, 50), 'p95': np.percentile(L, 95), 'p99': np.percentile(L, 99),
         'C': C.mean(), 'C90': np.percentile(C, 90), 'Lsd': L.std(),
         'rgbmin': [float(np.percentile(rgb[:, i], 1)) for i in range(3)], 'rgbmax': [float(np.percentile(rgb[:, i], 99)) for i in range(3)]}
    for nm, lo, hi in (('sh', 0, 30), ('md', 30, 65), ('hi', 65, 101)):
        m = (L >= lo) & (L < hi) & (C < 18)
        r[nm+'_a'] = a[m].mean() if m.sum() > 40 else np.nan; r[nm+'_b'] = b[m].mean() if m.sum() > 40 else np.nan
        m2 = (L >= lo) & (L < hi)
        r[nm+'_C'] = C[m2].mean() if m2.sum() > 40 else np.nan
    for nm, lo, hi in (('red', 0, 50), ('skin', 40, 75), ('yel', 75, 105), ('grn', 105, 170), ('cyan', 170, 235), ('blue', 235, 300), ('mag', 300, 360)):
        m = (H >= lo) & (H < hi) & (C > 12)
        r[nm+'_C'] = C[m].mean() if m.sum() > 60 else np.nan
        r[nm+'_H'] = H[m].mean() if m.sum() > 60 else np.nan
        r[nm+'_L'] = L[m].mean() if m.sum() > 60 else np.nan
    return r
out = {}
for g in sys.argv[2:]:
    rows = [s for s in (stats(f) for f in sorted(glob.glob(os.path.join(sys.argv[1], g, '*.jpg')))) if s]
    keys = [k for k in rows[0] if not k.startswith('rgb')]
    med = {k: float(np.nanmedian([r[k] for r in rows])) for k in keys}
    med['rgbmin'] = np.median([r['rgbmin'] for r in rows], 0).round(3).tolist(); med['rgbmax'] = np.median([r['rgbmax'] for r in rows], 0).round(3).tolist()
    med['n'] = len(rows); out[g] = med
ks = [k for k in out[sys.argv[2]] if k not in ('rgbmin', 'rgbmax', 'n')]
print('%-8s' % 'metric' + ''.join('%10s' % g for g in sys.argv[2:]))
print('%-8s' % 'n' + ''.join('%10d' % out[g]['n'] for g in sys.argv[2:]))
for k in ks: print('%-8s' % k + ''.join('%10.2f' % out[g][k] for g in sys.argv[2:]))
for g in sys.argv[2:]: print(g, 'rgb p1', out[g]['rgbmin'], 'rgb p99', out[g]['rgbmax'])
json.dump(out, open(os.path.join(sys.argv[1], '..', 'stats.json'), 'w'), indent=1)
