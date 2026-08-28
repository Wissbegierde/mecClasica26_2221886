"""
Verificación numérica de leyes de conservación para sistemas con simetrías
Parte E: Investigación de conservación de energía y momento angular

Sistema: Partícula 2D con potencial V = 0.5*k*r² + λ*W(x,y)
Casos:
    (i)   W = (x² + y²)² - Simetría rotacional continua, L_z conservado
    (ii)  W = x²y² - Simetría discreta, L_z NO conservado

Integradores: Verlet de velocidades y Runge-Kutta 4
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint
import json
from pathlib import Path

# ==============================================================================
# PARÁMETROS DEL SISTEMA
# ==============================================================================

k = 1.0          # Constante del oscilador armónico
m = 1.0          # Masa
Omega = np.sqrt(k/m)  # Frecuencia natural

# Parámetro de perturbación: variaremos λ desde 0 hasta detectar efectos
lambda_values = np.logspace(-3, -0.5, 5)  # λ ∈ [0.001, 0.316]

# Paso de integración: variaremos h para análisis de convergencia
h_values = np.logspace(-3, -0.1, 8)  # h ∈ [0.001, 0.794]

# Condiciones iniciales
x0, y0 = 1.0, 0.5
vx0, vy0 = 0.0, 1.0
t_final = 100.0  # Tiempo de integración

# ==============================================================================
# DEFINICIÓN DE FUNCIONES DE POTENCIAL Y FUERZAS
# ==============================================================================

def W_case_i(x, y):
    """Caso (i): W = (x² + y²)²"""
    r2 = x**2 + y**2
    return r2**2

def dW_dx_case_i(x, y):
    """dW/dx para caso (i)"""
    r2 = x**2 + y**2
    return 4*x*r2

def dW_dy_case_i(x, y):
    """dW/dy para caso (i)"""
    r2 = x**2 + y**2
    return 4*y*r2

def W_case_ii(x, y):
    """Caso (ii): W = x²y²"""
    return (x*y)**2

def dW_dx_case_ii(x, y):
    """dW/dx para caso (ii)"""
    return 2*x*y**2

def dW_dy_case_ii(x, y):
    """dW/dy para caso (ii)"""
    return 2*x**2*y

# Diccionario de funciones
potentials = {
    'case_i': {
        'W': W_case_i,
        'dW_dx': dW_dx_case_i,
        'dW_dy': dW_dy_case_i,
        'name': r'$W = (x^2 + y^2)^2$'
    },
    'case_ii': {
        'W': W_case_ii,
        'dW_dx': dW_dx_case_ii,
        'dW_dy': dW_dy_case_ii,
        'name': r'$W = x^2y^2$'
    }
}

# ==============================================================================
# FUNCIONES DE CONSERVACIÓN
# ==============================================================================

def energia(x, y, vx, vy, lam, case):
    """Energía total E = KE + PE"""
    KE = 0.5*m*(vx**2 + vy**2)
    PE = 0.5*k*(x**2 + y**2) + lam*potentials[case]['W'](x, y)
    return KE + PE

def momento_angular_z(x, y, vx, vy):
    """Momento angular L_z = m(x*vy - y*vx)"""
    return m*(x*vy - y*vx)

# ==============================================================================
# INTEGRADOR: VERLET DE VELOCIDADES
# ==============================================================================

def verlet_velocities(h, t_final, case, lam):
    """
    Integra usando Verlet de velocidades
    Retorna: t, x, y, vx, vy, E, L_z
    """
    n_steps = int(t_final / h)

    # Inicialización
    t = np.zeros(n_steps)
    x = np.zeros(n_steps)
    y = np.zeros(n_steps)
    vx = np.zeros(n_steps)
    vy = np.zeros(n_steps)
    E = np.zeros(n_steps)
    Lz = np.zeros(n_steps)

    x[0], y[0] = x0, y0
    vx[0], vy[0] = vx0, vy0

    dW_dx = potentials[case]['dW_dx']
    dW_dy = potentials[case]['dW_dy']

    # Aceleraciones en t=0
    ax = -(Omega**2)*x[0] - (lam/m)*dW_dx(x[0], y[0])
    ay = -(Omega**2)*y[0] - (lam/m)*dW_dy(x[0], y[0])

    E[0] = energia(x[0], y[0], vx[0], vy[0], lam, case)
    Lz[0] = momento_angular_z(x[0], y[0], vx[0], vy[0])

    # Loop de integración
    for i in range(1, n_steps):
        t[i] = i*h

        # Verlet: actualiza posición
        x_new = x[i-1] + h*vx[i-1] + 0.5*h**2*ax
        y_new = y[i-1] + h*vy[i-1] + 0.5*h**2*ay

        # Aceleración en nueva posición
        ax_new = -(Omega**2)*x_new - (lam/m)*dW_dx(x_new, y_new)
        ay_new = -(Omega**2)*y_new - (lam/m)*dW_dy(x_new, y_new)

        # Actualiza velocidad
        vx_new = vx[i-1] + 0.5*h*(ax + ax_new)
        vy_new = vy[i-1] + 0.5*h*(ay + ay_new)

        x[i], y[i] = x_new, y_new
        vx[i], vy[i] = vx_new, vy_new
        ax, ay = ax_new, ay_new

        E[i] = energia(x[i], y[i], vx[i], vy[i], lam, case)
        Lz[i] = momento_angular_z(x[i], y[i], vx[i], vy[i])

    return t, x, y, vx, vy, E, Lz

# ==============================================================================
# INTEGRADOR: RUNGE-KUTTA 4
# ==============================================================================

def rk4_system(state, case, lam):
    """Derivadas para RK4: [x, y, vx, vy]"""
    x, y, vx, vy = state
    dW_dx = potentials[case]['dW_dx']
    dW_dy = potentials[case]['dW_dy']

    ax = -(Omega**2)*x - (lam/m)*dW_dx(x, y)
    ay = -(Omega**2)*y - (lam/m)*dW_dy(x, y)

    return np.array([vx, vy, ax, ay])

def rk4(h, t_final, case, lam):
    """
    Integra usando Runge-Kutta 4
    Retorna: t, x, y, vx, vy, E, L_z
    """
    n_steps = int(t_final / h)

    t = np.zeros(n_steps)
    state_history = np.zeros((n_steps, 4))
    E = np.zeros(n_steps)
    Lz = np.zeros(n_steps)

    state = np.array([x0, y0, vx0, vy0])
    state_history[0] = state

    x, y, vx, vy = state
    E[0] = energia(x, y, vx, vy, lam, case)
    Lz[0] = momento_angular_z(x, y, vx, vy)

    for i in range(1, n_steps):
        t[i] = i*h

        k1 = rk4_system(state, case, lam)
        k2 = rk4_system(state + 0.5*h*k1, case, lam)
        k3 = rk4_system(state + 0.5*h*k2, case, lam)
        k4 = rk4_system(state + h*k3, case, lam)

        state = state + (h/6.0)*(k1 + 2*k2 + 2*k3 + k4)
        state_history[i] = state

        x, y, vx, vy = state
        E[i] = energia(x, y, vx, vy, lam, case)
        Lz[i] = momento_angular_z(x, y, vx, vy)

    x = state_history[:, 0]
    y = state_history[:, 1]
    vx = state_history[:, 2]
    vy = state_history[:, 3]

    return t, x, y, vx, vy, E, Lz

# ==============================================================================
# ANÁLISIS DE CONVERGENCIA: VARIACIÓN DE h
# ==============================================================================

def convergence_analysis(case, lam_fixed=0.1):
    """
    Análisis de convergencia variando el paso h
    Retorna: h_values, max_dE_verlet, max_dLz_verlet, max_dE_rk4, max_dLz_rk4
    """
    max_dE_verlet = []
    max_dLz_verlet = []
    max_dE_rk4 = []
    max_dLz_rk4 = []

    print(f"\n{'='*70}")
    print(f"CONVERGENCIA - Caso: {potentials[case]['name']}, lam = {lam_fixed}")
    print(f"{'='*70}")

    for h in h_values:
        print(f"  h = {h:.4f}...", end="", flush=True)

        # Verlet
        t, x, y, vx, vy, E, Lz = verlet_velocities(h, t_final, case, lam_fixed)
        dE = np.abs(E - E[0])
        dLz = np.abs(Lz - Lz[0])
        max_dE_verlet.append(np.max(dE))
        max_dLz_verlet.append(np.max(dLz))

        # RK4
        t, x, y, vx, vy, E, Lz = rk4(h, t_final, case, lam_fixed)
        dE = np.abs(E - E[0])
        dLz = np.abs(Lz - Lz[0])
        max_dE_rk4.append(np.max(dE))
        max_dLz_rk4.append(np.max(dLz))

        print(f" [OK]")

    return max_dE_verlet, max_dLz_verlet, max_dE_rk4, max_dLz_rk4

# ==============================================================================
# EJECUCIÓN PRINCIPAL
# ==============================================================================

results = {}

for case in ['case_i', 'case_ii']:
    print(f"\n\n{'#'*70}")
    print(f"# CASO {case.upper()}: {potentials[case]['name']}")
    print(f"{'#'*70}")

    max_dE_v, max_dLz_v, max_dE_r, max_dLz_r = convergence_analysis(case, lam_fixed=0.1)

    results[case] = {
        'h_values': h_values.tolist(),
        'max_dE_verlet': max_dE_v,
        'max_dLz_verlet': max_dLz_v,
        'max_dE_rk4': max_dE_r,
        'max_dLz_rk4': max_dLz_r
    }

# ==============================================================================
# GENERACIÓN DE GRÁFICAS LOG-LOG
# ==============================================================================

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('Verificación Numérica: Convergencia en Conservación de E y $L_z$',
             fontsize=14, fontweight='bold')

cases_list = ['case_i', 'case_ii']
case_labels = [r'Caso (i): $W = (x^2+y^2)^2$ - Simetría $SO(2)$, $L_z$ conservado',
               r'Caso (ii): $W = x^2y^2$ - Simetría discreta, $L_z$ no conservado']

for idx, case in enumerate(cases_list):
    h_vals = np.array(results[case]['h_values'])

    # Subplot: Energía
    ax = axes[idx, 0]
    ax.loglog(h_vals, results[case]['max_dE_verlet'], 'o-', linewidth=2,
              markersize=6, label='Verlet (orden 2)', color='#1f77b4')
    ax.loglog(h_vals, results[case]['max_dE_rk4'], 's-', linewidth=2,
              markersize=6, label='RK4 (orden 4)', color='#ff7f0e')

    # Líneas de referencia para órdenes de convergencia
    h_ref = h_vals[len(h_vals)//2]
    y_ref = results[case]['max_dE_verlet'][len(h_vals)//2]
    ax.loglog(h_vals, y_ref * (h_vals/h_ref)**2, '--', alpha=0.5,
              color='#1f77b4', label=r'$\propto h^2$')
    ax.loglog(h_vals, y_ref * (h_vals/h_ref)**4 / (h_ref**2), '--', alpha=0.5,
              color='#ff7f0e', label=r'$\propto h^4$')

    ax.set_xlabel(r'Paso temporal $h$', fontsize=11)
    ax.set_ylabel(r'$\max|\Delta E|$', fontsize=11)
    ax.set_title(case_labels[idx] + '\n(Energía)', fontsize=10)
    ax.legend(fontsize=9, loc='best')
    ax.grid(True, alpha=0.3, which='both')

    # Subplot: Momento angular
    ax = axes[idx, 1]
    ax.loglog(h_vals, results[case]['max_dLz_verlet'], 'o-', linewidth=2,
              markersize=6, label='Verlet', color='#1f77b4')
    ax.loglog(h_vals, results[case]['max_dLz_rk4'], 's-', linewidth=2,
              markersize=6, label='RK4', color='#ff7f0e')

    h_ref = h_vals[len(h_vals)//2]
    y_ref = results[case]['max_dLz_verlet'][len(h_vals)//2]
    ax.loglog(h_vals, y_ref * (h_vals/h_ref)**2, '--', alpha=0.5,
              color='#1f77b4', label=r'$\propto h^2$')
    ax.loglog(h_vals, y_ref * (h_vals/h_ref)**4 / (h_ref**2), '--', alpha=0.5,
              color='#ff7f0e', label=r'$\propto h^4$')

    ax.set_xlabel(r'Paso temporal $h$', fontsize=11)
    ax.set_ylabel(r'$\max|\Delta L_z|$', fontsize=11)
    ax.set_title(case_labels[idx] + '\n(Momento Angular)', fontsize=10)
    ax.legend(fontsize=9, loc='best')
    ax.grid(True, alpha=0.3, which='both')

plt.tight_layout()
plt.savefig(r'C:\fisica\MecClasica26_2221886\codigos\verificacion_ley_conservacion\convergencia_log_log.png',
            dpi=300, bbox_inches='tight')
print("\n[OK] Gráfica guardada: convergencia_log_log.png")

plt.show()

# ==============================================================================
# GUARDADO DE RESULTADOS
# ==============================================================================

output_file = Path(r'C:\fisica\MecClasica26_2221886\codigos\verificacion_ley_conservacion\resultados.json')
with open(output_file, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\n[OK] Resultados guardados en: {output_file}")
print("\n" + "="*70)
print("EJECUCIÓN COMPLETADA")
print("="*70)
