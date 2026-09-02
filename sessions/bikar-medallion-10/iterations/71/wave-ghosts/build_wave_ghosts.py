#!/usr/bin/env python3
"""Build per-wave ghost images: full pattern in faint grey (#DBDBDB) with white gaps,
only the active wave's faces colored at their real fill. Matches reference wave-N.png style.

Wave->face mapping: each wave's reference shapes (wave-plan.json shapes[].{r_frac,theta_deg})
are matched to render faces by normalized polar position (greedy nearest, radius-weighted).
Face-classes span multiple radial bands, so per-wave subsetting is by position, not class."""
import json,re,math,sys
B="/Users/omareid/Library/CloudStorage/Dropbox/Data/sacred-patterns/bikar-medallion-10"
GHOST="#DBDBDB"; EDGE="#FFFFFF"; EDGE_W="1.4"

wp=json.load(open(f"{B}/input/reference-analysis/wave-plan/wave-plan.json"))
svg=open(f"{B}/iterations/71/render.svg").read()

def centroid(d):
    nums=re.findall(r'-?\d+\.?\d*',d);xs=list(map(float,nums[0::2]));ys=list(map(float,nums[1::2]))
    n=min(len(xs),len(ys));return sum(xs[:n])/n,sum(ys[:n])/n

faces={}
for m in re.finditer(r'<path[^>]*?>',svg):
    t=m.group(0);fi=re.search(r'data-face-index="(\d+)"',t);d=re.search(r'\sd="([^"]*)"',t)
    if not(fi and d):continue
    x,y=centroid(d.group(1))
    faces[int(fi.group(1))]={"r":math.hypot(x,y),"th":math.degrees(math.atan2(-y,x))%360}
Rrender=max(f["r"] for f in faces.values())

def match_wave(wi,used):
    keep=[]
    for s in wp["waves"][wi]["shapes"]:
        rf=s["r_frac"];th=s["theta_deg"]%360;best=None;bd=1e9
        for fi,f in faces.items():
            if fi in used:continue
            dr=abs(f["r"]/Rrender-rf);dth=abs((f["th"]-th+180)%360-180)
            cost=dr*3+dth/180.0
            if cost<bd:bd=cost;best=fi
        if best is not None:keep.append(best);used.add(best)
    return keep

# Cumulative-used across waves prevents double-assignment, but each wave image is INDEPENDENT
# (ghost all, color just this wave). Build per-wave keep-sets with a fresh used-set per call
# so a wave isn't starved by an earlier wave's matches -> use global assignment once.
used=set(); wave_keep={}
for wi in range(len(wp["waves"])):
    wave_keep[wi+1]=set(match_wave(wi,used))

def ghost_svg(active_keep):
    def proc(m):
        t=m.group(0)
        if 'data-face-index' in t:
            fi=int(re.search(r'data-face-index="(\d+)"',t).group(1))
            if fi in active_keep:return t
            return re.sub(r'fill="#[0-9A-Fa-f]{6}"',f'fill="{GHOST}"',t,1)
        if 'data-edge-index' in t:
            t=re.sub(r'stroke="#[0-9A-Fa-f]{6}"',f'stroke="{EDGE}"',t,1)
            return re.sub(r'stroke-width="[\d.]+"',f'stroke-width="{EDGE_W}"',t,1)
        return t
    return re.sub(r'<path[^>]*?>',proc,svg)

import cairosvg
OUT=f"{B}/iterations/71/wave-ghosts"
for wn in range(1,len(wp["waves"])+1):
    out=ghost_svg(wave_keep[wn])
    open(f"{OUT}/wave-{wn}.svg","w").write(out)
    cairosvg.svg2png(url=f"{OUT}/wave-{wn}.svg",write_to=f"{OUT}/wave-{wn}.png",
                     output_width=512,output_height=512,background_color="white")
    print(f"wave-{wn}: {len(wave_keep[wn])} faces colored")
print("DONE")
