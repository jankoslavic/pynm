"""Skica problema (skica.png): lestev ob gladki steni z osebo in silami."""

import numpy as np
import matplotlib.pyplot as plt

L = 4.0                       # dolžina lestve [m]
theta = np.radians(65.0)      # kot lestve za skico [rad]
x_osebe = 2.6                 # lega osebe [m]

# točke A (tla), B (stena), težišče G in oseba P
A = np.array([L * np.cos(theta), 0.0])
B = np.array([0.0, L * np.sin(theta)])
smer = (B - A) / L
G = A + smer * L / 2
P = A + smer * x_osebe

fig, ax = plt.subplots(figsize=(6.4, 5.2))
ax.set_aspect("equal")
ax.axis("off")

# stena in tla s šrafuro
ax.plot([0, 0], [-0.2, 4.4], "k", lw=2)
ax.plot([-0.2, 3.2], [0, 0], "k", lw=2)
for y in np.arange(0.0, 4.4, 0.25):
    ax.plot([-0.25, 0], [y - 0.25, y], "k", lw=0.6)
for x in np.arange(0.0, 3.2, 0.25):
    ax.plot([x - 0.25, x], [-0.25, 0], "k", lw=0.6)

# lestev (dva kraka in prečke)
odmik = np.array([-smer[1], smer[0]]) * 0.09
for znak in (-1, 1):
    zac = A + znak * odmik
    kon = B + znak * odmik
    ax.plot([zac[0], kon[0]], [zac[1], kon[1]], color="tab:brown", lw=3)
for s in np.linspace(0.25, L - 0.25, 9):
    sredina = A + smer * s
    ax.plot([sredina[0] - odmik[0], sredina[0] + odmik[0]],
            [sredina[1] - odmik[1], sredina[1] + odmik[1]],
            color="tab:brown", lw=1.5)

# oseba (krog in kratka "noga")
ax.plot(P[0], P[1] + 0.35, "o", ms=14, color="tab:blue")
ax.plot([P[0], P[0]], [P[1], P[1] + 0.25], color="tab:blue", lw=3)


def puscica(zac, dx, dy, barva="tab:red"):
    """Nariše puščico sile od točke zac v smeri (dx, dy)."""
    ax.annotate("", xy=(zac[0] + dx, zac[1] + dy), xytext=zac,
                arrowprops=dict(arrowstyle="-|>", lw=1.6, color=barva))


# sile: teža lestve in osebe, reakcije v A in B
puscica(G, 0.0, -0.9)
ax.text(G[0] - 0.05, G[1] - 1.3, "$m\\,g$", color="tab:red", fontsize=12)
puscica(P, 0.0, -1.1)
ax.text(P[0] - 0.55, P[1] - 1.45, "$m_o\\,g$", color="tab:red", fontsize=12)
puscica(A, 0.0, 1.0, "tab:green")
ax.text(A[0] + 0.1, A[1] + 0.9, "$N_A$", color="tab:green", fontsize=12)
puscica(A, -0.9, 0.0, "tab:green")
ax.text(A[0] - 0.9, A[1] - 0.4, "$F_A$", color="tab:green", fontsize=12)
puscica(B, 0.8, 0.0, "tab:green")
ax.text(B[0] + 0.3, B[1] - 0.4, "$N_B$", color="tab:green", fontsize=12)

# kot theta, dolžina L in lega osebe x (kotirni črti desno od lestve)
lok = np.linspace(np.pi - theta, np.pi, 30)
ax.plot(A[0] + 0.6 * np.cos(lok), A[1] + 0.6 * np.sin(lok), "k", lw=1)
ax.text(A[0] - 0.95, A[1] + 0.2, "$\\theta$", fontsize=13)
pravokotno = np.array([np.sin(theta), np.cos(theta)])
kota_L = pravokotno * 0.9
ax.annotate("", xy=B + kota_L, xytext=A + kota_L,
            arrowprops=dict(arrowstyle="<->", lw=1))
ax.text(G[0] + kota_L[0] + 0.1, G[1] + kota_L[1], "$L$", fontsize=13)
kota_x = pravokotno * 0.45
ax.annotate("", xy=P + kota_x, xytext=A + kota_x,
            arrowprops=dict(arrowstyle="<->", lw=1))
sredina_x = A + smer * x_osebe / 2 + kota_x
ax.text(sredina_x[0] + 0.1, sredina_x[1], "$x$", fontsize=13)

ax.text(0.15, 4.2, "gladka stena", fontsize=10)
ax.text(1.9, -0.55, "tla, $\\mu$", fontsize=10)
ax.set_xlim(-1.4, 4.0)
ax.set_ylim(-0.8, 4.6)
fig.tight_layout()
fig.savefig("skica.png", dpi=150)
print("Shranjeno: skica.png")
