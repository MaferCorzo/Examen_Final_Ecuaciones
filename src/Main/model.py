import sympy as sp
import numpy as np
from sympy.utilities.lambdify import lambdify


# w = velocidad angular
# v = velocidad inicial
# k = coeficiente que determina el comportamiento de v respecto al torque
# c = coeficiente que determina el comportamiento de w respecto al torque
def torque_constante(w, v):
    return 0  # El torque se ajusta a una constante específica


"---------------------------------------------------------------------------------"


def torque_lineal(w, v):
    k, c = sp.symbols("k c")
    return -k * v - c * w  # relación lineal entre el torque y las variables v y w


"---------------------------------------------------------------------------------"


def torque_cuadratico(w, v):
    k, c = sp.symbols("k c")
    return -k * v**2 - c * w  # el torque depende cuadraticamente de v


"---------------------------------------------------------------------------------"


def torque_cubico(w, v):
    k, c = sp.symbols("k c")
    return -k * v**3 - c * w  # el torque depende cubicamente de la variable v


"---------------------------------------------------------------------------------"


def torque_funcion(tipo_torque, w, v):
    print("Tipo de torque recibido:", tipo_torque)
    if tipo_torque == "constante":
        return torque_constante(w, v)
    elif tipo_torque == "lineal":
        return torque_lineal(w, v)
    elif tipo_torque == "cuadratico":
        return torque_cuadratico(w, v)
    elif tipo_torque == "cubico":
        return torque_cubico(w, v)
    else:
        raise ValueError("Tipo de torque no soportado.")


"---------------------------------------------------------------------------------"


class ModelMath:
    # I = Momento de inercia
    # r = radio
    # θ = posición angular
    # w = velocidad angular

    def __init__(self, I, r):
        self.I = I
        self.r = r

    def ecuacion_diferencial_ordinaria(self, θ, w):
        t = sp.symbols("t")  # t = tiempo
        theta = sp.Function("theta")(t)  # theta(t) =  posicion angular respecto a t
        omega = sp.diff(
            theta, t
        )  # derivada de theta con respecto a t para obtener velocidad angular (omega(t))

        # Ecuacion diferencial ordinaria:
        eq = sp.Eq(
            self.I * sp.diff(theta, t, t),
            torque_funcion("constante", omega, self.r * omega),
        )  # torque constante
        ci = {
            theta.subs(t, 0): θ,
            sp.diff(theta, t).subs(t, 0): w,
        }  # posición angular inicial θ se asigna a theta(0) y velocidad angula w se asigna a la derivada de theta(t) en t=0
        sol = sp.dsolve(
            eq, theta, ci=ci
        )  # solucion de la ED eq con respecto a theta teniendo en cuenta las condiciones ci

        theta_sol = sol.rhs  # extracción para expresión de theta

        # Convertir la expresión simbólica en una función numérica
        theta_func = lambdify(t, theta_sol, modules="numpy")

        # Generar valores de tiempo utilizando np.linspace
        t_valores = np.linspace(0, 10, 400)

        # Evaluar la función numérica en los valores de tiempo
        theta_valores = theta_func(t_valores)

        return t_valores, theta_valores

    def ecuacion_diferencial_lineal(self, θ, w):
        t = sp.symbols("t")  # t = tiempo
        theta = sp.Function("theta")(t)  # theta(t) =  posicion angular respecto a t
        omega = sp.diff(
            theta, t
        )  # derivada de theta con respecto a t para obtener velocidad angular (omega(t))

        # Ecuacion diferencial lineal:
        k, c = sp.symbols("k c")
        torque = -k * omega - c * omega  # torque lineal: -k * v - c * w
        eq = sp.Eq(self.I * sp.diff(theta, t, t), torque)
        ci = {
            theta.subs(t, 0): θ,
            sp.diff(theta, t).subs(t, 0): w,
        }  # posición angular inicial θ se asigna a theta(0) y velocidad angular w se asigna a la derivada de theta(t) en t=0
        sol = sp.dsolve(
            eq, theta, ci=ci
        )  # solucion de la ED eq con respecto a theta teniendo en cuenta las condiciones ci

        theta_sol = sol.rhs  # extracción para expresión de theta

        # Convertir la expresión simbólica en una función numérica
        theta_func = lambdify(t, theta_sol, modules="numpy")

        # Generar valores de tiempo utilizando np.linspace
        t_valores = np.linspace(0, 10, 400)

        # Evaluar la función numérica en los valores de tiempo
        theta_valores = theta_func(t_valores)

        return t_valores, theta_valores

    def ecuacion_diferencial_no_lineal(self, θ, w, tipo_torque, m):
        t = sp.symbols("t")
        theta = sp.Function("theta")(t)
        omega = sp.diff(theta, t)
        alpha = sp.diff(omega, t)

        if tipo_torque == "cuadratico":
            k, c = sp.symbols("k c")
            torque = -k * omega**2 - c * omega
            eq = sp.Eq(self.I * alpha, torque + m * theta**3)
        elif tipo_torque == "cubico":
            k, c = sp.symbols("k c")
            torque = -k * omega**3 - c * omega
            eq = sp.Eq(self.I * alpha, torque + m * theta**3)
        else:
            raise ValueError(
                "Tipo de torque no válido para ecuación diferencial no lineal."
            )

        ci = {theta.subs(t, 0): θ, omega.subs(t, 0): w}
        sol = sp.dsolve(eq, theta, ics=ci)

        theta_sol = sol.rhs

        theta_func = lambdify(t, theta_sol, modules="numpy")
        t_valores = np.linspace(0, 10, 400)
        theta_valores = theta_func(t_valores)

        return t_valores, theta_valores
