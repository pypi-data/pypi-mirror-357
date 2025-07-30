def bisect(f, a, b, eps=1e-5, N=100):
    """
    Bisection method for finding a root of the scalar function f in the interval [a, b].

    Parameters:
    f (callable): The scalar function for which to find the root.
    a (float): The start of the interval.
    b (float): The end of the interval.
    eps (float): The tolerance for convergence.
    N (int): The maximum number of iterations.

    Returns:
    float: The approximate root of the scalar function f.
    """
    if f(a) * f(b) >= 0:
        raise ValueError("f(a) and f(b) must have different signs.")

    for _ in range(N):
        c = (a + b) / 2
        if abs(f(c)) < eps or (b - a) / 2 < eps:
            return c
        if f(c) * f(a) < 0:
            b = c
        else:
            a = c

    raise RuntimeError("Maximum number of iterations reached without convergence.")


def iterate(f, x0, eps=1e-5, N=100):
    """
    Fixed-point iteration method for finding a root of the scalar function f.

    Parameters:
    f (callable): The scalar function for which to find the root.
    x0 (float or ndarray): The initial guess for the root.
    eps (float): The tolerance for convergence.
    N (int): The maximum number of iterations.

    Returns:
    float: The approximate root of the scalar function f.
    """
    x = x0
    for _ in range(N):
        x_ = f(x)
        if abs(x_ - x) < eps:
            return x_
        x = x_

    raise RuntimeError("Maximum number of iterations reached without convergence.")

def newton(f, df, x0, eps=1e-5, N=100):
    """
    Newton's method for finding a root of the scalar function f.

    Parameters:
    f (callable): The scalar function for which to find the root.
    df (callable): The derivative of the scalar function f.
    x0 (float or ndarray): The initial guess for the root.
    eps (float): The tolerance for convergence.
    N (int): The maximum number of iterations.

    Returns:
    float: The approximate root of the scalar function f.
    """
    x = x0
    for _ in range(N):
        fx = f(x)
        dfx = df(x)
        if dfx == 0:
            raise ValueError("Derivative is zero. No solution found.")
        x_ = x - fx / dfx
        if abs(x_ - x) < eps:
            return x_
        x = x_

    raise RuntimeError("Maximum number of iterations reached without convergence.")