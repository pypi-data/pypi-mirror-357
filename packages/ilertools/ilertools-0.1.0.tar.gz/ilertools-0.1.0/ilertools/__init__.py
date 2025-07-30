from sympy import * # type: ignore
from sympy.stats import Binomial, variance, skewness
from scipy.stats import * # type: ignore
from scipy.spatial import distance
from scipy import integrate
from scipy.special import comb
from itertools import * # type: ignore
from fractions import Fraction
import numpy as np
import math
import random
import inspect
init_printing()


def import_libs():
    def f():
        # from sympy import *
        from sympy.stats import Binomial, variance, skewness
        # from scipy.stats import *
        from scipy.spatial import distance
        from scipy import integrate
        from scipy.special import comb
        # from itertools import *
        from fractions import Fraction
        import numpy as np
        import math
        import random
        init_printing()
    inner_code = inspect.getsource(f)
    print(inner_code)

def сlassical_probability_1():
    """ В группе региональных банков """
    def f():
        def union(A, B):
            return {a + b for a in A for b in B}
        def Omega(group, k):
            return [' '.join(comb) for comb in combinations(group, k)]
        group = np.array(list(union('N', '123456789abс') | union('P', '123456789abcв')))
        omega = Omega(group, 3)
        A = [x for x in omega if x.count('P') >= 1]
        P = len(A) / len(omega)
        round(P, 3)
    inner_code = inspect.getsource(f)
    print(inner_code)

def сlassical_probability_2():
    """ Независимо друг от друга """
    def f():
        w = [str(i) for i in range(1, 12)]
        omega = list(product(w, repeat=4))
        P = [x for x in omega if len(set(x)) < 4]  # Все случаи, где хотя бы двое в одном вагоне
        probability = round(len(P) / len(omega), 3)
        print(probability)
    inner_code = inspect.getsource(f)
    print(inner_code)

def geometric_probability_1():
    """ Двое договорились о """
    def f():
        U1 = uniform()
        U2 = uniform()
        N = 100000
        cnt = 0
        for i in range(N):
            x = U1.rvs(size=1)[0]
            y = U2.rvs(size=1)[0]
            if (x <= y + 2/5) & (y <= x + 2/5):
                cnt += 1
        pstat = cnt / N
        round(pstat, 3)
    inner_code = inspect.getsource(f)
    print(inner_code)

def geometric_probability_2():
    """ В круг радиуса 60 наудачу бросаются """
    def f():
        N = 10000
        R = 60
        r = 20
        cnt = 0
        for i in range(N):
            r1 = sqrt(np.random.uniform(0, R**2))
            r2 = sqrt(np.random.uniform(0, R**2))
            if r1 <= r or r2 <= r:
                cnt += 1
        pstat = cnt / N
        round(pstat, 2)
    inner_code = inspect.getsource(f)
    print(inner_code)

def independent_events_1():
    """ События A, B и C независимы """
    def f():
        def P(event, space):
            return Fraction( len(event) , len(space) )
        A = [True for _ in range(1)] + [False for _ in range(9)]
        B = [True for _ in range(6)] + [False for _ in range(4)]
        C = [True for _ in range(9)] + [False for _ in range(1)]
        omega = list(product(A, B, C))
        omegaIF = [a for a in omega if (a[0] or a[1]) and (a[0] or a[2]) and (a[1] or a[2])]
        omega1 = [a for a in omega if a[0] == True]
        omega1IF = [a for a in omega1 if (a[0] or a[1]) and (a[0] or a[2]) and (a[1] or a[2])]
        round(float(P(omegaIF, omega)), 3), round(float(P(omega1IF, omega1)), 3)
    inner_code = inspect.getsource(f)
    print(inner_code)

def formulas_bayes_1():
    """ Имеется две корзины (без n и p) """
    def f():
        n1 = 28 # общее кол-во шаров в 1-ой корзине
        w1 = 13 # белые 1-ая корзина
        c1 = 5 # извелкаются из 1-ой корзины
        n2 = 37
        w2 = 17
        c2 = 10
        total_white = np.zeros((c1 + 1, c2 + 1))
        for i in range(c1 + 1):
            for j in range(c2 + 1):
                if i <= w1 and j <= w2:
                    prob1 = hypergeom.pmf(i, n1, w1, c1)
                    prob2 = hypergeom.pmf(j, n2, w2, c2)
                    total_white[i, j] = prob1 * prob2

        P_A = sum(total_white[i, j] * (i + j) for i in range(c1 + 1) for j in range(c2 + 1)) / 15
        print(round(P_A, 3))
        P_H = c1 / (c1 + c2)
        P_A_given_H = sum(total_white[i, j] * (i / c1) for i in range(c1 + 1) for j in range(c2 + 1))
        res = (P_A_given_H * P_H) / P_A
        print(round(res, 3)) 
    inner_code = inspect.getsource(f)
    print(inner_code)

def formulas_bayes_2():
    """ Имеется две корзины (n и p) """
    def f():
        P_X1 = {k: binom.pmf(k, 7, 0.3) for k in range(8)}
        P_X2 = {k: binom.pmf(k, 5, 0.5) for k in range(6)}
        b1 = 12
        b2 = 6
        N = b1 + b2
        P_A = sum(P_X1[k1] * P_X2[k2] * (k1 + k2) / N for k1, k2 in product(P_X1.keys(), P_X2.keys()))
        P_A_H = sum(P_X1[k1] * k1 / b1 for k1 in P_X1.keys())
        P_H = b1 / (b1 + b2)
        P_H_A = (P_A_H * P_H) / P_A
        round(P_A, 3), round(P_H_A, 3)
    inner_code = inspect.getsource(f)
    print(inner_code)

def discrete_random_1():
    """ События А, B и С имеют вероятности """
    def f():
        P_A = 0.1
        P_B = 0.4
        P_C = 0.3
        X = bernoulli(P_A)
        Y = bernoulli(P_B)
        Z = bernoulli(P_C)
        E_X = X.mean()
        E_Y = Y.mean()
        E_Z = Z.mean()
        U_coeffs = [3, 7, 2]
        E_U = U_coeffs[0] * E_X + U_coeffs[1] * E_Y + U_coeffs[2] * E_Z
        Var_X = X.var()
        Var_Y = Y.var()
        Var_Z = Z.var()
        Var_U = (U_coeffs[0] ** 2 * Var_X +
                U_coeffs[1] ** 2 * Var_Y +
                U_coeffs[2] ** 2 * Var_Z)
        round(E_U, 1), round(Var_U, 2)
    inner_code = inspect.getsource(f)
    print(inner_code)
    
def discrete_random_2():
    """ Случайная велечина X """
    def f():
        X_values = np.arange(1, 41)
        Y_values = np.abs(X_values - 17.5)
        unique_Y, counts = np.unique(Y_values, return_counts=True)
        prob_Y = counts / 40
        Y = rv_discrete(name='Y', values=(unique_Y, prob_Y))
        Q1min = Y.ppf(0.25)
        P_geq = Y.sf(unique_Y) + Y.pmf(unique_Y)
        valid_Q1Max = unique_Y[np.isclose(P_geq, 0.75, atol=1e-4) | (P_geq >= 0.75)]
        Q1max = valid_Q1Max.max() if valid_Q1Max.size > 0 else np.nan
        Q3min = Y.ppf(0.75)
        P_geq = Y.sf(unique_Y) + Y.pmf(unique_Y)
        valid_Q3Max = unique_Y[np.isclose(P_geq, 0.25, atol=1e-4) | (P_geq >= 0.25)]
        Q3max = valid_Q3Max.max() if valid_Q3Max.size > 0 else np.nan
        round(Q1min, 1), round(Q1max, 1), round(Q3min, 1), round(Q3max, 1)
    inner_code = inspect.getsource(f)
    print(inner_code)

def discrete_random_3():
    """ Распределение случайной велечины X """
    def f():
        xk = np.array([2, 6, 9, 13, 15])
        pxk = np.array([0.1, 0.2, 0.2, 0.3, 0.2])
        X = rv_discrete(name='X', values=(xk, pxk))
        E_X = X.expect()
        E_Y = X.expect(lambda x: np.abs(x - 10))
        E_XY = X.expect(lambda x: x * np.abs(x - 10))
        Var_X = X.var()
        Var_Y = X.expect(lambda x: np.abs(x - 10)**2) - E_Y**2
        round(E_X, 1), round(E_Y, 1), round(E_XY, 1), round(Var_X, 2), round(Var_Y, 2)
    inner_code = inspect.getsource(f)
    print(inner_code)

def special_discrete_1():
    """ Корзина содержит """
    def f():
        N = 63  # общее количество шаров
        K = 18  # количество красных шаров
        L = 6   # количество синих шаров
        n = 24  # количество извлечённых шаров
        cov_xy_formula = -n * K * (L / N ** 2) * (N - n) / (N - 1)
        print(round(cov_xy_formula, 2))
    inner_code = inspect.getsource(f)
    print(inner_code)

def special_discrete_2():
    """ Монеты в количестве """
    def f():
        n_coins = 15
        k_success = 7
        total_successes = 20
        p_success = binomial(n_coins, k_success) / (2 ** n_coins)
        p = Rational(p_success)
        E_X = 1 / p
        var_X = (1 - p) / p**2
        sigma_X = np.sqrt(float(var_X))
        cov_XY = var_X
        var_Y = total_successes * (1 - p) / p**2
        rho_XY = cov_XY / np.sqrt(float(var_X * var_Y))
        E_Y = total_successes / p
        E_XY = float(cov_XY + E_X * E_Y)
        round(E_X, 3), round(sigma_X, 3), round(rho_XY, 3), round(E_XY, 1)
    inner_code = inspect.getsource(f)
    print(inner_code)

def special_discrete_3():
    """ Селекционер отобрал """
    def f():
        n1, p1 = 290, 0.91
        n2, p2 = 160, 0.92
        X = Binomial('X', n1, p1)
        Y = Binomial('Y', n2, p2)
        S = X + Y
        asymm = skewness(S)
        var = variance(S)
        round(var ** 0.5, 1), round(asymm.evalf(), 3)
    inner_code = inspect.getsource(f)
    print(inner_code)

def special_discrete_4():
    """ Независимые пуассоновские """
    def f():
        sigma1 = 1.5
        sigma2 = 1.3
        sigma3 = 1.3
        total = sigma1 ** 2 + sigma2 ** 2 + sigma3 ** 2
        prob_X7 = poisson.pmf(7, total)
        most_val = int(total)
        std = round(np.sqrt(total), 3)
        asymm = 1 / std
        excess = 1 / total
        round(prob_X7, 3), most_val, round(std, 3), round(asymm, 3), round(excess, 3)
    inner_code = inspect.getsource(f)
    print(inner_code)

def continuous_random_1():
    """ Случайная велечина X равномерно распределена """
    def f():
        a, b = (5, 7)
        def EY(X):
            if (a <= X <= b):
                return (1 + 6*X ** 0.5 + 3*X ** 0.7 + 8*X ** 0.9) ** 1.1 * (1/(b - a))
            return 0
        E_Y = integrate.quad(EY, a, b)[0]
        print(f'{E_Y:.1f}')
        def Var(X):
            if (a <= X <= b):
                return (((1 + 6*X ** 0.5 + 3*X ** 0.7 + 8*X ** 0.9) ** 1.1) ** 2 * (1/(b - a)))
            return 0
        std_Y = np.sqrt(integrate.quad(Var, a, b)[0] - E_Y ** 2)
        print(f'{std_Y:.2f}')
        def As(X):
            if (a <= X <= b):
                return (((1 + 6*X ** 0.5 + 3*X ** 0.7 + 8*X ** 0.9) ** 1.1 - E_Y) ** 3 * (1/(b - a)))
            return 0
        asymm_Y = (1 / std_Y ** 3) * integrate.quad(As, a, b)[0]
        print(f'{asymm_Y:.4f}')
        X = symbols('X')
        X_08 = a + 0.8*(b - a)
        Y_08 = float(((1 + 6*X ** 0.5 + 3*X ** 0.7 + 8*X ** 0.9) ** 1.1).subs(X, X_08).evalf())
        print(f'{Y_08:.4f}')
    inner_code = inspect.getsource(f)
    print(inner_code)

def continuous_random_2():
    """ Абсолютно непрерывная случная велечина X """
    def f():
        def func(x):
            return (1 + 2*x ** 0.5 + 3*x ** 0.7 + 7*x ** 0.9) ** 1.5
        a, b = (5, 7)
        def f(x):
            if (a <= x <= b):
                return func(x)
            return 0
        C = 1 / integrate.quad(f, a, b)[0]
        print(f'{C:.5f}')
        def EX(x):
            if (a <= x <= b):
                return C * x * func(x)
            return 0
        E_X = integrate.quad(EX, a, b)[0]
        print(f'{E_X:.3f}')
        def Var(x):
            if (a <= x <= b):
                return C * (x - E_X) ** 2 * func(x)
            return 0
        std_X = np.sqrt(integrate.quad(Var, a, b)[0])
        print(f'{std_X:.3f}')
        class distr(rv_continuous):
            def _pdf(self, x):
                return C * f(x)
        X = distr()
        Q1 = X.ppf(0.8)
        print(f'{Q1:.3f}')
    inner_code = inspect.getsource(f)
    print(inner_code)

def independent_dsv_1():
    """ Доход по типовому контракту """
    def f():
        n = 9
        xk = np.array([5, 8, 9, 10, 11])
        pxk = np.array([0.2, 0.2, 0.2, 0.3, 0.1])
        X = rv_discrete(name='X', values=(xk, pxk))
        E_X = X.mean()
        VarE_X = X.var()
        round(E_X, 2), round(VarE_X / n, 3)
    inner_code = inspect.getsource(f)
    print(inner_code)

def independent_dsv_2():
    """ Вероятность повышения цены акции """
    def f():
        values = [1.05, 1.003, 0.99]
        probs = [0.1, 0.4, 0.5]
        xk = [el for el in values]
        pxk = [pr for pr in probs]
        X = rv_discrete(name='X', values=(xk, pxk))
        xk1 = [el ** 2 for el in values]
        X1 = rv_discrete(name='X1', values=(xk1, pxk))
        S0 = 1000
        n = 150
        ES_150 = S0 * X.mean() ** n
        print(round(ES_150, 2))
        VarS_160 = S0 ** 2 * ((X1.mean()) ** n - X.mean() ** (2 * n))
        print(round(sqrt(VarS_160), 2))
    inner_code = inspect.getsource(f)
    print(inner_code)

def independent_dsv_3():
    """ Игрок начал игру с капиталом """
    def f():
        initial_capital = 11000
        probabilities = [0.1, 0.4, 0.5]
        outcomes = [400, -100, 7]
        n_games = 5
        E_one_game = sum(p * x for p, x in zip(probabilities, outcomes))
        E_total = initial_capital + n_games * E_one_game
        variance_one_game = sum(p * (x - E_one_game)**2 for p, x in zip(probabilities, outcomes))
        variance_total = n_games * variance_one_game
        std_dev = math.sqrt(variance_total)
        print(round(E_total, 2), round(std_dev, 2))
    inner_code = inspect.getsource(f)
    print(inner_code)

def dependent_dsv_1():
    """ Случайные велечины X1, ..., X11 """
    def f():
        vals = [0, 1, 5]
        probs = [0.4, 0.3, 0.3]
        X = rv_discrete(name='X', values=(vals, probs))
        E_X = X.expect()
        VarE_X = X.var()
        probs_sum = [0.12, 0.15, 0.1]
        E_Xi_Xj = (vals[1] * probs_sum[0] + vals[2] * probs_sum[1] + vals[2] ** 2 * probs_sum[2])
        Cov_Xi_Xj = E_Xi_Xj - E_X ** 2
        print(round(Cov_Xi_Xj, 2))
        n = 11
        Var_S = n * VarE_X + n * (n - 1) * Cov_Xi_Xj
        print(round(Var_S, 2))
    inner_code = inspect.getsource(f)
    print(inner_code)

def dependent_dsv_2():
    """ Корзина содержит 35 пронумерованных шаров """
    def f():
        xk = np.arange(1, 36)
        pxk = [1/35] * 35
        X = rv_discrete(name='X', values=(xk, pxk))
        n = 35
        k = 20
        round(k * X.mean(), 2), round((k * (n + 1) / 12) * (n - k), 3)
    inner_code = inspect.getsource(f)
    print(inner_code)

def dependent_dsv_3():
    """ Корзина содержит 47 шаров, на которых изображены цифры: """
    def f():
        total_balls = 47
        balls_1 = 19
        balls_4 = 8
        balls_6 = 20
        n_draws = 14
        E_1 = hypergeom.mean(total_balls, balls_1, n_draws)
        E_4 = hypergeom.mean(total_balls, balls_4, n_draws)
        E_6 = hypergeom.mean(total_balls, balls_6, n_draws)
        Var_1 = hypergeom.var(total_balls, balls_1, n_draws)
        Var_4 = hypergeom.var(total_balls, balls_4, n_draws)
        Var_6 = hypergeom.var(total_balls, balls_6, n_draws)
        cov_1_4 = -n_draws * (balls_1 / total_balls) * (balls_4 / total_balls) * (total_balls - n_draws) / (total_balls - 1)
        cov_1_6 = -n_draws * (balls_1 / total_balls) * (balls_6 / total_balls) * (total_balls - n_draws) / (total_balls - 1)
        cov_4_6 = -n_draws * (balls_4 / total_balls) * (balls_6 / total_balls) * (total_balls - n_draws) / (total_balls - 1)
        E_S = 1 * E_1 + 4 * E_4 + 6 * E_6
        Var_S = (1**2) * Var_1 + (4**2) * Var_4 + (6**2) * Var_6 + 2 * (1 * 4 * cov_1_4 + 1 * 6 * cov_1_6 + 4 * 6 * cov_4_6)
        round(E_S, 3), round(Var_S, 3)
    inner_code = inspect.getsource(f)
    print(inner_code)

def discrete_vectors_1():
    """ Дано совместное рапределение дискретных случайных велечин X и Y """
    def f():
        X_values = np.array([3, 5, 8])
        Y_values = np.array([9, 10])
        joint_prob = np.array([
            [0.24, 0.04, 0.29],   # Y = 9
            [0.09, 0.11, 0.23]    # Y = 10
        ])
        P_X = joint_prob.sum(axis=0)
        E_X = np.sum(X_values * P_X)
        print(f"1. E(X) = {E_X:.3f}")
        E_X_sq = np.sum(X_values**2 * P_X)
        var_X = E_X_sq - E_X**2
        print(f"2. Var(X) = {var_X:.3f}")
        P_Y = joint_prob.sum(axis=1)
        E_Y = np.sum(Y_values * P_Y)
        print(f"3. E(Y) = {E_Y:.3f}")
        E_Y_sq = np.sum(Y_values**2 * P_Y)
        var_Y = E_Y_sq - E_Y**2
        print(f"4. Var(Y) = {var_Y:.3f}")
        E_XY = np.sum([x * y * joint_prob[j, i]
                    for i, x in enumerate(X_values)
                    for j, y in enumerate(Y_values)])
        cov_XY = E_XY - E_X * E_Y
        rho_XY = cov_XY / (np.sqrt(var_X) * np.sqrt(var_Y))
        print(f"5. ρ(X, Y) = {rho_XY:.3f}")
    inner_code = inspect.getsource(f)
    print(inner_code)

def discrete_vectors_2():
    """ Распределение случайного вектора имеет вид """
    def f():
        X_values = np.array([1, 3, 5])
        Y_values = np.array([8, 9])
        joint_prob = np.array([
            [0.12, 0.06, 0.08],
            [0.44, 0.29, 0.01]
        ])
        P_X = joint_prob.sum(axis=0)
        E_X = np.sum(X_values * P_X)
        print(f"1. E(X) = {E_X:.3f}")
        E_X_squared = np.sum(X_values**2 * P_X)
        var_X = E_X_squared - E_X**2
        print(f"2. Var(X) = {var_X:.3f}")
        E_XY = np.sum([x * y * joint_prob[j, i] for i, x in enumerate(X_values) for j, y in enumerate(Y_values)])
        print(f"3. E(XY) = {E_XY:.3f}")
        P_Y = joint_prob.sum(axis=1)
        E_Y = np.sum(Y_values * P_Y)
        cov_XY = E_XY - E_X * E_Y
        print(f"4. Cov(X, Y) = {cov_XY:.3f}")
        var_Y = np.sum(Y_values**2 * P_Y) - E_Y**2
        rho_XY = cov_XY / np.sqrt(var_X * var_Y)
        print(f"5. ρ(X, Y) = {rho_XY:.3f}")
    inner_code = inspect.getsource(f)
    print(inner_code)

def discrete_vectors_3():
    """ Распределение случайного вектора имеет вид """
    def f():
        X_values = np.array([4, 5, 7])
        Y_values = np.array([8, 11])
        joint_prob = np.array([
            [0.17, 0.19, 0.12],
            [0.18, 0.05, 0.29]
        ])
        P_X = joint_prob.sum(axis=0)
        E_X = np.sum(X_values * P_X)
        print(f"1. E(X) = {E_X:.3f}")
        E_X_squared = np.sum(X_values**2 * P_X)
        var_X = E_X_squared - E_X**2
        sigma_X = np.sqrt(var_X)
        print(f"2. σ(X) = {sigma_X:.3f}")
        P_Y = joint_prob.sum(axis=1)
        E_Y = np.sum(Y_values * P_Y)
        E_Y_squared = np.sum(Y_values**2 * P_Y)
        var_Y = E_Y_squared - E_Y**2
        sigma_Y = np.sqrt(var_Y)
        print(f"3. σ(Y) = {sigma_Y:.3f}")
        E_XY = 0
        for i, x in enumerate(X_values):
            for j, y in enumerate(Y_values):
                E_XY += x * y * joint_prob[j, i]
        cov_XY = E_XY - E_X * E_Y
        print(f"4. Cov(X, Y) = {cov_XY:.3f}")
        rho_XY = cov_XY / (sigma_X * sigma_Y)
        print(f"5. ρ(X, Y) = {rho_XY:.3f}")
    inner_code = inspect.getsource(f)
    print(inner_code)

def discrete_vectors_4():
    """ Дано совместное рапределение дискретных случайных велечин X и Y """
    def f():
        X_values = np.array([2, 5, 6])
        Y_values = np.array([10, 11])
        joint_prob = np.array([
            [0.02, 0.31, 0.04],
            [0.21, 0.19, 0.23]
        ])
        X_sq_values = X_values**2
        Y_sq_values = Y_values**2
        P_X = joint_prob.sum(axis=0)
        E_X_sq = np.sum(X_sq_values * P_X)
        print(f"1. E(X²) = {E_X_sq:.3f}")
        E_X_sq_sq = np.sum(X_sq_values**2 * P_X)
        var_X_sq = E_X_sq_sq - E_X_sq**2
        sigma_X_sq = np.sqrt(var_X_sq)
        print(f"2. σ(X²) = {sigma_X_sq:.3f}")
        P_Y = joint_prob.sum(axis=1)
        E_Y_sq = np.sum(Y_sq_values * P_Y)
        E_Y_sq_sq = np.sum(Y_sq_values**2 * P_Y)
        var_Y_sq = E_Y_sq_sq - E_Y_sq**2
        sigma_Y_sq = np.sqrt(var_Y_sq)
        print(f"3. σ(Y²) = {sigma_Y_sq:.3f}")
        E_Xsq_Ysq = np.sum([x_sq * y_sq * joint_prob[j, i]
                        for i, x_sq in enumerate(X_sq_values)
                        for j, y_sq in enumerate(Y_sq_values)])
        cov_Xsq_Ysq = E_Xsq_Ysq - E_X_sq * E_Y_sq
        print(f"4. Cov(X², Y²) = {cov_Xsq_Ysq:.3f}")
        rho_Xsq_Ysq = cov_Xsq_Ysq / (sigma_X_sq * sigma_Y_sq)
        print(f"5. ρ(X², Y²) = {rho_Xsq_Ysq:.3f}")
    inner_code = inspect.getsource(f)
    print(inner_code)

def discrete_vectors_5():
    """ Распределение случайного вектора имеет вид """
    def f():
        X_values = np.array([1, 4, 5])
        Y_values = np.array([7, 9])
        joint_prob = np.array([
            [0.28, 0.02, 0.03],   # Y = 7
            [0.31, 0.05, 0.31]    # Y = 9
        ])
        P_X = joint_prob.sum(axis=0)
        X_sq_values = X_values ** 2
        E_X_sq = np.sum(X_sq_values * P_X)
        print(f"1. E(X²) = {E_X_sq:.3f}")
        X_quad_values = X_values ** 4
        E_X_quad = np.sum(X_quad_values * P_X)
        print(f"2. E(X⁴) = {E_X_quad:.3f}")
        var_X_sq = E_X_quad - E_X_sq ** 2
        print(f"3. Var(X²) = {var_X_sq:.3f}")
        E_X_sq_Y = np.sum([x_sq * y * joint_prob[j, i]
                        for i, x_sq in enumerate(X_sq_values)
                        for j, y in enumerate(Y_values)])
        print(f"4. E(X²Y) = {E_X_sq_Y:.3f}")
        P_Y = joint_prob.sum(axis=1)
        E_Y = np.sum(Y_values * P_Y)
        cov_X_sq_Y = E_X_sq_Y - E_X_sq * E_Y
        print(f"5. Cov(X², Y) = {cov_X_sq_Y:.3f}")
    inner_code = inspect.getsource(f)
    print(inner_code)

def discrete_vectors_6():
    """ Распределение случайного вектора имеет вид """
    def f():
        X_values = np.array([3, 5, 7])
        Y_values = np.array([10, 11])
        joint_prob = np.array([
            [0.04, 0.18, 0.01],   # Y = 10
            [0.47, 0.17, 0.13]    # Y = 11
        ])
        X_sq_values = X_values ** 2
        P_X = joint_prob.sum(axis=0)
        E_X_sq = np.sum(X_sq_values * P_X)
        print(f"1. E(X²) = {E_X_sq:.3f}")
        P_Y = joint_prob.sum(axis=1)
        E_Y = np.sum(Y_values * P_Y)
        print(f"2. E(Y) = {E_Y:.3f}")
        E_X_sq_sq = np.sum(X_sq_values ** 2 * P_X)
        var_X_sq = E_X_sq_sq - E_X_sq ** 2
        sigma_X_sq = np.sqrt(var_X_sq)
        print(f"3. σ(X²) = {sigma_X_sq:.3f}")
        E_Y_sq = np.sum(Y_values ** 2 * P_Y)
        var_Y = E_Y_sq - E_Y ** 2
        sigma_Y = np.sqrt(var_Y)
        print(f"4. σ(Y) = {sigma_Y:.3f}")
        E_X_sq_Y = np.sum([x_sq * y * joint_prob[j, i]
                        for i, x_sq in enumerate(X_sq_values)
                        for j, y in enumerate(Y_values)])
        cov_X_sq_Y = E_X_sq_Y - E_X_sq * E_Y
        rho_X_sq_Y = cov_X_sq_Y / (sigma_X_sq * sigma_Y)
        print(f"5. ρ(X², Y) = {rho_X_sq_Y:.3f}")
    inner_code = inspect.getsource(f)
    print(inner_code)

def independent_discrete_1():
    """ Внутри квадрата площади 100 расположены треугольник и круг """
    def f():
        square_area = 100
        triangle_area = 44
        circle_area = 40
        intersection_area = 20
        p_triangle = triangle_area / square_area  # P(X=1)
        p_circle = circle_area / square_area      # P(Y=1)
        p_intersection = intersection_area / square_area  # P(X=1 и Y=1)
        p_Z0 = 1 - p_triangle - p_circle + p_intersection
        p_Z1 = (p_triangle - p_intersection) + (p_circle - p_intersection)
        p_Z2 = p_intersection
        E_Z = 0*p_Z0 + 1*p_Z1 + 2*p_Z2
        E_U = 3 * E_Z
        print(f"1. E(U) = {E_U:.3f}")
        E_Z_sq = 0*p_Z0 + 1*p_Z1 + 4*p_Z2
        var_Z = E_Z_sq - E_Z**2
        var_U = 3 * var_Z
        print(f"2. Var(U) = {var_U:.3f}")
        E_V = E_Z ** 3
        print(f"3. E(V) = {E_V:.3f}")
        E_Z_sq = p_Z1 + 4*p_Z2
        E_V_sq = (p_Z1 + 4*p_Z2) ** 3
        var_V = E_V_sq - E_V**2
        print(f"4. Var(V) = {var_V:.3f}")
    inner_code = inspect.getsource(f)
    print(inner_code)

def normal_vectors_1():
    """ Случайный вектор (X, Y) имеет плотность распределения """
    def f():
        Sigma_inv = np.array([[20, 24], [24, 45]])
        Sigma = np.linalg.inv(Sigma_inv)
        mu = Sigma @ np.array([5, 6])
        E_X, E_Y = mu
        Var_X = Sigma[0, 0]
        Var_Y = Sigma[1, 1]
        Cov_XY = Sigma[0, 1]
        rho = Cov_XY / np.sqrt(Var_X * Var_Y)
        print(f"1) E(X) = {E_X:.4f}")
        print(f"2) E(Y) = {E_Y:.4f}")
        print(f"3) Var(X) = {Var_X:.4f}")
        print(f"4) Var(Y) = {Var_Y:.4f}")
        print(f"5) Cov(X, Y) = {Cov_XY:.4f}")
        print(f"6) ρ(X, Y) = {rho:.4f}")
    inner_code = inspect.getsource(f)
    print(inner_code)

def normal_vectors_2():
    """ Для нормального случайного вектора: P((X-8)(X-11)(Y-1)<0) """
    def f():
        mu_x = -2
        mu_y = 4
        var_x = 9
        var_y = 36
        corr = 0.68
        cov = corr * np.sqrt(var_x) * np.sqrt(var_y)
        cov_matrix = [[var_x, cov], [cov, var_y]]
        mvn = multivariate_normal(mean=[mu_x, mu_y], cov=cov_matrix)
        X = norm(loc=mu_x, scale=np.sqrt(var_x))
        Y = norm(loc=mu_y, scale=np.sqrt(var_y))
        P_A = mvn.cdf([8, 1])
        P_B = X.cdf(11) - X.cdf(8) - (mvn.cdf([11, 1]) - mvn.cdf([8, 1]))
        P_C = Y.cdf(1) - mvn.cdf([11, 1])
        round(P_A + P_B + P_C, 4)
    inner_code = inspect.getsource(f)
    print(inner_code)

def normal_vectors_3():
    """ Для нормального случайного вектора: P((X-4)(Y-3)<0) """
    def f():
        mu_x = -7
        mu_y = 17
        sigma_x = np.sqrt(81)
        sigma_y = np.sqrt(16)
        rho = 0.6
        cov_xy = rho * sigma_x * sigma_y
        cov_matrix = [[sigma_x ** 2, cov_xy], [cov_xy, sigma_y ** 2]]
        mvn = multivariate_normal(mean=[mu_x, mu_y], cov=cov_matrix)
        X = norm(loc=mu_x, scale=sigma_x)
        Y = norm(loc=mu_y, scale=sigma_y)
        round(X.cdf(4) + Y.cdf(3) - 2 * mvn.cdf([4, 3]), 5)
    inner_code = inspect.getsource(f)
    print(inner_code)

def conditional_sv_1():
    """ Максимальный ущерб от страхового случая составляет """
    def f():
        max_loss = 3.4  # Максимальный ущерб
        avg_cases = 16 / 5  # Среднее число случаев в год (16 за 5 лет)
        E_S = avg_cases * max_loss / 2
        std_S = np.sqrt(avg_cases * max_loss**2 / 3)
        print(f"1) {E_S:.2f} руб.")
        print(f"2) {std_S:.2f} руб.")
    inner_code = inspect.getsource(f)
    print(inner_code)

def conditional_sv_2():
    """ В первом броске учавствуют 115 несимметричных монет. Отв: 'без орлов' """
    def f():
        n = 115
        p = 0.4
        E_conditional_variance = n * p * (1 - p)
        E_X = n * p
        E_D_Y_given_X = (1 - p) * p * E_X
        D_X = n * p * (1 - p)
        D_E_Y_given_X = p**2 * D_X
        print(f"1) {E_D_Y_given_X:.4f}")
        print(f"2) {D_E_Y_given_X:.4f}")
    inner_code = inspect.getsource(f)
    print(inner_code)

def conditional_sv_3():
    """ В первом броске учавствуют 115 несимметричных монет. Отв: 'орлов' """
    def f():
        n = 56
        p = 0.6
        E_Y = n * p * p
        E_conditional_variance = n * p * p * (1 - p)
        print(f"1) {E_Y:.3f}")
        print(f"2) {E_conditional_variance:.4f}")
    inner_code = inspect.getsource(f)
    print(inner_code)

def conditional_sv_4():
    """ В первом броске учавствуют 186 несимметричных монет. Отв: мат. ожид. """
    def f():
        n = 186
        p = 0.65
        E_Y = n * p * p
        D_X = n * p * (1 - p)
        D_E_Y_given_X = (p ** 2) * D_X
        print(f"1) {E_Y:.3f}")
        print(f"2) {D_E_Y_given_X:.4f}")
    inner_code = inspect.getsource(f)
    print(inner_code)

def conditional_sv_5():
    """ Для случайной цены Y известны вероятности: """
    def f():
        P_Y = {9: 0.4, 18: 0.6}
        E_XY = sum(y * (6*y)/2 * p for y, p in P_Y.items())
        E_Y = sum(y * p for y, p in P_Y.items())
        E_X = sum((6*y)/2 * p for y, p in P_Y.items())
        E_XY_cov = E_XY - E_X * E_Y
        print(f"1) {E_XY:.3f}")
        print(f"2) {E_XY_cov:.4f}")
    inner_code = inspect.getsource(f)
    print(inner_code)

def conditional_sv_6():
    """ Игральная кость и 25 монет подбрасываются до тех пор, """
    def f():
        n_coins = 25
        target_heads = 15
        p_head = 0.5
        p_success = comb(n_coins, target_heads) * (p_head ** n_coins)
        E_N = 1 / p_success
        Var_N = (1 - p_success) / (p_success ** 2)
        E_dice = 3.5
        count_sides = 6
        Var_dice = (count_sides ** 2 - 1) / 12
        E_S = E_N * E_dice
        Var_S = E_N * Var_dice + (E_dice ** 2) * Var_N
        sigma_S = np.sqrt(Var_S)
        print(f"1) {E_S:.4f}")
        print(f"2) {sigma_S:.4f}")
    inner_code = inspect.getsource(f)
    print(inner_code)

def conditional_vectors_1():
    """ Дано совместное рапределение дискретных случайных велечин X и Y. Отв: E5 = E(E(X|Y)) """
    def f():
        joint_prob = {
            (2,6): 0.29,
            (3,6): 0.06,
            (5,6): 0.01,
            (2,7): 0.28,
            (3,7): 0.02,
            (5,7): 0.34
        }
        P1 = sum(v for (x,y), v in joint_prob.items() if y == 6)
        P2 = sum(v for (x,y), v in joint_prob.items() if y == 7)
        E3 = sum(x*v for (x,y), v in joint_prob.items() if y == 6) / P1
        E4 = sum(x*v for (x,y), v in joint_prob.items() if y == 7) / P2
        E5 = E3*P1 + E4*P2
        print(f"1) {P1:.2f}")
        print(f"2) {P2:.2f}")
        print(f"3) {E3:.4f}")
        print(f"4) {E4:.4f}")
        print(f"5) {E5:.2f}")
    inner_code = inspect.getsource(f)
    print(inner_code)

def portfolio_analysis_1():
    """ Математическое ожидание доходности акций компаний А и B составляет """
    def f():
        E_A, E_B = 0.01, 0.02  # Мат. ожидания доходностей
        sigma_A, sigma_B = 0.03, 0.05  # Стандартные отклонения
        rho = 0.31  # Коэффициент корреляции
        cov = rho * sigma_A * sigma_B
        w_A = (sigma_B**2 - cov) / (sigma_A**2 + sigma_B**2 - 2*cov)
        w_B = 1 - w_A
        E_portfolio = w_A * E_A + w_B * E_B
        sigma_portfolio = np.sqrt(w_A**2 * sigma_A**2 + w_B**2 * sigma_B**2 + 2*w_A*w_B*cov)
        print(f"1) Доля A = {w_A:.3f}; Доля B = {w_B:.3f}")
        print(f"2) Ожидаемая доходность = {E_portfolio:.4f}%; Стандартное отклонение = {sigma_portfolio:.5f}%")
    inner_code = inspect.getsource(f)
    print(inner_code)

def portfolio_analysis_2():
    """ Инвестор сформировал портфель из акций команий А и B, """
    def f():
        w_A = 10 / (10 + 1)  # Доля акций A (10 частей из 11)
        w_B = 1 / (10 + 1)    # Доля акций B (1 часть из 11)
        E_A, E_B = 0.01, 0.05  # Ожидаемые доходности (%)
        sigma_A, sigma_B = 0.03, 0.08  # Стандартные отклонения (%)
        rho = 0.4  # Коэффициент корреляции
        cov = rho * sigma_A * sigma_B
        sigma_portfolio = np.sqrt(w_A**2 * sigma_A**2 + w_B**2 * sigma_B**2 + 2 * w_A * w_B * cov)
        otv = sigma_portfolio * 100
        print(f"1) {otv:.6f}")
    inner_code = inspect.getsource(f)
    print(inner_code)

def portfolio_analysis_3():
    """ Ожидаемая доходность и стандартное отклонение доходности за период """
    def f():
        returns = np.array([0.02, 0.03, 0.04])  # Ожидаемые доходности A, B, C (%)
        volatilities = np.array([0.03, 0.05, 0.06])  # Стандартные отклонения A, B, C (%)
        weights = 1 / volatilities**2
        weights /= weights.sum()
        portfolio_return = np.dot(weights, returns)
        otv= portfolio_return * 100
        print(f"1) {otv:.3f}")
    inner_code = inspect.getsource(f)
    print(inner_code)

def monte_carlo_1():
    """ В области ограниченной эллипсом """
    def f():
        def point():
            while True:
                u = random.uniform(-13, 13)
                v = random.uniform(-9, 9)
                if (u / 13) ** 2 + (v / 9) ** 2 <= 1:
                    return [u, v]
        counter_A = 0
        for i in range(10**5):
            point1 = point()
            point2 = point()
            counter_A += distance.euclidean(point1, point2) < 5.2
        print(counter_A / 10 ** 5)
        counter_B, counter_A = 0, 0
        for i in range(10**5):
            point1 = point()
            point2 = point()
            if all(map(lambda x: x < 0, point1 + point2)):
                counter_B += 1
                counter_A += distance.euclidean(point1, point2) < 5.2
        print(counter_A / counter_B)
    inner_code = inspect.getsource(f)
    print(inner_code)

def monte_carlo_2():
    """ В прямоугольной области """
    def f():
        def length(point1, point2):
            return sqrt((point2[0] - point1[0])**2 + (point2[1] - point1[1])**2)
        N = 100000
        cnt_A = 0
        cnt_B = 0
        for i in range(N):
            point1 = random.uniform(-20, 20), random.uniform(-8, 8)
            point2 = random.uniform(-20, 20), random.uniform(-8, 8)
            if abs(point1[0] - point2[0]) < 14:
                cnt_B += 1
            if length(point1, point2) < 11:
                cnt_A += 1
        pstat_A = cnt_A / N
        pstatA_B = cnt_A / cnt_B
        print(round(pstat_A, 2), round(pstatA_B, 2))
    inner_code = inspect.getsource(f)
    print(inner_code)

def monte_carlo_3():
    """ В кубе объема 3 случайным образом """
    def f():
        n_acute = 0
        r_count = 0
        s_count = 0
        while n_acute < 100000:
            points = np.random.rand(3, 3)
            a = distance.euclidean(points[1], points[2])
            b = distance.euclidean(points[0], points[2])
            c = distance.euclidean(points[0], points[1])
            if a + b > c and a + c > b and b + c > a:
                angles = np.degrees(np.arccos([
                    (b**2 + c**2 - a**2) / (2 * b * c),
                    (a**2 + c**2 - b**2) / (2 * a * c),
                    (a**2 + b**2 - c**2) / (2 * a * b)
                ]))
                if np.all(angles < 90):
                    n_acute += 1
                    min_angle = np.min(angles)
                    max_angle = np.max(angles)
                    if min_angle < 35.6:
                        r_count += 1
                    if max_angle < 68.4:
                        s_count += 1
        p_r_given_t = r_count / n_acute
        p_s_given_t = s_count / n_acute
        print(f"P(R|T) ≈ {p_r_given_t:.2f}")
        print(f"P(S|T) ≈ {p_s_given_t:.2f}")
    inner_code = inspect.getsource(f)
    print(inner_code)

def get_methods():
    def f():
        'Название методов:'
        'import_libs() –> Импорт библиотек'
        'сlassical_probability_n() –> Задание №1'
        'geometric_probability_n() –> Задание №1'
        'independent_events_n() –> Задание №1'
        'formulas_bayes_n() –> Задание №1'
        'monte_carlo_n() –> Задание №1'
        'discrete_random_n() –> Задание №2'
        'independent_dsv_n() –> Задание №2'
        'independent_discrete_n() –> Задание №2'
        'special_discrete_n() –> Задание №3'
        'dependent_dsv_n() –> Задание №3'
        'portfolio_analysis_n() –> Задание №3'
        'continuous_random_n() –> Задание №4'
        'normal_vectors_n() –> Задание №4'
        'discrete_vectors_n() –> Задание №5'
        'conditional_sv_n() –> Задание №6'
        'conditional_vectors_n() –> Задание №6'
        'n - это номер шаблона, n=[1, 6]'
    inner_code = inspect.getsource(f)
    print(inner_code)

def find_docs(search_string):
    """ 
    Пример: 
    method = find_docs('независимые пуассоновские')
    потом method() 
    если NoneType -> условия нет
    """
    current_module = globals()
    for name, obj in current_module.items():
        if inspect.isfunction(obj) and obj.__doc__:
            if search_string.lower() in obj.__doc__.lower():
                return obj
    return None