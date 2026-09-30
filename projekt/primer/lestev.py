"""
Lestev ob gladki steni: statika (zdrs) in dinamika padca.

Modul zbira funkcije, ki jih poročilo uporabi večkrat: matriko in desno
stran ravnotežnih enačb, kritično lego osebe in kritični kot, kotno
hitrost padca iz energije, silo stene med padcem, desno stran
diferencialne enačbe padca in lastno Eulerjevo metodo.

Oznake: theta je kot lestve od tal [rad], L dolžina lestve [m],
m masa lestve [kg], m_o masa osebe [kg], x lega osebe od spodnjega
konca [m], mu koeficient trenja na tleh [-], g težni pospešek [m/s^2].
Funkcije ne rišejo in ne izpisujejo; vračajo samo številske rezultate.
"""

from __future__ import annotations

from typing import Callable

import numpy as np


def matrika_ravnotezja(theta: float, L: float) -> np.ndarray:
    """
    Matrika ravnotežnih enačb lestve za neznanke [F_A, N_A, N_B].

    Vrstice so vsota sil v x, vsota sil v y in vsota momentov okoli
    spodnjega konca A. Matrika je odvisna le od kota lestve.

    Parameters
    ----------
    theta : float
        Kot lestve od tal [rad].
    L : float
        Dolžina lestve [m].

    Returns
    -------
    ndarray, shape (3, 3)
        Matrika sistema.
    """
    A = np.array([[1.0, 0.0, -1.0],
                  [0.0, 1.0, 0.0],
                  [0.0, 0.0, L * np.sin(theta)]])
    return A


def desna_stran(theta: float, x: float, m: float, m_o: float,
                L: float, g: float) -> np.ndarray:
    """
    Desna stran ravnotežnih enačb (obremenitve).

    Parameters
    ----------
    theta : float
        Kot lestve od tal [rad].
    x : float
        Lega osebe od spodnjega konca [m].
    m, m_o : float
        Masa lestve in masa osebe [kg].
    L : float
        Dolžina lestve [m].
    g : float
        Težni pospešek [m/s^2].

    Returns
    -------
    ndarray, shape (3,)
        Vektor desne strani [N, N, N m].
    """
    moment = (m * L / 2 + m_o * x) * g * np.cos(theta)
    b = np.array([0.0, (m + m_o) * g, moment])
    return b


def kriticna_lega(theta: float, mu: float, m: float, m_o: float,
                  L: float) -> float:
    """
    Lega osebe, pri kateri lestev začne drseti (F_A = mu N_A).

    Parameters
    ----------
    theta : float
        Kot lestve od tal [rad].
    mu : float
        Koeficient trenja med lestvijo in tlemi [-].
    m, m_o : float
        Masa lestve in masa osebe [kg].
    L : float
        Dolžina lestve [m].

    Returns
    -------
    float
        Kritična lega x_kr [m]; lahko je tudi zunaj [0, L].
    """
    x_kr = (mu * (m + m_o) * L * np.tan(theta) - m * L / 2) / m_o
    return x_kr


def kriticni_kot(mu: float) -> float:
    """
    Najmanjši kot, pri katerem lestev brez osebe še ne zdrsne.

    Parameters
    ----------
    mu : float
        Koeficient trenja med lestvijo in tlemi [-].

    Returns
    -------
    float
        Kritični kot [rad], tan(theta_kr) = 1 / (2 mu).
    """
    return np.arctan(1.0 / (2.0 * mu))


def omega_energija(theta: np.ndarray, theta0: float, L: float,
                   g: float) -> np.ndarray:
    """
    Kotna hitrost padajoče lestve iz ohranitve energije.

    Velja za lestev brez trenja, ki se dotika tal in stene in je bila
    izpuščena iz mirovanja pri kotu theta0.

    Parameters
    ----------
    theta : ndarray
        Kot lestve [rad], theta <= theta0.
    theta0 : float
        Začetni kot [rad].
    L : float
        Dolžina lestve [m].
    g : float
        Težni pospešek [m/s^2].

    Returns
    -------
    ndarray
        Velikost kotne hitrosti [rad/s].
    """
    return np.sqrt(3.0 * g / L * (np.sin(theta0) - np.sin(theta)))


def pospesek_kota(theta: np.ndarray, L: float, g: float) -> np.ndarray:
    """
    Kotni pospešek padajoče lestve brez trenja.

    Parameters
    ----------
    theta : ndarray
        Kot lestve [rad].
    L : float
        Dolžina lestve [m].
    g : float
        Težni pospešek [m/s^2].

    Returns
    -------
    ndarray
        Kotni pospešek [rad/s^2].
    """
    return -3.0 * g / (2.0 * L) * np.cos(theta)


def sila_stene(theta: np.ndarray, omega: np.ndarray, m: float,
               L: float, g: float) -> np.ndarray:
    """
    Sila gladke stene na lestev med padcem iz trenutnega stanja.

    Izhaja iz N_B = m * d^2 x_G / dt^2 z x_G = L/2 cos(theta).

    Parameters
    ----------
    theta, omega : ndarray
        Kot [rad] in kotna hitrost [rad/s] lestve.
    m : float
        Masa lestve [kg].
    L : float
        Dolžina lestve [m].
    g : float
        Težni pospešek [m/s^2].

    Returns
    -------
    ndarray
        Sila stene N_B [N]; negativna vrednost pomeni odlepitev.
    """
    alfa = pospesek_kota(theta, L, g)
    pospesek_x = -L / 2 * (np.cos(theta) * omega**2 + np.sin(theta) * alfa)
    return m * pospesek_x


def sila_stene_energija(theta: np.ndarray, theta0: float, m: float,
                        g: float) -> np.ndarray:
    """
    Sila gladke stene kot funkcija kota (kotna hitrost iz energije).

    Parameters
    ----------
    theta : ndarray
        Kot lestve [rad].
    theta0 : float
        Začetni kot [rad].
    m : float
        Masa lestve [kg].
    g : float
        Težni pospešek [m/s^2].

    Returns
    -------
    ndarray
        Sila stene N_B [N].
    """
    faktor = 3.0 * np.sin(theta) - 2.0 * np.sin(theta0)
    return 3.0 * m * g / 4.0 * np.cos(theta) * faktor


def kot_odlepitve(theta0: float) -> float:
    """
    Kot, pri katerem se zgornji konec lestve odlepi od stene.

    Parameters
    ----------
    theta0 : float
        Začetni kot [rad].

    Returns
    -------
    float
        Kot odlepitve [rad], sin(theta_od) = 2/3 sin(theta0).
    """
    return np.arcsin(2.0 / 3.0 * np.sin(theta0))


def integrand_casa(theta: np.ndarray, theta0: float, L: float,
                   g: float) -> np.ndarray:
    """
    Integrand za čas padca, dt/dtheta = 1 / omega(theta).

    Parameters
    ----------
    theta : ndarray
        Kot lestve [rad], theta < theta0.
    theta0 : float
        Začetni kot [rad].
    L : float
        Dolžina lestve [m].
    g : float
        Težni pospešek [m/s^2].

    Returns
    -------
    ndarray
        Vrednost integranda [s/rad]; pri theta0 ima singularnost.
    """
    return 1.0 / omega_energija(theta, theta0, L, g)


def desna_stran_de(t: float, y: np.ndarray, L: float,
                   g: float) -> np.ndarray:
    """
    Desna stran sistema 1. reda za padec lestve brez trenja.

    Stanje je y = [theta, omega].

    Parameters
    ----------
    t : float
        Čas [s]; v enačbi ne nastopa.
    y : ndarray, shape (2,)
        Kot [rad] in kotna hitrost [rad/s].
    L : float
        Dolžina lestve [m].
    g : float
        Težni pospešek [m/s^2].

    Returns
    -------
    ndarray, shape (2,)
        Odvod stanja [rad/s, rad/s^2].
    """
    theta, omega = y
    return np.array([omega, pospesek_kota(theta, L, g)])


def euler(f: Callable, y0: np.ndarray, t: np.ndarray,
          args: tuple = ()) -> np.ndarray:
    """
    Eksplicitna Eulerjeva metoda za sistem y' = f(t, y).

    Parameters
    ----------
    f : callable
        Desna stran f(t, y, *args), vrne ndarray oblike y.
    y0 : ndarray
        Začetno stanje.
    t : ndarray
        Časovne točke (enakomerne ali ne).
    args : tuple
        Dodatni argumenti za f.

    Returns
    -------
    ndarray, shape (len(t), len(y0))
        Rešitev v časovnih točkah.
    """
    y = np.zeros((t.size, np.size(y0)))
    y[0] = y0
    for i in range(t.size - 1):
        dt = t[i + 1] - t[i]
        y[i + 1] = y[i] + dt * f(t[i], y[i], *args)
    return y
