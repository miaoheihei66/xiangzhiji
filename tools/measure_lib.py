import numpy as np
def srgb2lin(c): return np.where(c <= 0.04045, c/12.92, ((c+0.055)/1.055)**2.4)
M = np.array([[0.4124,0.3576,0.1805],[0.2126,0.7152,0.0722],[0.0193,0.1192,0.9505]])
def lab(rgb):
    xyz = srgb2lin(np.clip(rgb,0,1)) @ M.T / np.array([0.95047,1.0,1.08883])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787*xyz + 16/116)
    return 116*f[...,1]-16, 500*(f[...,0]-f[...,1]), 200*(f[...,1]-f[...,2])
def one(rgb):
    L, a, b = lab(rgb); C = np.hypot(a, b); H = (np.degrees(np.arctan2(b, a)) + 360) % 360
    r = {'p1': np.percentile(L, 1), 'p5': np.percentile(L, 5), 'p50': np.percentile(L, 50), 'p95': np.percentile(L, 95), 'p99': np.percentile(L, 99),
         'C': C.mean(), 'C90': np.percentile(C, 90), 'Lsd': L.std(),
         'rgbmin': np.percentile(rgb, 1, axis=0), 'rgbmax': np.percentile(rgb, 99, axis=0)}
    for nm, lo, hi in (('sh', 0, 30), ('md', 30, 65), ('hi', 65, 101)):
        m = (L >= lo) & (L < hi) & (C < 18)
        r[nm+'_a'] = a[m].mean() if m.sum() > 25 else np.nan; r[nm+'_b'] = b[m].mean() if m.sum() > 25 else np.nan
    for nm, lo, hi in (('red', 0, 50), ('skin', 40, 75), ('grn', 105, 170), ('blue', 235, 300)):
        m = (H >= lo) & (H < hi) & (C > 12)
        r[nm+'_C'] = C[m].mean() if m.sum() > 25 else np.nan; r[nm+'_H'] = H[m].mean() if m.sum() > 25 else np.nan
    return r
def statset(imgs):
    rows = [one(x) for x in imgs]
    out = {k: float(np.nanmedian([r[k] for r in rows])) for k in rows[0] if not k.startswith('rgb')}
    out['rgbmin'] = np.median([r['rgbmin'] for r in rows], 0); out['rgbmax'] = np.median([r['rgbmax'] for r in rows], 0)
    return out
