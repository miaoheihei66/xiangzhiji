import json, os, sys, urllib.request, urllib.parse, re, concurrent.futures as cf
out = sys.argv[1]
proxy = urllib.request.ProxyHandler({'https': 'http://127.0.0.1:7897', 'http': 'http://127.0.0.1:7897'})
op = urllib.request.build_opener(proxy); op.addheaders = [('User-Agent', 'Mozilla/5.0 film-study')]
groups = {
  'polaroid': ['polaroid600', 'polaroidoriginals', 'polaroidsx70', 'itypefilm', 'polaroidnow', 'impossibleproject', 'polaroidfilm', 'polaroid600film', 'sx70film', 'polaroidonestep'],
  'instax':   ['instaxmini', 'instaxwide', 'instaxsquare', 'instaxfilm', 'fujiinstax', 'instaxminifilm', 'instaxmini90', 'instaxwide300'],
  'phone':    ['shotoniphone', 'iphonephotography', 'iphone15pro', 'iphone14pro', 'iphone13pro'],
}
jobs = []
for g, tags in groups.items():
    os.makedirs(os.path.join(out, g), exist_ok=True)
    seen = set()
    for t in tags:
        u = 'https://www.flickr.com/services/feeds/photos_public.gne?format=json&nojsoncallback=1&tags=' + urllib.parse.quote(t)
        try:
            raw = op.open(u, timeout=30).read().decode('utf-8', 'replace')
            raw = raw.replace("\'", "'")
            items = json.loads(raw)['items']
        except Exception as e:
            print('feed fail', t, e); continue
        for it in items:
            m = it['media']['m']
            if m in seen: continue
            seen.add(m); jobs.append((g, m.replace('_m.jpg', '_z.jpg'), it.get('tags', '')))
print('jobs', len(jobs))
def dl(j):
    g, url, tags = j
    fn = os.path.join(out, g, url.rsplit('/', 1)[1])
    try:
        with open(fn, 'wb') as f: f.write(op.open(url, timeout=40).read())
        return 1
    except Exception as e:
        return 0
with cf.ThreadPoolExecutor(8) as ex: n = sum(ex.map(dl, jobs))
print('downloaded', n)
for g in groups: print(g, len(os.listdir(os.path.join(out, g))))
