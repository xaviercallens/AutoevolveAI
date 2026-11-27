/* Auditor's independent enumeration for DH-Psi2 (written from eq. (LI)/(trace), not from producer code).
 * Reduction: diagonal sign gauge (F0,F1,F2) -> (D0 F0 D1, D1 F1 D2, D2 F2 D0), exact invariance of every
 * term sum_{ijk} F0[i][j] F1[j][k] F2[k][i] w(i,j,k). Canonical reps: F0 row0 = col0 = +1 (2^9), F1 row0 = +1 (2^12).
 * No l1 reduction: literal max over all 2^16 F2 by Gray code.
 * Terms (units 1/64, N=2, n=4): T: w=1; level 0: w=h(i)h(j)h(k), h(c)=+1 if c in left half [0,1/2) i.e. c<2;
 * level 1 (prefactor 2): intervals P(c)=c/2, Haar g(c)=+1 if c is the left cell of its half-interval (c%2==0);
 * admissible triples (p,q,r) with p^q^r=0, w = [P(i)=p][P(j)=q][P(k)=r] g(i)g(j)g(k).
 * Usage: gauge_enum HAAR(0/1) [slice F0code_lo F0code_hi]
 *   slice mode: producer's encoding for F0 (cell 0 = +1, bit b -> cell b+1 is -1), all F1 with F1[0][0]=+1, all 2^16 F2.
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#define NW 3
static int W[6][4][4][4], PF[6];
static int wT_list[NW] = {1, 3, 4};
static void build(int haar){
  for(int i=0;i<4;i++)for(int j=0;j<4;j++)for(int k=0;k<4;k++){
    int c[3]={i,j,k}; int hl0=1, g1=1;
    for(int v=0;v<3;v++){ if(haar){ hl0*= (c[v]<2)?1:-1; g1*= (c[v]%2==0)?1:-1; } }
    W[0][i][j][k]=1; W[1][i][j][k]=hl0;
    int t=2;
    for(int p=0;p<2;p++)for(int q=0;q<2;q++){ int r=p^q;
      W[t][i][j][k] = (i/2==p && j/2==q && k/2==r) ? g1 : 0; t++; }
  }
  PF[0]=0; PF[1]=1; for(int t=2;t<6;t++)PF[t]=2;
}
static uint64_t hist[NW][2048]; static int gmax[NW]; static uint64_t nmaxF2[NW]; static uint64_t npairmax[NW]; static uint64_t over192[NW];
static int argF[NW][3][4][4];
static void do_pair(int F0[4][4], int F1[4][4]){
  int c[6][16];
  for(int t=0;t<6;t++)for(int k=0;k<4;k++)for(int i=0;i<4;i++){ int s=0;
    for(int j=0;j<4;j++) s+=F0[i][j]*F1[j][k]*W[t][i][j][k]; c[t][k*4+i]=s; }
  int a[6]; for(int t=0;t<6;t++){a[t]=0; for(int x=0;x<16;x++)a[t]+=c[t][x];}
  int sg[16]; for(int x=0;x<16;x++)sg[x]=1;
  int best[NW]; int bestg[NW]; uint64_t cnt[NW];
  for(int m=0;m<NW;m++){best[m]=-1;cnt[m]=0;bestg[m]=0;}
  unsigned gray=0;
  for(unsigned step=0; step<65536u; step++){
    if(step){ int x=__builtin_ctz(step); for(int t=0;t<6;t++) a[t]-=2*sg[x]*c[t][x]; sg[x]=-sg[x]; gray^=1u<<x; }
    int base=abs(a[1]); for(int t=2;t<6;t++) base+=2*abs(a[t]);
    int at=abs(a[0]);
    for(int m=0;m<NW;m++){ int S=base+wT_list[m]*at;
      if(S>best[m]){best[m]=S;cnt[m]=1;bestg[m]=gray;} else if(S==best[m])cnt[m]++; }
  }
  for(int m=0;m<NW;m++){ hist[m][best[m]]++;
    if(best[m]>192) over192[m]++;
    if(best[m]>gmax[m]){gmax[m]=best[m]; nmaxF2[m]=0; npairmax[m]=0;
      for(int i=0;i<4;i++)for(int j=0;j<4;j++){argF[m][0][i][j]=F0[i][j];argF[m][1][i][j]=F1[i][j];}
      for(int x=0;x<16;x++) argF[m][2][x/4][x%4] = ((bestg[m]>>x)&1)?-1:1; }
    if(best[m]==gmax[m]){ nmaxF2[m]+=cnt[m]; npairmax[m]++; }
  }
}
static int fullS(int F[3][4][4], int wT){ int tot=0;
  for(int t=0;t<6;t++){int s=0; for(int i=0;i<4;i++)for(int j=0;j<4;j++)for(int k=0;k<4;k++) s+=F[0][i][j]*F[1][j][k]*F[2][k][i]*W[t][i][j][k];
    tot += (t==0?wT:PF[t])*abs(s);} return tot; }
int main(int argc,char**argv){
  if(argc<2){fprintf(stderr,"usage\n");return 2;}
  int haar=atoi(argv[1]); build(haar);
  int slice = argc>2;
  uint64_t npairs=0;
  int F0[4][4],F1[4][4];
  for(int m=0;m<NW;m++)gmax[m]=-1;
  if(!slice){
    unsigned lo0 = 0, hi0 = 512;
    for(unsigned m0=lo0;m0<hi0;m0++){
      int b=0; for(int i=0;i<4;i++)for(int j=0;j<4;j++){ if(i==0||j==0)F0[i][j]=1; else {F0[i][j]=((m0>>b)&1)?-1:1; b++;} }
      for(unsigned m1=0;m1<4096u;m1++){
        int bb=0; for(int i=0;i<4;i++)for(int j=0;j<4;j++){ if(i==0)F1[i][j]=1; else {F1[i][j]=((m1>>bb)&1)?-1:1; bb++;} }
        do_pair(F0,F1); npairs++; }
    }
  } else {
    unsigned lo=(unsigned)atoi(argv[3]), hi=(unsigned)atoi(argv[4]);
    for(unsigned a=lo;a<hi;a++){
      for(int cc=0;cc<16;cc++) F0[cc/4][cc%4] = (cc && ((a>>(cc-1))&1))?-1:1;
      for(unsigned b=0;b<32768u;b++){
        for(int cc=0;cc<16;cc++) F1[cc/4][cc%4] = (cc && ((b>>(cc-1))&1))?-1:1;
        do_pair(F0,F1); npairs++; } }
  }
  printf("{\"haar\": %d, \"slice\": %d, \"pairs\": %llu, \"modes\": {", haar, slice, (unsigned long long)npairs);
  for(int m=0;m<NW;m++){
    printf("%s\"wT=%d\": {\"max_S\": %d, \"argmax_recheck\": %d, \"pairs_gt192\": %llu, \"pairs_at_max\": %llu, \"F2_maximisers_summed_over_max_pairs\": %llu, \"argmax\": [",
      m?", ":"", wT_list[m], gmax[m], fullS(argF[m],wT_list[m]), (unsigned long long)over192[m], (unsigned long long)npairmax[m], (unsigned long long)nmaxF2[m]);
    for(int v=0;v<3;v++){printf("%s[",v?",":""); for(int i=0;i<4;i++){printf("%s[",i?",":""); for(int j=0;j<4;j++)printf("%s%d",j?",":"",argF[m][v][i][j]); printf("]");} printf("]");}
    printf("], \"hist\": {"); int f=1; for(int h=0;h<2048;h++) if(hist[m][h]){printf("%s\"%d\": %llu",f?"":", ",h,(unsigned long long)hist[m][h]); f=0;}
    printf("}}");
  }
  printf("}}\n"); return 0;
}
