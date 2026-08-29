import csv, json, re, sys

def load(p):
    rows=list(csv.reader(open(p,encoding='utf-8')))
    w=max(len(r) for r in rows)
    return [r+['']*(w-len(r)) for r in rows], w

def cell(g,r,c):
    if 0<=r<len(g) and 0<=c<len(g[0]): return g[r][c].strip()
    return ''

def parse_tab(path):
    g,w=load(path)
    builds=[]
    for r in range(len(g)):
        for c in range(w):
            if re.fullmatch(r'Level\s*1\s*:', cell(g,r,c), re.I):
                b=parse_block(g,r,c,w)
                if b: builds.append(b)
    return builds

def parse_block(g,r0,c0,w):
    title=cell(g,r0-3,c0); desc=cell(g,r0-2,c0)
    tiers=[cell(g,r0-1,c0), cell(g,r0-1,c0+3), cell(g,r0-1,c0+6)]
    levels={}
    for seg,(coff,lo,hi) in enumerate([(0,1,15),(3,16,35),(6,36,55)]):
        for rr in range(r0, r0+20):
            lab=cell(g,rr,c0+coff)
            m=re.fullmatch(r'Level\s*(\d+)\s*:', lab, re.I)
            if not m: continue
            lvl=int(m.group(1))
            if not (lo<=lvl<=hi): continue
            picks=[x for x in (cell(g,rr,c0+coff+1), cell(g,rr,c0+coff+2)) if x]
            levels[lvl]=picks
    if not levels: return None
    skills=[]; gear=[]
    for rr in range(r0-3, r0+20):
        lab=cell(g,rr,c0+10)
        if lab=='Skill Options':
            v=cell(g,rr+1,c0+10)
            if v: skills.append(v)
        elif lab and lab not in ('Gear to consider','') and cell(g,rr,c0+11):
            gear.append([lab, cell(g,rr,c0+11)])
    return dict(title=title, desc=desc, tiers=tiers, levels=levels, skills=skills, gear=gear)

if __name__=='__main__':
    for p in sys.argv[1:]:
        bs=parse_tab(p)
        print('==',p,len(bs),'builds')
        for b in bs[:100]:
            print('  ', b['title'][:60],'|',b['tiers'],'| lvls',len(b['levels']),'| gear',len(b['gear']))
