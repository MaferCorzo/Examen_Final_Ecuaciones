from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QInputDialog
from PyQt5 import QtGui
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
from sympy.printing import latex
from main_window_ui import Ui_MainWindow
from model import ModelMath
from model import torque_funcion
from PyQt5.QtCore import Qt
from scipy.integrate import solve_ivp
from sympy import nsimplify


class Controller(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.tipo_torque.addItems(["Constante", "Lineal", "Cuadratico", "Cubico"])
        self.ui.ecuacion_diferencial.clicked.connect(self.definir_ecuacion_diferencial)
        self.ui.graficar.clicked.connect(self.graficar)
        
        

    def mostrar_resultado(self, imagen_path, mensaje_extra=""):
        # Mostrar el mensaje extra si está disponible
        if mensaje_extra:
            self.ui.img.setText(mensaje_extra)
            self.ui.img.adjustSize()  # Ajustar el tamaño del QLabel al texto
            self.ui.img.setStyleSheet("background: transparent; color: black;")

        # Cargar la imagen en el QLabel
        pixmap = QtGui.QPixmap(imagen_path)

        # Escalar la imagen para ajustarse al QLabel
        max_size = 400  # Establecer el tamaño máximo para la imagen
        scaled_pixmap = pixmap.scaledToWidth(max_size, Qt.SmoothTransformation)

        # Mostrar la imagen en el QLabel
        self.ui.img.setPixmap(scaled_pixmap)

        # No permitir que el QLabel cambie su tamaño
        self.ui.img.setFixedSize(scaled_pixmap.size())

    def mostrar_error(self, mensaje):
        QMessageBox.critical(self, "Error", mensaje)

    def generar_ecuacion_diferencial(self, tipo_torque, I, r, theta, omega):
        t = sp.symbols("t")
        k = sp.Symbol("k")
        c = sp.Symbol("c")

        # Validar las constantes k y c según el tipo de torque
        try:
            k_val = int(self.ui.coeficiente_k.text())
            c_val = int(self.ui.coeficiente_c.text())
        except ValueError:
            raise self.mostrar_error(
                "Los coeficientes k y c deben ser números enteros."
            )

        # Validar las constantes k y c según el tipo de torque
        if tipo_torque == "Constante":
            k_val = int(self.ui.coeficiente_k.text())
            c_val = int(self.ui.coeficiente_c.text())
            if k_val != 0 or c_val != 0:
                raise ValueError(
                    "Error: el torque constante no debe depender de la velocidad angular ni de la velocidad inicial, por lo que los coeficientes k y c deben ser ambos cero."
                )
            eq_general = sp.Eq(I * sp.diff(theta, t, t), 0)
        elif tipo_torque == "Lineal":
            k_val = int(self.ui.coeficiente_k.text())
            c_val = int(self.ui.coeficiente_c.text())
            if k_val == 0 or c_val == 0:
                raise ValueError(
                    "Error: El torque lineal no acepta valores de k y c iguales a 0."
                )
            eq_general = sp.Eq(I * sp.diff(theta, t, t), k_val * omega + c_val)

        elif tipo_torque.lower() == "cuadratico": ##usar libreria odeint
            if k_val == 0 or c_val == 0:
                raise ValueError(
                    "Error: El torque no lineal no acepta valores de k y c iguales a 0."
                )
            eq_general = sp.Eq(I * theta.diff(t, t), k * theta.diff(t) ** 2 + c * theta)
        elif tipo_torque.lower() == "cubico":
            if k_val == 0 or c_val == 0:
                raise ValueError(
                    "Error: El torque no lineal no acepta valores de k y c iguales a 0."
                )
            eq_general = sp.Eq(I * theta.diff(t, t), k * theta.diff(t) ** 3 + c * theta)
        else:
            raise ValueError(
                "Tipo de torque no válido para ecuación diferencial no lineal."
            )

        return eq_general

    def definir_ecuacion_diferencial(self):
        # Obtener valores de entrada
        tipo_torque = self.ui.tipo_torque.currentText()
        try:
            I = int(self.ui.inercia.text())
            r = int(self.ui.radio.text())
            theta_0 = int(self.ui.angulo_inicial.text())
            omega_0 = int(self.ui.velocidad_angular.text())
            k_val = int(self.ui.coeficiente_k.text())
            c_val = int(self.ui.coeficiente_c.text())
        except ValueError:
            self.mostrar_error(
                "Por favor ingrese valores numéricos válidos para Inercia, Radio, Ángulo Inicial y Velocidad Angular como enteros."
            )
            return

        t = sp.symbols("t")
        theta = sp.Function("theta")(t)
        omega = theta.diff(t)

        try:
            eq_general = self.generar_ecuacion_diferencial(tipo_torque, sp.Symbol("I"), r, theta, omega)
            if eq_general is None:
                return

            # Reemplazar los valores específicos en la ecuación general
            eq_reemplazada = eq_general.subs({sp.Symbol("I"): I, sp.Symbol("k"): k_val, sp.Symbol("c"): c_val})

            try:
                # Intentar resolver la ecuación diferencial de forma analítica
                sol = sp.dsolve(eq_reemplazada,theta,ics={theta.subs(t, 0): theta_0, omega.subs(t, 0): omega_0},)
                pasos_solucion = sp.simplify(sol)

                # Convertir las ecuaciones a LaTeX
                eq_general_latex = sp.latex(eq_general, mode="inline")
                eq_reemplazada_latex = sp.latex(eq_reemplazada, mode="inline")
                pasos_solucion_latex = sp.latex(pasos_solucion, mode="inline")

                # Mostrar ecuaciones en QLabel usando Matplotlib para generar imágenes
                fig, ax = plt.subplots(figsize=(8, 6))
                ax.axis("off")

                if tipo_torque.lower() == "constante":
                    ecuacion_general_texto = r"$\text{Ecuación general Ordinaria:}$"
                    eq_general =  r"$ I \cdot \frac{d^2\theta}{dt^2} = 0 $"
                elif tipo_torque.lower() == "lineal":
                    ecuacion_general_texto = r"$\text{Ecuación general Lineal:}$"
                    eq_general = r"$I \cdot \frac{d^2\theta}{dt^2} = k \cdot \omega + c$"    
                else:
                    ecuacion_general_texto = r"$\text{Ecuación general No Lineal:}$"
                    if tipo_torque=='cuadratico':
                        eq_general = r"$I \cdot \frac{d^2\theta}{dt^2} = k \cdot \left(\frac{d\theta}{dt}\right)^2 + c \cdot \theta$"
                    if tipo_torque=='cubico':
                        eq_general = r"$I \cdot \frac{d^2\theta}{dt^2} = k \cdot \left(\frac{d\theta}{dt}\right)^3 + c \cdot \theta$"
                        

                ax.text(
                0.5,
                0.9,
                ecuacion_general_texto,
                horizontalalignment="center",
                verticalalignment="top",
                fontsize=20,
                transform=ax.transAxes,
                )
                ax.text(
                0.5,
                0.8,
                eq_general,
                horizontalalignment="center",
                verticalalignment="top",
                fontsize=20,
                transform=ax.transAxes,
                )
                ax.text(
                0.5,
                0.6,
                r"$\text{Ecuación con valores reemplazados:}$",
                horizontalalignment="center",
                verticalalignment="top",
                fontsize=20,
                transform=ax.transAxes,
                )
                ax.text(
                0.5,
                0.5,
                eq_reemplazada_latex,
                horizontalalignment="center",
                verticalalignment="top",
                fontsize=20,
                transform=ax.transAxes,
                )
                ax.text(
                0.5,
                0.3,
                r"$\text{Solución:}$",
                horizontalalignment="center",
                verticalalignment="top",
                fontsize=20,
                transform=ax.transAxes,
                )
                ax.text(
                0.5,
                0.2,
                pasos_solucion_latex,
                horizontalalignment="center",
                verticalalignment="top",
                fontsize=20,
                transform=ax.transAxes,
                )

                plt.savefig(
                    "ecuacion_ordinaria.png",
                    bbox_inches="tight",
                    transparent=True,
                    dpi=300,
                )
                plt.close()

                self.mostrar_resultado("ecuacion_ordinaria.png", pasos_solucion_latex)
                self.pasos_solucion = pasos_solucion
            except Exception:
                eq_general_latex = sp.latex(eq_general, mode="inline")
                eq_reemplazada_latex = sp.latex(eq_reemplazada, mode="inline")
                solucion_texto = "Visualice mejor la solución en la gráfica"

                fig, ax = plt.subplots(figsize=(8, 6))
                ax.axis("off")   

                ax.text(
                    0.5,
                    0.9,
                    r"$\text{Ecuación general no lineal:}$",
                    horizontalalignment="center",
                    verticalalignment="top",
                    fontsize=20,
                    transform=ax.transAxes,
                )
                ax.text(
                    0.5,
                    0.8,
                    eq_general_latex,
                    horizontalalignment="center",
                    verticalalignment="top",
                    fontsize=20,
                    transform=ax.transAxes,
                )
                ax.text(
                    0.5,
                    0.6,
                    r"$\text{Ecuación con valores reemplazados:}$",
                    horizontalalignment="center",
                    verticalalignment="top",
                    fontsize=20,
                    transform=ax.transAxes,
                )
                ax.text(
                    0.5,
                    0.5,
                    eq_reemplazada_latex,
                    horizontalalignment="center",
                    verticalalignment="top",
                    fontsize=20,
                    transform=ax.transAxes,
                )
                ax.text(
                    0.5,
                    0.3,
                    r"$\text{Solución:}$",
                    horizontalalignment="center",
                    verticalalignment="top",
                    fontsize=20,
                    transform=ax.transAxes,
                )
                ax.text(
                    0.5,
                    0.2,
                    solucion_texto,
                    horizontalalignment="center",
                    verticalalignment="top",
                    fontsize=20,
                    transform=ax.transAxes,
                )

                plt.savefig("ecuacion_ordinaria.png", bbox_inches="tight", transparent=True, dpi=300)
                plt.close()

                self.mostrar_resultado("ecuacion_ordinaria.png", solucion_texto)
        except Exception as e:
            self.mostrar_error(f"Error al resolver la ecuación diferencial: {e}")
            print(e)

    def graficar(self):
        I = int(self.ui.inercia.text())
        r = int(self.ui.radio.text())
        k_val = int(self.ui.coeficiente_k.text())
        c_val = int(self.ui.coeficiente_c.text())
        if not hasattr(self, "pasos_solucion"):
            self.mostrar_error("Por favor, defina primero la ecuación diferencial.")
            return
        if isinstance(self.pasos_solucion, bool):
            self.mostrar_error(
                "Error: la solución de la ecuación diferencial no es válida."
            )
            return
        try:
            tipo_torque = self.ui.tipo_torque.currentText()
            t_span = (0, 10)  # Definir el rango de tiempo
            y0 = [int(self.ui.angulo_inicial.text()), int(self.ui.velocidad_angular.text())]
            if tipo_torque.lower() in ["cuadratico", "cubico"]:
                def ecuacion_diferencial(t, y):
                    theta, omega = y
                    
                    dtheta_dt = omega
                    domega_dt = (k_val * omega + c_val) / I
                    return [dtheta_dt, domega_dt]
                
                sol_numerica = solve_ivp(
                fun=ecuacion_diferencial,
                t_span=t_span,
                y0=y0,
                method='RK45'
                )

                theta_vals = sol_numerica.y[0]

                # Graficar la solución numérica
                plt.figure()
                plt.plot(sol_numerica.t, theta_vals, label='Theta(t)')
                plt.xlabel('Tiempo (t)')
                plt.ylabel('Posición Angular (θ)')
                plt.legend()
                plt.title('Dinámica del movimiento rotacional del ventilador')
                plt.grid(True)
                plt.savefig('solucion_grafica.png')
                plt.show()

            else:
                t_vals = sp.symbols("t_vals")
                t_vals = sp.lambdify(sp.symbols("t"), self.pasos_solucion.rhs, "numpy")
                t = np.linspace(0, 10, 400)
                theta_vals = t_vals(t)

                plt.figure()
                plt.plot(t, theta_vals, label="Theta(t)")
                plt.xlabel("Tiempo (t)")
                plt.ylabel("Posición Angular(θ)")
                plt.legend()
                plt.title("Dinámica del movimiento rotacional del ventilador.")
                plt.grid(True)
                plt.savefig("solucion_grafica.png")
                plt.show()
        except Exception as e:
            self.mostrar_error(f"Error al graficar la solución: {e}")
