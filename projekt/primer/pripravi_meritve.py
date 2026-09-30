"""
Priprava sintetičnih meritev (meritve_trenje.csv in meritve_padec.csv).

Realnih meritev nimam, zato ju generiram iz modela in dodam normalno
porazdeljen šum. Seme generatorja je fiksno, da so podatki ponovljivi.

* meritve_trenje.csv: sila vleka F pri sedmih obremenitvah N
  (Coulombovo trenje z mu = 0,32, šum 4 N),
* meritve_padec.csv: kot lestve med padcem brez trenja iz 75 stopinj,
  30 sličic na sekundo, šum 0,5 stopinje, do odlepitve od stene.
"""

import numpy as np
from scipy.integrate import solve_ivp

import lestev as le

# podatki (enaki kot v poročilu)
L = 4.0                     # dolžina lestve [m]
m = 12.0                    # masa lestve [kg]
g = 9.81                    # težni pospešek [m/s^2]
mu_pravi = 0.32             # koeficient trenja za generiranje [-]
theta0 = np.radians(75.0)   # začetni kot padca [rad]
frekvenca = 30.0            # sličic na sekundo [1/s]

rng = np.random.default_rng(0)

# meritve trenja: normalna sila in sila vleka
N_mer = np.arange(100.0, 701.0, 100.0)
F_mer = mu_pravi * N_mer + rng.normal(0.0, 4.0, N_mer.size)
np.savetxt("meritve_trenje.csv",
           np.column_stack([N_mer, F_mer]),
           delimiter=",",
           header="N [N],F [N]",
           comments="",
           fmt="%.1f")
print(f"Zapisanih {N_mer.size} točk v meritve_trenje.csv")


# meritve padca: kot iz videa do odlepitve od stene
def odlepitev(t, y, L, g):
    return le.sila_stene(y[0], y[1], m, L, g)


odlepitev.terminal = True
odlepitev.direction = -1

resitev = solve_ivp(le.desna_stran_de,
                    (0.0, 5.0),
                    [theta0, 0.0],
                    args=(L, g),
                    events=odlepitev,
                    dense_output=True,
                    rtol=1e-10,
                    atol=1e-12)
t_od = resitev.t_events[0][0]
t_mer = np.arange(0.0, t_od, 1.0 / frekvenca)
theta_mer = np.degrees(resitev.sol(t_mer)[0])
theta_mer = theta_mer + rng.normal(0.0, 0.5, t_mer.size)
np.savetxt("meritve_padec.csv",
           np.column_stack([t_mer, theta_mer]),
           delimiter=",",
           header="t [s],theta [deg]",
           comments="",
           fmt="%.4f,%.2f")
print(f"Zapisanih {t_mer.size} točk v meritve_padec.csv")
