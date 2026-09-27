default(parisize,64000000);
Vs=[[0,-1,1,-10,-20],[0,0,1,-1,0],[0,1,1,-2,0],[0,0,1,-7,6]];
labels=["11a1(r0)","37a1(r1)","389a1(r2)","5077a1(r3)"];
for(i=1,4, E=ellinit(Vs[i]); ar=ellanalyticrank(E); print(labels[i], " analytic_rank=", ar[1], "  L^(r)(1)=", precision(ar[2],10)));
quit
