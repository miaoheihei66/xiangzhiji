# Fit the colour part of the film shader so that phone photos run through it
# match the measured statistics of real instant prints.
import sys, glob, os, json
import numpy as np
from PIL import Image
from scipy.optimize import minimize
sys.path.insert(0, os.path.dirname(__file__))
from measure_lib import lab, statset
D = sys.argv[1]; film = sys.argv[2]
target = json.load(open(os.path.join(D, '..', 'stats.json')))[film]

def load(g):
    out = []
    for f in sorted(glob.glob(os.path.join(D, g, '*.jpg'))):
        try: im = Image.open(f).convert('RGB')
        except Exception: continue
        w, h = im.size; cw, ch = int(w*.55), int(h*.55)
        im = im.crop(((w-cw)//2, (h-ch)//2, (w+cw)//2, (h+ch)//2)).resize((int(os.environ.get("RES","96")),)*2)
        out.append(np.asarray(im, dtype=np.float64).reshape(-1, 3)/255)
    return out
phones = load('phone')

def s2l(c): return np.where(c <= 0.04045, c/12.92, ((np.clip(c,0,None)+0.055)/1.055)**2.4)
def l2s(c): c = np.clip(c, 0, 1); return np.where(c <= 0.0031308, c*12.92, 1.055*c**(1/2.4)-0.055)
M1 = np.array([[0.4122214708,0.5363325363,0.0514459929],[0.2119034982,0.6806995451,0.1073969566],[0.0883024619,0.2817188376,0.6299787005]])
M2 = np.array([[0.2104542553,0.7936177850,-0.0040720468],[1.9779984951,-2.4285922050,0.4505937099],[0.0259040371,0.7827717662,-0.8086757660]])
I1, I2 = np.linalg.inv(M1), np.linalg.inv(M2)
def bump(h, c, wdt):  # smooth weight around hue c (radians), half width wdt
    d = np.angle(np.exp(1j*(h-c))); x = np.clip(1-np.abs(d)/wdt, 0, 1); return x*x*(3-2*x)
NAMES = ['expo','warm','tint','sat','hR','hG','hB','sR','sG','sB','k','mA','mB','bR','bG','bB','wR','wG','wB']
def apply(c, p):
    P = dict(zip(NAMES, p))
    c = c*P['expo']; c = c*np.array([1+P['warm'], 1+P['tint'], 1-P['warm']])
    lab_ = np.cbrt(np.clip(s2l(np.clip(c,0,1)) @ M1.T, 0, None)) @ M2.T
    L, a, b = lab_[:,0], lab_[:,1], lab_[:,2]
    C = np.hypot(a, b); h = np.arctan2(b, a)
    wr, wg, wb = bump(h, np.radians(30), np.radians(55)), bump(h, np.radians(140), np.radians(60)), bump(h, np.radians(262), np.radians(55))
    h = h + np.radians(P['hR'])*wr + np.radians(P['hG'])*wg + np.radians(P['hB'])*wb
    C = C*P['sat']*(1 + P['sR']*wr + P['sG']*wg + P['sB']*wb)
    mid = np.clip(1 - np.abs(L-0.6)/0.35, 0, 1)
    a = C*np.cos(h) + P['mA']*0.01*mid; b = C*np.sin(h) + P['mB']*0.01*mid
    lin = (np.stack([L, a, b], 1) @ I2.T)**3 @ I1.T
    c = l2s(lin)
    s = c*c*(3-2*c); k = P['k']
    c = c + (s-c)*min(k,1); 
    if k > 1: s2 = c*c*(3-2*c); c = c + (s2-c)*(k-1)
    blk = np.array([P['bR'],P['bG'],P['bB']]); wht = np.array([P['wR'],P['wG'],P['wB']])
    return blk + c*(wht-blk)

W = {'p1':1,'p5':1,'p50':1,'p95':1,'p99':1,'C':2,'C90':1,'Lsd':1.5,'sh_a':1.5,'sh_b':1.5,'md_a':1.5,'md_b':1.5,'hi_a':1.5,'hi_b':1.5,
     'red_H':.25,'red_C':.6,'skin_H':.4,'skin_C':.6,'grn_H':.25,'grn_C':.6,'blue_H':.25,'blue_C':.6}
def loss(p):
    st = statset([apply(c, p) for c in phones])
    e = sum(w*((st[k]-target[k]))**2 for k, w in W.items() if np.isfinite(st[k]))
    e += 300*sum((np.array(st['rgbmin'])-np.array(target['rgbmin']))**2) + 300*sum((np.array(st['rgbmax'])-np.array(target['rgbmax']))**2)
    P = dict(zip(NAMES, p))
    e += 50*sum(max(0, abs(P[k])-25)**2 for k in ('hR','hG','hB')) + 200*max(0, .3-P['k'])**2
    return e
x0 = np.array([float(v) for v in os.environ.get('X0','1.0,0,0,0.8,0,0,0,0,0,0,0.8,0,0,0.1,0.1,0.1,0.88,0.88,0.88').split(',')])
r = minimize(loss, x0, method='Powell', options={'maxiter': int(os.environ.get('PIT','6000')), 'xtol': 1e-3, 'ftol': 1e-4})
r = minimize(loss, r.x, method='Nelder-Mead', options={'maxiter': int(os.environ.get('NIT','3000')), 'xatol': 1e-4, 'fatol': 1e-4})
P = dict(zip(NAMES, [round(float(v), 4) for v in r.x]))
st = statset([apply(c, r.x) for c in phones])
print(film, 'loss', round(float(r.fun), 2)); print(json.dumps(P))
for k in list(W) + ['rgbmin', 'rgbmax']:
    print('%-7s fit %-22s target %s' % (k, np.round(st[k], 2), np.round(target[k], 2)))
json.dump(P, open(os.path.join(D, '..', 'fit_%s.json' % film), 'w'))
