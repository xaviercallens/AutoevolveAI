import mpmath as mp
mp.mp.dps = 60
h = lambda x: mp.mpf('0.5') * mp.e**(-x / 100) + mp.mpf('0.5') * mp.e**(-x / 5)
d = 5
vals = [h(mp.mpf(k) / 10 + d) / h(mp.mpf(k) / 10) for k in range(0, 5001)]
print('a0=0 two-exp rho strictly increasing on [0,500] grid (60 digits):', all(b > a for a, b in zip(vals, vals[1:])),
      'rho(0)=', mp.nstr(vals[0], 10), 'rho(500)=', mp.nstr(vals[-1], 15), 'L=', mp.nstr(mp.e**(-mp.mpf(d) / 100), 15))
