def forward_difference(f, x, h=1e-5):
    """
    Menghitung turunan numerik pertama menggunakan metode selisih maju (forward difference).

    Parameters
    ----------
    f : function
        Fungsi yang akan diturunkan.
    x : float
        Titik di mana turunan dihitung.
    h : float, optional
        Langkah kecil untuk pendekatan numerik (default: 1e-5).

    Returns
    -------
    float
        Nilai pendekatan turunan pertama di titik x.

    Examples
    --------
    >>> forward_difference(lambda x: x**2, 2)
    4.000010000027032
    """
    return (f(x + h) - f(x)) / h


def central_difference(f, x, h=1e-5):
    """
    Menghitung turunan numerik pertama menggunakan metode selisih tengah (central difference).

    Parameters
    ----------
    f : function
        Fungsi yang akan diturunkan.
    x : float
        Titik di mana turunan dihitung.
    h : float, optional
        Langkah kecil untuk pendekatan numerik (default: 1e-5).

    Returns
    -------
    float
        Nilai pendekatan turunan pertama di titik x.

    Examples
    --------
    >>> central_difference(lambda x: x**2, 2)
    4.000000000026205
    """
    return (f(x + h) - f(x - h)) / (2 * h)


def trapezoidal(f, a, b, n=100):
    """
    Menghitung integral tentu menggunakan metode Trapezoidal.

    Parameters
    ----------
    f : function
        Fungsi yang akan diintegralkan.
    a : float
        Batas bawah integral.
    b : float
        Batas atas integral.
    n : int, optional
        Jumlah subinterval (default: 100).

    Returns
    -------
    float
        Nilai pendekatan integral tentu dari f(x) pada [a, b].

    Examples
    --------
    >>> trapezoidal(lambda x: x**2, 0, 1)
    0.33335
    """
    h = (b - a) / n
    result = 0.5 * (f(a) + f(b))
    for i in range(1, n):
        result += f(a + i * h)
    return result * h


def simpsons_one_third(f, a, b, n=100):
    """
    Menghitung integral tentu menggunakan metode Simpson's 1/3.

    Parameters
    ----------
    f : function
        Fungsi yang akan diintegralkan.
    a : float
        Batas bawah integral.
    b : float
        Batas atas integral.
    n : int, optional
        Jumlah subinterval (default: 100). Akan dibulatkan ke genap jika ganjil.

    Returns
    -------
    float
        Nilai pendekatan integral tentu dari f(x) pada [a, b].

    Examples
    --------
    >>> simpsons_one_third(lambda x: x**2, 0, 1)
    0.3333333333333333
    """
    if n % 2 == 1:
        n += 1
    h = (b - a) / n
    result = f(a) + f(b)
    for i in range(1, n):
        coef = 4 if i % 2 == 1 else 2
        result += coef * f(a + i * h)
    return result * h / 3