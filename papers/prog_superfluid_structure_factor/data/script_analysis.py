"""P6 WORK1: the owner's diffraction test S(k) <= sqrt(k/(2k*)) against published data.

Inputs (all under OUT/raw and the repo's papers/ar_bogoliubov_sk/data):
  parsed.json (Donnelly & Barenghi Table 14.1/14.3), helium_tier_l.json (Godfrin 2020 Table VI rows),
  fig4_digitized.json (Steinhauer 2002 Fig. 4, Tier X), sk_fig3a_digitized.json (Stamper-Kurn 1999 Fig. 3a, Tier X).
Outputs: data/*.csv, results.json.   Nothing here is invented: every number is read or computed.
"""
import csv
import json
import math
import os
import sys

import numpy as np
from scipy import constants as C
from scipy import integrate

WORK = '/home/callensxavier_gmail_com/programmes-2026-10-25/P6'
REPO_HE = '/home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/openai-math-discovery/papers/ar_bogoliubov_sk/data/helium_tier_l.json'
OUT = sys.argv[1]
os.makedirs(OUT + '/data', exist_ok=True)

hbar = C.hbar
h = C.h
u = C.physical_constants['atomic mass constant'][0]
meV = C.e * 1e-3

res = {}


def write_csv(path, rows, fields):
    with open(path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, '') for k in fields})


def bound(k, kstar):
    return np.sqrt(k / (2.0 * kstar))


def sbog(k, kstar):
    return k / np.sqrt(kstar ** 2 + k ** 2)


# =============================================================== He-4
m4 = 4.0026032 * u          # Godfrin et al. arXiv:2012.09067 Sec. III A (4.0026032 g/mol) -> amu
c_he, dc_he = 238.3, 0.1     # m/s, same paper Sec. II A
kstar_he = 2 * m4 * c_he / hbar * 1e-10          # Angstrom^-1
kstar_he_lo = 2 * m4 * (c_he - dc_he) / hbar * 1e-10
kstar_he_hi = 2 * m4 * (c_he + dc_he) / hbar * 1e-10
hb2_2m = hbar ** 2 / (2 * m4) / meV * 1e20      # meV Angstrom^2
res['he4'] = dict(m_amu=4.0026032, c_m_s=c_he, dc_m_s=dc_he, kstar_inv_A=kstar_he,
                  kstar_range_inv_A=[kstar_he_lo, kstar_he_hi], hbar2_over_2m_meV_A2=hb2_2m)

pj = json.load(open(WORK + '/raw/donnelly/parsed.json'))
t141 = pj['table14_1']
t143 = pj['table14_3']
res['he4']['parse_report'] = pj['report']
keyname = {1: 'Robkoff-Hallock X-ray (Donnelly ref 9, PRB 24, 159 (1981))',
           2: 'Svensson et al. neutron (Donnelly ref 10, PRB 21, 3638 (1980))',
           3: 'theory S(0) value adopted by Donnelly-Barenghi'}
data = [r for r in t141 if r['key'] in (1, 2) and r['Q'] > 0]
Q = np.array([r['Q'] for r in data])
S = np.array([r['S'] for r in data])
K = np.array([r['key'] for r in data])
sq = np.array([d['Q'] for d in t143])
ss = np.array([d['S'] for d in t143])
spl = np.interp(Q, sq, ss)
resid = S - spl
res['he4']['n_points'] = int(len(Q))
res['he4']['n_xray'] = int((K == 1).sum())
res['he4']['n_neutron'] = int((K == 2).sum())

# dataset discrepancy proxy (no published error bars in Table 14.1)
mx1 = float(S[K == 1].max()); mx2 = float(S[K == 2].max())
q1 = float(Q[K == 1][S[K == 1].argmax()]); q2 = float(Q[K == 2][S[K == 2].argmax()])
delta_ds = abs(mx1 - mx2)
pk = (Q >= 1.8) & (Q <= 2.4)
res['he4']['peak'] = dict(xray_max=mx1, xray_at=q1, neutron_max=mx2, neutron_at=q2, delta_ds=delta_ds,
                          mean_resid_xray_1p8_2p4=float(resid[pk & (K == 1)].mean()),
                          mean_resid_neutron_1p8_2p4=float(resid[pk & (K == 2)].mean()),
                          rms_resid_all=float(np.sqrt((resid ** 2).mean())),
                          rms_resid_xray=float(np.sqrt((resid[K == 1] ** 2).mean())),
                          rms_resid_neutron=float(np.sqrt((resid[K == 2] ** 2).mean())),
                          max_abs_resid=float(np.abs(resid).max()))

# Godfrin dispersion rows: Feynman upper bound S_up = eps0/eps
he_rows = json.load(open(REPO_HE))['rows']
gk = np.array([r['k'] for r in he_rows]); ge = np.array([r['eps'] for r in he_rows])
gerr = np.array([r['err'] for r in he_rows])


def s_up(k):
    eps = np.interp(k, gk, ge)
    err = np.interp(k, gk, gerr)
    eps0 = hb2_2m * k ** 2
    return eps0 / eps, eps0 / (eps - err)


rows_he = []
for q, s, key, sp, rr in zip(Q, S, K, spl, resid):
    b = float(bound(q, kstar_he))
    b_lo = float(bound(q, kstar_he_hi)); b_hi = float(bound(q, kstar_he_lo))   # bound is larger for smaller k*
    M = float(s - b)
    if M <= 0:
        verdict = 'CONSISTENT'
    elif M > delta_ds:
        verdict = 'REFUTED'
    else:
        verdict = 'UNDECIDED'
    sB = float(sbog(q, kstar_he))
    r = dict(Q_invA=q, S=s, key=int(key), source=keyname[int(key)], bound=b, margin=M, ratio=float(s / b),
             refuting_fraction=float(1 - b / s), S_bogoliubov_homog=sB, verdict=verdict,
             nominal_exceeds=bool(M > 0), spline_t143=float(sp), resid_vs_spline=float(rr),
             bound_c_minus=b_lo, bound_c_plus=b_hi)
    if 0.05 <= q <= 3.6:
        su, su_c = s_up(q)
        r['S_up_feynman_godfrin'] = float(su)
        r['S_up_conservative'] = float(su_c)
        r['exceeds_feynman_upper'] = bool(s > su_c)
    rows_he.append(r)
fields_he = ['Q_invA', 'S', 'key', 'source', 'bound', 'margin', 'ratio', 'refuting_fraction', 'S_bogoliubov_homog',
             'verdict', 'nominal_exceeds', 'spline_t143', 'resid_vs_spline', 'bound_c_minus', 'bound_c_plus',
             'S_up_feynman_godfrin', 'S_up_conservative', 'exceeds_feynman_upper']
write_csv(OUT + '/data/test_he4.csv', rows_he, fields_he)

# raw data csv with provenance
prov = []
for r in t141:
    prov.append(dict(Q_invA=r['Q'], S=r['S'], key=r['key'], source=keyname[r['key']],
                     table='Donnelly & Barenghi, J. Phys. Chem. Ref. Data 27, 1217 (1998), Table 14.1 (Ch. 14, web edition '
                           'pages.uoregon.edu/rjd/vapor15.htm); web edition (c) 2004 assumed, NOT checked, to reproduce the 1998 journal Table 14.1; journal page not pinned',
                     tier='L (secondary compilation of printed primary tables; no per-point uncertainty printed)',
                     temperature='not stated per point in the compilation'))
write_csv(OUT + '/data/he4_Sk_donnelly_table14_1.csv', prov,
          ['Q_invA', 'S', 'key', 'source', 'table', 'tier', 'temperature'])
write_csv(OUT + '/data/he4_Sk_spline_donnelly_table14_3.csv',
          [dict(Q_invA=d['Q'], S=d['S'], table='Donnelly & Barenghi Table 14.3 (spline fit, smoothed; cross-check only)',
                tier='L (fit, not data)') for d in t143], ['Q_invA', 'S', 'table', 'tier'])

# brackets
nom = [r for r in rows_he if r['nominal_exceeds']]
strict = [r for r in rows_he if r['verdict'] == 'REFUTED']


def brackets(rows, flag):
    # contiguous runs in Q of the given predicate
    out = []
    cur = None
    for r in sorted(rows_he, key=lambda x: x['Q_invA']):
        if flag(r):
            if cur is None:
                cur = [r['Q_invA'], r['Q_invA']]
            else:
                cur[1] = r['Q_invA']
        else:
            if cur is not None:
                out.append(cur)
                cur = None
    if cur is not None:
        out.append(cur)
    return out


res['he4']['verdict_counts'] = {v: sum(1 for r in rows_he if r['verdict'] == v)
                                for v in ('CONSISTENT', 'UNDECIDED', 'REFUTED')}
res['he4']['nominal_exceed_runs_Q'] = brackets(rows_he, lambda r: r['nominal_exceeds'])
res['he4']['strict_refuted_runs_Q'] = brackets(rows_he, lambda r: r['verdict'] == 'REFUTED')
srt = sorted(rows_he, key=lambda x: x['Q_invA'])
last_cons_before = [r for r in srt if r['Q_invA'] < 1.6 and not r['nominal_exceeds']]
first_nom = [r for r in srt if r['nominal_exceeds'] and r['Q_invA'] > 1.0][0]
res['he4']['onset'] = dict(first_nominal_exceed=dict(Q=first_nom['Q_invA'], S=first_nom['S'], bound=first_nom['bound'], key=first_nom['key']),
                           last_consistent_below=dict(Q=last_cons_before[-1]['Q_invA'], S=last_cons_before[-1]['S'],
                                                     bound=last_cons_before[-1]['bound'], key=last_cons_before[-1]['key']))
roton = [r for r in rows_he if 1.7 <= r['Q_invA'] <= 2.4]
res['he4']['roton_region_1p7_2p4'] = dict(n=len(roton), min_ratio=min(r['ratio'] for r in roton),
                                         max_ratio=max(r['ratio'] for r in roton),
                                         min_margin=min(r['margin'] for r in roton),
                                         all_refuted=all(r['verdict'] == 'REFUTED' for r in roton))
hi = [r for r in rows_he if r['Q_invA'] > 2 * kstar_he - 1.0 and r['Q_invA'] < 2 * kstar_he + 0.7]
res['he4']['near_2kstar'] = [dict(Q=r['Q_invA'], S=r['S'], bound=r['bound'], margin=r['margin'], verdict=r['verdict']) for r in hi]
res['he4']['lowk'] = [dict(Q=r['Q_invA'], S=r['S'], bound=r['bound'], S_B=r['S_bogoliubov_homog'],
                           S_up=r.get('S_up_feynman_godfrin'), exceeds_feynman=r.get('exceeds_feynman_upper'))
                      for r in srt if r['Q_invA'] < 1.0 and r['key'] == 1]
fe = [r for r in rows_he if 'exceeds_feynman_upper' in r]
res['he4']['feynman_check'] = dict(n=len(fe), n_exceed=sum(1 for r in fe if r['exceeds_feynman_upper']),
                                   exceed_Q=[r['Q_invA'] for r in fe if r['exceeds_feynman_upper']])

# Feynman-based second prong (Lean not_bogoliubov_of_structure_factor): for S above bound, eps measured != eps_B
sec = []
for r in srt:
    if r['nominal_exceeds'] and 0.05 <= r['Q_invA'] <= 3.6:
        k = r['Q_invA']
        eps = float(np.interp(k, gk, ge))
        # epsilon_B^2 = (hbar c k)^2 + (hbar^2 k^2/2m)^2 with hbar c in meV*A
        hc_meVA = hbar * c_he / meV * 1e10
        epsB = math.sqrt((hc_meVA * k) ** 2 + (hb2_2m * k * k) ** 2)
        sec.append(dict(Q=k, eps_measured_meV=eps, eps_bogoliubov_meV=epsB, ratio=eps / epsB))
res['he4']['second_prong_eps_vs_bogoliubov'] = sec[:3] + sec[-3:] if len(sec) > 6 else sec
res['he4']['hbar_c_meV_A'] = hbar * c_he / meV * 1e10

# ---- controls on the machinery (He-4 abscissae)
rng = np.random.default_rng(20261025)
Sb = sbog(Q, kstar_he)
pos_viol = int(((Sb - bound(Q, kstar_he)) > 0).sum())
noise_false = []
for sigma in (0.01, 0.02, 0.04):
    cnt = 0
    for _ in range(2000):
        s_n = Sb + rng.normal(0, sigma, size=Sb.shape)
        cnt += int(((s_n - bound(Q, kstar_he)) > delta_ds).sum() > 0)
    noise_false.append(dict(sigma=sigma, frac_trials_with_REFUTED=cnt / 2000))
free = np.ones_like(Q)
neg_ref = int(((free - bound(Q, kstar_he)) > delta_ds).sum())
neg_nom = int(((free - bound(Q, kstar_he)) > 0).sum())
neg_expected_nom = int((Q < 2 * kstar_he).sum())
planted = Sb * 1.5
pl_nom = int(((planted - bound(Q, kstar_he)) > 0).sum())
pl_ref = int(((planted - bound(Q, kstar_he)) > delta_ds).sum())
res['he4']['controls'] = dict(
    positive_bogoliubov_homog=dict(n=len(Q), violations_nominal=pos_viol, max_S_over_bound=float((Sb / bound(Q, kstar_he)).max())),
    positive_with_noise=noise_false,
    negative_free_S_equals_1=dict(n=len(Q), nominal_violations=neg_nom, strict_violations=neg_ref,
                                  expected_nominal=neg_expected_nom, delta_ds_used=delta_ds),
    planted_1p5_times_Bogoliubov=dict(nominal_violations=pl_nom, strict_violations=pl_ref),
    transcription=dict(second_parse_equal=pj['report']['equal_1'] and pj['report']['equal_3'],
                       table141_vs_spline=res['he4']['peak']['rms_resid_all']))

# =============================================================== BEC
def lda_S_and_bound(q, mu, mass, conv=None):
    """Trap-averaged Bogoliubov S and the trap-averaged bound.  q [1/m], mu [J], mass [kg].
    weight w(x) = (15/4) x sqrt(1-x), x = n/n0, local mu(x) = mu x, local c = sqrt(mu x/m)."""
    e0 = hbar ** 2 * q ** 2 / (2 * mass)
    w = lambda x: 15.0 / 4.0 * x * math.sqrt(1 - x)
    S_loc = lambda x: math.sqrt(e0 / (e0 + 2 * mu * x))
    ks_loc = lambda x: 2 * mass * math.sqrt(mu * x / mass) / hbar
    B_loc = lambda x: math.sqrt(q / (2 * ks_loc(x)))
    S_avg = integrate.quad(lambda x: w(x) * S_loc(x), 0, 1, epsabs=1e-12, epsrel=1e-12)[0]
    B_avg = integrate.quad(lambda x: w(x) * B_loc(x), 0, 1, epsabs=1e-12, epsrel=1e-12)[0]
    norm = integrate.quad(w, 0, 1)[0]
    return S_avg, B_avg, norm


def conv_bounds(q, mu, mass):
    c0 = math.sqrt(mu / mass)
    out = {}
    for name, fac in (('peak', 1.0), ('mean_density_c_large', math.sqrt(4.0 / 7.0)),
                      ('c_eff_phonon', math.sqrt(32.0 / (15.0 * math.pi)))):
        ks = 2 * mass * c0 * fac / hbar
        out[name] = dict(kstar_inv_um=ks * 1e-6, bound=math.sqrt(q / (2 * ks)))
    return out


# closed-form positive control: phonon-limit trap-average 15 pi/32 sqrt(e0/2mu)
mass_na = 22.98976928 * u
mass_rb = 86.909180527 * u
q0 = math.sqrt(4 * math.pi * mass_na * 1.38e3 / hbar)    # hbar q^2/2m = h * 1.38 kHz  (Stamper-Kurn Fig 3 caption)
res['bec'] = {}
chk = []
for ratio in (1e-6, 1e-4):
    mu_t = 1.0
    e0 = ratio * mu_t
    q_t = math.sqrt(2 * mass_na * e0) / hbar
    Sa, Ba, nm = lda_S_and_bound(q_t, mu_t, mass_na)
    chk.append(dict(e0_over_mu=ratio, S_lda=Sa, S_phonon_closed_form=15 * math.pi / 32 * math.sqrt(e0 / (2 * mu_t)), norm=nm))
res['bec']['lda_closed_form_check'] = chk

sk = json.load(open(WORK + '/raw/bec/sk_fig3a_digitized.json'))
# bottom axis mu/h: 0 at col 203, 5 kHz at col 625, 10 kHz at col 1047 (crop skfig3b_axis.png, same x offset)
mu_axis = lambda px: (px - 203.0) / 84.4
rows_sk = []
for r in sk:
    mu_kHz = mu_axis(r['px'])
    mu = h * mu_kHz * 1e3
    Sa, Ba, nm = lda_S_and_bound(q0, mu, mass_na)
    cb = conv_bounds(q0, mu, mass_na)
    sig = 0.5 * (r['S_hi'] - r['S_lo'])
    row = dict(source='Stamper-Kurn et al. PRL 83, 2876 (1999) = arXiv:cond-mat/9906035, Fig. 3a (p.3)', tier='X (read from figure)',
               peak_density_1e14_cm3=r['dens_1e14'], mu_over_h_kHz=mu_kHz, q_inv_um=q0 * 1e-6,
               S=r['S'], S_hi=r['S_hi'], S_lo=r['S_lo'], sigma=sig,
               S_lda_bogoliubov=Sa, bound_lda_average=Ba, ratio_model_over_bound=Sa / Ba,
               bound_peak=cb['peak']['bound'], bound_mean_density=cb['mean_density_c_large']['bound'],
               bound_c_eff=cb['c_eff_phonon']['bound'], kstar_peak_inv_um=cb['peak']['kstar_inv_um'],
               q_over_kstar_peak=q0 * 1e-6 / cb['peak']['kstar_inv_um'],
               z_vs_lda_bound=(r['S'] - Ba) / sig, z_vs_lda_model=(r['S'] - Sa) / sig,
               max_S_to_refute_at_1sigma=Ba + sig)
    rows_sk.append(row)
res['bec']['stamper_kurn'] = rows_sk
res['bec']['stamper_kurn_q_inv_um'] = q0 * 1e-6
res['bec']['stamper_kurn_cross_check_sound_speed_6p7kHz_mm_s'] = math.sqrt(h * 6.7e3 / mass_na) * 1e3
flds = ['source', 'tier', 'peak_density_1e14_cm3', 'mu_over_h_kHz', 'q_inv_um', 'S', 'S_hi', 'S_lo', 'sigma',
        'S_lda_bogoliubov', 'bound_lda_average', 'ratio_model_over_bound', 'bound_peak', 'bound_mean_density',
        'bound_c_eff', 'kstar_peak_inv_um', 'q_over_kstar_peak', 'z_vs_lda_bound', 'z_vs_lda_model',
        'max_S_to_refute_at_1sigma']
write_csv(OUT + '/data/bec_stamper_kurn_fig3a_tierX.csv', rows_sk, flds)

# model curve over mu for the Stamper-Kurn q (positive control + convention table)
curve = []
for mu_kHz in np.linspace(0.5, 12.0, 24):
    mu = h * mu_kHz * 1e3
    Sa, Ba, nm = lda_S_and_bound(q0, mu, mass_na)
    cb = conv_bounds(q0, mu, mass_na)
    curve.append(dict(mu_over_h_kHz=float(mu_kHz), S_lda=Sa, bound_lda_avg=Ba, bound_peak=cb['peak']['bound'],
                      bound_mean_density=cb['mean_density_c_large']['bound'], bound_c_eff=cb['c_eff_phonon']['bound'],
                      S_homog_peak=float(sbog(q0, 2 * mass_na * math.sqrt(mu / mass_na) / hbar))))
write_csv(OUT + '/data/bec_model_curve_stamper_kurn_q.csv', curve, list(curve[0].keys()))
res['bec']['convention_failures_of_trapped_model'] = {
    'bound_lda_average': sum(1 for c in curve if c['S_lda'] > c['bound_lda_avg'] + 1e-12),
    'bound_peak': sum(1 for c in curve if c['S_lda'] > c['bound_peak'] + 1e-12),
    'bound_mean_density': sum(1 for c in curve if c['S_lda'] > c['bound_mean_density'] + 1e-12),
    'bound_c_eff': sum(1 for c in curve if c['S_lda'] > c['bound_c_eff'] + 1e-12),
    'n_curve_points': len(curve)}

# solid-curve positive control: read the solid line of Fig. 3a at three columns away from markers
from PIL import Image
img = np.array(Image.open(WORK + '/raw/bec/skfig3a_crop.png').convert('L')) < 128
cols = [300, 380, 540, 620, 880, 1035]
ctrl = []
for c in cols:
    ys = np.where(img[212:630, c])[0] + 212
    if len(ys) == 0:
        continue
    # take the lowest contiguous run centre (the curve; error bars are thin and absent at these columns)
    yc = float(ys.mean())
    Sread = (633.0 - yc) / (633.0 - 206.0)
    dens = (c - 205.0) / (969.0 - 205.0) * 6.0
    mu_kHz = mu_axis(c)
    Sa, Ba, nm = lda_S_and_bound(q0, h * mu_kHz * 1e3, mass_na)
    ctrl.append(dict(col=c, dens_1e14=dens, mu_kHz=mu_kHz, S_curve_read=Sread, S_lda_mine=Sa, diff=Sread - Sa))
res['bec']['solid_curve_control'] = ctrl

# ---- Steinhauer Fig. 4 (Rb-87, mu/h = 1.91 kHz)
mu_st = h * 1.91e3
st = json.load(open(WORK + '/raw/bec/fig4_digitized.json'))
rows_st = []
for r in st:
    k = r['k']
    qm = k * 1e6
    Sa, Ba, nm = lda_S_and_bound(qm, mu_st, mass_rb)
    cb = conv_bounds(qm, mu_st, mass_rb)
    row = dict(source='Steinhauer, Ozeri, Katz, Davidson PRL 88, 120407 (2002) = arXiv:cond-mat/0111438, Fig. 4 (p.4)',
               tier='X (read from figure)',
               kind=('closed circle: measured S(k) x2.3 (rescaled to the LDA-Bogoliubov curve by the authors)' if r['kind'] == 'filled'
                     else 'open circle: eps0/omega(k) from the measured dispersion via Feynman relation (not a diffraction value)'),
               k_inv_um=k, S=r['S'], S_hi=r.get('S_hi', ''), S_lo=r.get('S_lo', ''),
               S_lda_bogoliubov=Sa, bound_lda_average=Ba, bound_peak=cb['peak']['bound'],
               bound_mean_density=cb['mean_density_c_large']['bound'], bound_c_eff=cb['c_eff_phonon']['bound'],
               kstar_peak_inv_um=cb['peak']['kstar_inv_um'], exceeds_lda_bound=bool(r['S'] > Ba))
    if r['kind'] == 'filled':
        row['S_raw_div_2p3'] = r['S'] / 2.3
        row['sigma'] = 0.5 * (r['S_hi'] - r['S_lo'])
        row['z_vs_lda_bound'] = (r['S'] - Ba) / row['sigma']
        row['z_raw_vs_lda_bound'] = (r['S'] / 2.3 - Ba) / (row['sigma'] / 2.3)
    rows_st.append(row)
res['bec']['steinhauer'] = rows_st
open_rows = [r for r in rows_st if r['kind'].startswith('open')]
res['bec']['steinhauer_open_vs_lda'] = dict(
    rms_diff=float(np.sqrt(np.mean([(r['S'] - r['S_lda_bogoliubov']) ** 2 for r in open_rows]))),
    max_abs_diff=float(max(abs(r['S'] - r['S_lda_bogoliubov']) for r in open_rows)),
    n=len(open_rows))
closed = [r for r in rows_st if r['kind'].startswith('closed')]
res['bec']['steinhauer_closed_summary'] = dict(
    n=len(closed), n_exceeds_bound_nominal=sum(1 for r in closed if r['exceeds_lda_bound']),
    n_exceeds_bound_1sigma=sum(1 for r in closed if r['z_vs_lda_bound'] > 1),
    n_raw_exceeds=sum(1 for r in closed if r['z_raw_vs_lda_bound'] > 0),
    max_z=max(r['z_vs_lda_bound'] for r in closed))
fl = ['source', 'tier', 'kind', 'k_inv_um', 'S', 'S_hi', 'S_lo', 'sigma', 'S_raw_div_2p3', 'S_lda_bogoliubov',
      'bound_lda_average', 'bound_peak', 'bound_mean_density', 'bound_c_eff', 'kstar_peak_inv_um', 'exceeds_lda_bound',
      'z_vs_lda_bound', 'z_raw_vs_lda_bound']
write_csv(OUT + '/data/bec_steinhauer_fig4_tierX.csv', rows_st, fl)

# BEC controls: positive = LDA-Bogoliubov model never exceeds LDA bound (any mu, any q); negative = S=1 exceeds LDA bound for q < ~2k*
posv = 0
negv = 0
ntot = 0
for mu_kHz in (0.5, 1.9, 3.1, 6.7, 9.3, 12.0):
    for qq in (0.2, 0.5, 1.0, 2.5, 4.0, 8.0, 15.0):
        Sa, Ba, nm = lda_S_and_bound(qq * 1e6, h * mu_kHz * 1e3, mass_rb)
        ntot += 1
        posv += int(Sa > Ba + 1e-12)
        negv += int(1.0 > Ba)
res['bec']['controls'] = dict(grid_points=ntot, lda_bogoliubov_violations=posv, free_S1_exceeds_bound_count=negv)

json.dump(res, open(OUT + '/results.json', 'w'), indent=1, default=float)
print(json.dumps(res['he4'], indent=1, default=float)[:6000])
print(json.dumps({k: v for k, v in res['bec'].items() if k not in ('stamper_kurn', 'steinhauer')}, indent=1, default=float))
for r in rows_sk:
    print({k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items() if k not in ('source', 'tier')})
