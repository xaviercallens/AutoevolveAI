# Independent recomputation of K3 part (c) with Sage RealBallField (arb), not producer code.
R = RealBallField(400)
Q = QQ
a0 = Q(2173)/10000; A = [Q(2240)/10000, Q(2824)/10000, Q(2763)/10000]; T = [Q(3944)/10, Q(3654)/100, Q(4304)/1000]
assert a0 + sum(A) == 1
def segs_from_nodes(nodes):
    out=[]
    for (p,mp),(q,mq) in zip(nodes[:-1],nodes[1:]):
        b=(mq-mp)/(q-p); a=mp-b*p; out.append((p,q,a,b))
    return out
def segs_from_steps(jumps):
    out=[]; lvl=Q(0)
    for k,(z,c) in enumerate(jumps):
        lvl+=c
        nxt = jumps[k+1][0] if k+1<len(jumps) else None
        if nxt is not None: out.append((z,nxt,lvl,Q(0)))
        else: assert lvl==0
    return out
def u(segs, t, a0=a0, A=A, T=T):
    t=Q(t); tot=R(0)
    for (p,q,a,b) in segs:
        if p>=t: continue
        q=min(q,t)
        tot += R(a0*(a*(q-p)+b*(q**2-p**2)/2))
        for ai,ti in zip(A,T):
            F = lambda z: (R(ti)*(R(a)+R(b)*R(z)) - R(b)*R(ti)**2)*(R(z-t)/R(ti)).exp()
            tot += R(ai)*(F(q)-F(p))
    return tot
def check(name, segs, times):
    us=[u(segs,s) for s in times]
    d=[us[1]-us[0], us[1]-us[2], us[3]-us[2], us[3]-us[4]]
    ok=all(x>0 for x in d)
    print(name, times); print('  u =', [x.mid().n(digits=20) for x in us])
    print('  rad max', max(x.rad() for x in us).n(digits=3))
    print('  diffs lower bounds', [(x.lower()).n(digits=12) for x in d], 'ALL>0:', ok)
I1=[(Q(a),Q(b)) for a,b in [(0,0),(10,1),(22,Q(1)/10),(300,Q(1)/10),(310,0)]]
I2=[(Q(a),Q(b)) for a,b in [(0,0),(10,1),(22,Q(1)/10),(300,Q(1)/20),(310,0)]]
S1=segs_from_steps([(Q(0),Q(1)),(Q(5),Q(-9)/10),(Q(200),Q(-1)/10)])
check('I1', segs_from_nodes(I1), [10,21,32,303,320])
check('I2', segs_from_nodes(I2), [10,21,40,305,330])
check('S1', S1, [1,5,11,200,500])
def mfun(segs,z):
    for (p,q,a,b) in segs:
        if p<=z<q: return float(a+b*z)
    return 0.0
def h(x): return float(a0)+sum(float(ai)*exp(-x/float(ti)) for ai,ti in zip(A,T))
for name,segs,ts in [('I1',segs_from_nodes(I1),[21,32,303]),('S1',S1,[5,11,200])]:
    for t in ts:
        brk=sorted(set([0,t]+[float(p) for p,_,_,_ in segs if p<t]+[float(q) for _,q,_,_ in segs if q<t]))
        val=sum(numerical_integral(lambda z: mfun(segs,z)*h(t-z), brk[k],brk[k+1])[0] for k in range(len(brk)-1))
        print('quad',name,t,val, float(u(segs,t).mid()))
