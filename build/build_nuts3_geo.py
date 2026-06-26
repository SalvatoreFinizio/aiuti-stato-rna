#!/usr/bin/env python3
import json, math, pathlib

SC = pathlib.Path("/private/tmp/claude-501/-Users-salvatorefinizio-Library-CloudStorage-OneDrive-LondonSchoolofEconomics-aiuti-stato/dbfdb7a0-5460-4911-9c70-f109d7b537f7/scratchpad")
ROOT = pathlib.Path("/Users/salvatorefinizio/Library/CloudStorage/OneDrive-LondonSchoolofEconomics/aiuti_stato")

geo = json.load(open(SC/"nuts3_03m.geojson"))
feats = [f for f in geo["features"] if f["properties"].get("CNTR_CODE") == "IT"]

def rings(geom):
    t, c = geom["type"], geom["coordinates"]
    if t == "Polygon": return c
    if t == "MultiPolygon": return [r for poly in c for r in poly]
    return []

# Douglas-Peucker for an OPEN polyline (distinct endpoints)
def dp(pts, tol):
    if len(pts) < 3: return pts
    a, b = pts[0], pts[-1]
    dx, dy = b[0]-a[0], b[1]-a[1]
    nrm = math.hypot(dx, dy) or 1e-12
    dmax, idx = 0.0, 0
    for i in range(1, len(pts)-1):
        px, py = pts[i][0]-a[0], pts[i][1]-a[1]
        d = abs(px*dy - py*dx)/nrm
        if d > dmax: dmax, idx = d, i
    if dmax > tol:
        return dp(pts[:idx+1], tol)[:-1] + dp(pts[idx:], tol)
    return [a, b]

# ring-aware DP: break the closed ring at the vertex farthest from pts[0]
def dp_ring(ring, tol):
    pts = ring[:-1] if ring[0] == ring[-1] else ring[:]
    if len(pts) < 4: return ring
    a = pts[0]
    far = max(range(len(pts)), key=lambda i: (pts[i][0]-a[0])**2 + (pts[i][1]-a[1])**2)
    s1 = dp(pts[:far+1], tol)
    s2 = dp(pts[far:] + [pts[0]], tol)
    return s1[:-1] + s2  # closed (ends at pts[0])

TOL = 0.014   # final ~1.4km, sub-pixel
MIN_RING_PTS = 4

# pass 1: global bbox
minlon=minlat=1e9; maxlon=maxlat=-1e9
for f in feats:
    for r in rings(f["geometry"]):
        for lon,lat in r:
            minlon=min(minlon,lon); maxlon=max(maxlon,lon)
            minlat=min(minlat,lat); maxlat=max(maxlat,lat)
midlat=(minlat+maxlat)/2; coslat=math.cos(math.radians(midlat))
W=560.0; k=W/((maxlon-minlon)*coslat); H=(maxlat-minlat)*k

def proj(lon,lat): return round((lon-minlon)*coslat*k,1), round((maxlat-lat)*k,1)

paths={}; nb=na=0
for f in feats:
    code=f["properties"]["NUTS_ID"]; d=[]
    for r in rings(f["geometry"]):
        nb+=len(r); rs=dp_ring(r,TOL); na+=len(rs)
        if len(rs)<MIN_RING_PTS: continue
        seg=[("M" if j==0 else "L")+f"{x},{y}" for j,(lon,lat) in enumerate(rs) for x,y in [proj(lon,lat)]]
        d.append(" ".join(seg)+" Z")
    paths[code]=" ".join(d)

out={"w":round(W),"h":round(H),"paths":paths}
(SC/"nuts3_paths.json").write_text(json.dumps(out,separators=(",",":")))
sz=(SC/"nuts3_paths.json").stat().st_size
empties=[c for c,p in paths.items() if not p]
print(f"provinces: {len(paths)}  points {nb} -> {na} ({na/nb*100:.0f}%)  file: {sz//1024} KB")
print(f"viewBox: {round(W)} x {round(H)}   empty: {empties}")
print("ITC4C len:", len(paths['ITC4C']), " ITI43 len:", len(paths['ITI43']))
