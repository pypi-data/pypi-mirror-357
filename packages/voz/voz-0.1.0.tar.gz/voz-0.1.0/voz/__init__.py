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
import pyperclip
import io
import sys
init_printing()


def import_libs():
    def f():
        # from sympy import *
        from sympy.stats import Binomial, variance, skewness
        # from scipy.stats import *
        from scipy.spatial import distance
        from scipy import integrate
        from scipy.stats import poisson
        from scipy.special import comb
        # from itertools import *
        from fractions import Fraction
        import numpy as np
        import math
        import random
        init_printing()
    inner_code = inspect.getsource(f)
    print(inner_code)

def classical_probability_1():
    """ В группе """
    def f():
        def union(A, B):
            return {a + b for a in A for b in B}

        def Omega(arr, k):
            return [" ".join(comb) for comb in combinations(arr, k)]
        
        group = list(union("N", "123456789abc") | union("P", "123456789abcd")) 
        omega = Omega(group, 3)
        len([x for x in omega if x.count('P') >= 1])/len(omega)
    inner_code = inspect.getsource(f)
    print(inner_code)

def classical_probability_2():
    """ Независимо друг """
    def f():
        1 - 11 * 10 * 9 * 8 / 11 ** 4 # 4 чела, 11 вагонов
    inner_code = inspect.getsource(f)
    print(inner_code)

def geometric_probability_1():
    """ Двое договорились """
    def f():
        import numpy as np
        all_area = 60 * 60 
        bad_area = 36 * 36
        good_area = all_area - bad_area
        p = good_area / all_area
        print(f"Вероятность встречи: {p:.3f}")
    inner_code = inspect.getsource(f)
    print(inner_code)

def geometric_probability_2():
    """ В круг """
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
    """ События 2 """
    def f():
        # независимы
        P_A = 0.1
        P_B = 0.6
        P_C = 0.9
        P_BorC = P_B + P_C - P_C * P_B
        print(P_A * P_B + P_B * P_C + P_A * P_C - 2 * P_A * P_B * P_C)
        print(P_BorC)
    inner_code = inspect.getsource(f)
    print(inner_code)

def formulas_bayes_1():
    """ Имеется две 1 """
    def f():
        f_w = 13
        f_b = 15
        s_w = 17
        s_b = 20
        p_f_w = f_w / (f_w + f_b)
        p_s_w = s_w / (s_w + s_b)
        print(p_f_w, p_s_w)
        print("P(H | A) = P(A | H) * P(H) / P(A)")
        print((p_f_w * 5 + p_s_w * 10)/15)
        print(1/3 * p_f_w / ((p_f_w * 5 + p_s_w * 10)/15))
    inner_code = inspect.getsource(f)
    print(inner_code)

def formulas_bayes_2():
    """ Имеется две 2 """
    def f():
        # c n u p
        E1 = 7 * 0.3
        E2 = 5 * 0.5
        p_f_w = E1 / 12 # мат ожидание делить на кол-во всех
        p_s_w = E2 / 6
        p_f_w, p_s_w
        E3 = E1 + E2
        p_t_w = E3/18
        print(p_t_w)
        print("P(H|A) = P(A|H) * P(H) / P(A)")
        P_AH = p_f_w
        P_A = p_t_w
        P_H = 2/3
        P_HA = P_AH * P_H / P_A
        print(P_HA)
    inner_code = inspect.getsource(f)
    print(inner_code)

def discrete_random_1():
    """ События 1 """
    def f():
        # Имеют вероятности
        P_A = 0.1
        P_B = 0.4
        P_C = 0.3
        EU = 3 * P_A + 7 * P_B + 2 * P_C
        print(EU)
        Var_X = P_A * (1-P_A)
        Var_Y = P_B * (1-P_B)
        Var_Z = P_C * (1-P_C)
        Var_U = 9 * Var_X + 49 * Var_Y + 4 * Var_Z
        print(Var_U)
    inner_code = inspect.getsource(f)
    print(inner_code)
    
def discrete_random_2():
    """ Случайная величина 2"""
    def f():
        X_values = np.arange(1, 41) #
        Y_values = np.abs(X_values - 17.5) #
        unique_Y, counts = np.unique(Y_values, return_counts=True)
        prob_Y = counts / 40 #
        Y = rv_discrete(name='Y', values=(unique_Y, prob_Y))
        Q1min = Y.ppf(0.25) #
        Q3min = Y.ppf(0.75) #
        P_geq = Y.sf(unique_Y) + Y.pmf(unique_Y)
        Q1max = unique_Y[P_geq >= 0.75].max() # 
        Q3max = unique_Y[P_geq >= 0.25].max() #
        round(Q1min, 1), round(Q1max, 1), round(Q3min, 1), round(Q3max, 1)
    inner_code = inspect.getsource(f)
    print(inner_code)

def discrete_random_3():
    """ Распределение случайной """
    def f():
        values = np.array([2, 6, 9, 13, 15])
        p = np.array([0.1, 0.2, 0.2, 0.3, 0.2])
        X = rv_discrete(name='X', values=(values, p))
        E_X = X.expect()
        E_Y = X.expect(lambda x: np.abs(x - 10))
        E_XY = X.expect(lambda x: x * np.abs(x - 10))
        Var_X = X.var()
        Var_Y = X.expect(lambda x: np.abs(x - 10)**2) - E_Y**2
        round(E_X, 1), round(E_Y, 1), round(E_XY, 1), round(Var_X, 2), round(Var_Y, 2)
    inner_code = inspect.getsource(f)
    print(inner_code)

def special_discrete_1():
    """ Корзина содержит 1"""
    def f():
        all_balls = 63  # общее количество шаров
        red = 18  # количество красных шаров
        blue = 6   # количество синих шаров
        taken = 24  # количество извлечённых шаров
        cov_xy = -taken * red * (blue / all_balls ** 2) * (all_balls - taken) / (all_balls - 1)
        print(round(cov_xy, 2))
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
        prob_X7 = poisson.pmf(7, total) # 
        most_val = int(total)
        std = round(np.sqrt(total), 3)
        asymm = 1 / std
        excess = 1 / total
        round(prob_X7, 3), most_val, round(std, 3), round(asymm, 3), round(excess, 3)
    inner_code = inspect.getsource(f)
    print(inner_code)

def continuous_random_1():
    """ Случайная величина 1"""
    def f():
        # равномерно распределена
        from scipy.integrate import quad
        from scipy.stats import uniform

        X = uniform(loc=5, scale=2)

        def Y(x):
            return (1 + 6 * x ** 0.5 + 3 * x ** 0.7 + 8 * x ** 0.9)**1.1
        def Y2(x):
            return (1 + 6 * x ** 0.5 + 3 * x ** 0.7 + 8 * x ** 0.9)**2.2
        EY = quad(Y, 5, 7)[0]/2

        print(EY)
        EY2 = quad(Y2, 5,7)[0]/2
        Var_Y = EY2 - EY**2
        sigma_Y = Var_Y ** 0.5
        print(sigma_Y)
        def Y_EY_3(x):
            return (Y(x) - EY) ** 3

        EY_EY_3 = quad(Y_EY_3, 5, 7)[0] / 2
        As_Y = EY_EY_3 / (sigma_Y ** 3)
        print(As_Y)
        print(X.ppf(0.8))

    inner_code = inspect.getsource(f)
    print(inner_code)

def continuous_random_2():
    """ Абсолютно непрерывная """
    def f():
        from scipy.integrate import quad
        from scipy.stats import rv_continuous
        def func(x):
            return (1 + 2*x ** 0.5 + 3*x ** 0.7 + 7*x ** 0.9) ** 1.5
        a, b = (5, 7)
        def f(x):
            if (a <= x <= b):
                return func(x)
            return 0
        C = 1 / quad(f, a, b)[0]
        print(f'{C:.5f}')
        def EX(x):
            if (a <= x <= b):
                return C * x * func(x)
            return 0
        E_X = quad(EX, a, b)[0]
        print(f'{E_X:.3f}')
        def Var(x):
            if (a <= x <= b):
                return C * (x - E_X) ** 2 * func(x)
            return 0
        std_X = np.sqrt(quad(Var, a, b)[0])
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
    """ Доход по типовому """
    def f():
        EX = 5 * 0.2 + 9 * 0.2 + 10 * 0.3 + 11 * 0.1 + 8 * 0.2
        print(EX)
        EX2 = 25 * 0.2 + 64 * 0.2 + 81 * 0.2 + 100 * 0.3 +121 *0.1
        Var_X = EX2 - EX**2 
        print(Var_X/9)
    inner_code = inspect.getsource(f)
    print(inner_code)

def independent_dsv_2():
    """ Вероятность повышения """
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
    """ Игрок начал """
    def f():
        values = [1.05, 1.003, 0.99]
        probs = [0.1, 0.4, 0.5]
        X = rv_discrete(name='X', values=(values, probs))
        X2 = rv_discrete(name='X2', values=([el ** 2 for el in values], probs))
        S0 = 1000
        n = 150
        ES_150 = S0 * X.mean() ** n
        print(round(ES_150, 2))
        VarS_150 = S0 ** 2 * ((X2.mean()) ** n - X.mean() ** (2 * n))
        print(round(sqrt(VarS_150), 2))
    inner_code = inspect.getsource(f)
    print(inner_code)

def dependent_dsv_1():
    """ Случайные велечины """
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
    """ Корзина содержит 2 """
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
    """ Корзина содержит 3 """
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
    """ Дано совместное """
    def f():
        EX3 = 3 * 0.33
        EX5 = 5 * 0.15
        EX8 = 8 * 0.52
        EX = EX3 + EX5 + EX8
        print(EX)
        Var_X = 9*0.33 + 25 *0.15 + 64 * 0.52 - EX**2
        print(Var_X)
        EY9 = 0.57 * 9
        EY10 = 0.43 * 10
        EY = EY9 + EY10
        print(EY)
        Var_Y = 81 * 0.57 + 100 * 0.43 - EY**2
        print(Var_Y)
        EXY = 27 * 0.24 + 45 * 0.04 + 72 * 0.29 + 30* 0.09 + 0.11 * 50 + 80 * 0.23
        print(EXY)
        Cov_XY = EXY - EX*EY
        print(Cov_XY)
        Corr_XY = Cov_XY / (Var_X ** 0.5 * Var_Y ** 0.5)
        print(Corr_XY)
    inner_code = inspect.getsource(f)
    print(inner_code)

def discrete_vectors_2():
    """ Распределение дискретного """
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
    """ Распределение дискретного """
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


def discrete_vectors_5():
    """ Распределение дискретного """
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
    """ Распределение дискретного """
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
    """ Внутри квадрата"""
    def f():
        tri_area = 44
        cir_area = 40
        all_area = 100
        per_area = 20
        P_X = tri_area/all_area
        P_Y = cir_area/all_area
        P_PER = per_area/all_area

        P_Z0 = 1 - P_X - P_Y + P_PER
        P_Z1 = (P_X - P_PER) + (P_Y - P_PER)
        P_Z2 = P_PER

        EZ = 0 * P_Z0 + 1 * P_Z1 + 2 * P_Z2
        E2Z = 0 * P_Z0 + 1 * P_Z1 + 4 * P_Z2
        Var_Z = E2Z - EZ**2
        EU = 3 * EZ
        Var_U = 3 * Var_Z
        print(EU, Var_U)
        EV = EZ ** 3 
        EV2 = E2Z**3
        Var_V = EV2 - EV**2
        print(EV, Var_V)
    inner_code = inspect.getsource(f)
    print(inner_code)

def normal_vectors_1():
    """ Случайный вектор """
    def f():
        from sympy import Matrix

        A = Matrix([[20,24],
                    [24, 45]])

        A.inv()
        corr = -2/27 / ((5/36)**0.5 * (5/81)**0.5)
        print(corr)
    inner_code = inspect.getsource(f)
    print(inner_code)

def tablichka():
    """ Таблица """
    def f():
        P1 = 0.3 + 0.04 + 0.3
        print(P1)
        P2 = 0.16 + 0.09 + 0.11
        print(P2)
        E3 = (2 * 0.3 + 4 * 0.04 + 7 * 0.3) / P1
        print(E3)
        E4 = (2 * 0.16 + 4 * 0.09 + 7 * 0.11) / P2
        print(E4)
        E5 = EX = 2 * 0.46 + 4 * 0.13 + 7 * 0.41
        print(E5)
    inner_code = inspect.getsource(f)
    print(inner_code)

def normal_vectors_2():
    """ Для нормального 2 """
    def f():
        # для трех скобок
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
    """ Для нормального 1 """
    def f():
        # для двух скобок
        EX = -7
        EY = 17
        Var_X = 81
        Var_Y = 16
        Corr_XY = 0.6
        Cov_XY = Corr_XY*(Var_X**0.5 * Var_Y**0.5)
        Cov_Matrix = [[Var_X, Cov_XY], [Cov_XY, Var_Y]]
        mvn = multivariate_normal(mean=[EX, EY], cov=Cov_Matrix)
        X = norm(loc=EX, scale=Var_X**0.5)
        Y = norm(loc=EY, scale=Var_Y**0.5)
        print(X.cdf(4) + Y.cdf(3) - 2 * mvn.cdf([4,3]))
    inner_code = inspect.getsource(f)
    print(inner_code)

def conditional_sv_1():
    """ Максимальный ущерб """
    def f():
        from scipy.stats import uniform
        X = uniform(loc=0, scale=3.4)
        print(X.mean() * 16/5)
        print((16/5 * X.var() + 16/5 * (X.mean())**2)**0.5)
    inner_code = inspect.getsource(f)
    print(inner_code)

def conditional_sv_2():
    """ В первом броске 1 """
    def f():
        # 1) математическое ожидание условной дисперсии
        # 2) дисперсию условного математического ожидания относительно числа орлов
        n = 115
        p = 0.4
        E_X = n * p
        E_D_Y_given_X = (1 - p) * p * E_X
        D_X = n * p * (1 - p)
        D_E_Y_given_X = p**2 * D_X
        print(f"1) {E_D_Y_given_X:.4f}")
        print(f"2) {D_E_Y_given_X:.4f}")
    inner_code = inspect.getsource(f)
    print(inner_code)

def conditional_sv_3():
    """ В первом броске 2 """
    def f():
        # 1) Математическое ожидание числа
        # 2) Мат. ожидание условной дисперсии
        n = 56
        p = 0.6
        E_Y = n * p * p
        E_conditional_variance = n * p * p * (1 - p)
        print(f"1) {E_Y:.3f}")
        print(f"2) {E_conditional_variance:.4f}")
    inner_code = inspect.getsource(f)
    print(inner_code)

def conditional_sv_4():
    """ В первом броске 3 """
    def f():
        # 1) Математическое ожидание
        # 2) Дисперсия условного математического ожидания
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
    """ Для случайной """
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
    """ Игральная кость """
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


def portfolio_analysis_1():
    """ Математическое ожидание """
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
    """ Инвестор сформировал """
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
    """ Ожидаемая доходность """
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
    """ В области ограниченной """
    def f():
        from scipy.stats import uniform
        from scipy.spatial.distance import euclidean
        def set_point():
            while True:
                u = uniform.rvs(loc=-13, scale=26)
                v = uniform.rvs(loc=-9, scale=18)
                if (u/13)**2 + (v/9)**2 <= 1:
                    return [u, v]
        n = 100_000
        count_dots_AandB = count_dots_B = 0
        for _ in range(n):
            point1 = set_point()
            point2 = set_point()
            if euclidean(point1, point2) < 5.2 and all(all(coord < 0 for coord in point) for point in [point1, point2]):
                count_dots_AandB += 1
            if point1[0] < 0 and all(all(coord < 0 for coord in point) for point in [point1, point2]):
                count_dots_B += 1

        print(f"{(count_dots_AandB/count_dots_B):.1f}")
    inner_code = inspect.getsource(f)
    print(inner_code)

def monte_carlo_2():
    """ В прямоугольной области """
    def f():
        from scipy.stats import uniform
        from scipy.spatial import distance
        def set_point():
            x = uniform.rvs(loc=-20, scale=40)
            y = uniform.rvs(loc=-12, scale=24)
            return [x,y]
        n = 100_000
        c_A = 0
        for _ in range (n):
            p1 = set_point()
            p2 = set_point()
            if  distance.euclidean(p1, p2) < 6.4:
                c_A += 1

        print(f"{(c_A/n):.1f}")
        c_AandB = 0
        c_B= 0
        for _ in range(n):
            p1 = set_point()
            p2 = set_point()
            c_AandB += distance.euclidean(p1, p2) < 6.4 and np.abs(p1[0] - p2[0]) < 14
            c_B += np.abs(p1[0] - p2[0]) < 14
        print(f"{(c_AandB/c_B):.1f}")
    inner_code = inspect.getsource(f)
    print(inner_code)

def monte_carlo_3():
    """ В кубе объема """
    def f():
        from scipy.stats import uniform
        from scipy.spatial import distance

        def point():
            x, y, z = uniform.rvs(loc=0, scale=3), uniform.rvs(loc=0, scale=3), uniform.rvs(loc=0, scale=3)
            return x, y, z
        n = 100_000
        c_RT = c_ST = 0
        count_T = 0
        def R(angls):
            return np.any(angls<35.6)

        def S(angls):
            return np.all(angls<68.4)

        def T(angls):
            return np.all(angls<90)

        while count_T < n:
            A = point()
            B = point()
            C = point()
            c = distance.euclidean(A, B)
            b = distance.euclidean(A, C)
            a = distance.euclidean(B, C)
            if (a + b > c) & (a + c > b) & (b + c > a):
                angles = np.degrees(np.arccos([(b**2 + c**2 - a**2)/(2*b*c),
                                            (a**2 + c**2 - b**2)/(2*a*c),
                                            (b**2 + a**2 - c**2)/(2*a*b)]))
                if T(angles):
                    count_T += 1
                    if R(angles):
                        c_RT += 1
                    if S(angles):
                        c_ST += 1

        c_RT/n, c_ST/n
    inner_code = inspect.getsource(f)
    print(inner_code)

def v(search_string):
    current_module = globals()
    found_functions = []
    
    for name, obj in current_module.items():
        if inspect.isfunction(obj) and obj.__doc__:
            if search_string.lower() in obj.__doc__.lower():
                found_functions.append((name, obj))
    
    if len(found_functions) == 0:
        print(404.0)
        return False
    elif len(found_functions) > 1:
        print(".")
    
    # Берем первый найденный результат
    _, obj = found_functions[0]
    # Перехватываем вывод print
    old_stdout = sys.stdout
    sys.stdout = buffer = io.StringIO()
    
    try:
        # Вызываем функцию
        obj()
        # Получаем вывод
        output = buffer.getvalue()
        # Извлекаем код функции f из вывода
        lines = output.split('\n')
        f_code_lines = []
        capture = False
        
        for line in lines:
            if 'def f():' in line:
                capture = True
                continue
            if capture:
                if line.strip() and not line.startswith('    '):
                    break
                if line.strip():
                    f_code_lines.append(line[8:])  # Убираем отступ
        
        code_to_copy = '\n'.join(f_code_lines)
        pyperclip.copy(code_to_copy)
        return True
        
    finally:
        sys.stdout = old_stdout


def z(search_string):
    current_module = globals()
    found_functions = []
    
    for name, obj in current_module.items():
        if inspect.isfunction(obj) and obj.__doc__:
            if search_string.lower() in obj.__doc__.lower():
                found_functions.append((name, obj))
    
    if len(found_functions) == 0:
        return None
    elif len(found_functions) > 1:
        print(".")
    
    # Возвращаем первый найденный результат
    _, obj = found_functions[0]
    return obj