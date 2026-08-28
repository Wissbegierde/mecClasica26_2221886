# Verificación Numérica de Ley de Conservación — Parte E

## Descripción General

Esta carpeta contiene el código necesario para verificar numéricamente las leyes de conservación en sistemas mecánicos estudiados en el ejercicio de consolidación: **Teorema de Noether y Cantidades Conservadas**.

Específicamente, se verifica la conservación del **momento angular** $p_\varphi$ y la **energía total** $E$ en el sistema de una partícula en un cono invertido bajo gravedad.

---

## Estructura del Proyecto

```
Verificacion_ley_conservacion/
├── README.md                          # Este archivo
├── VERSION.md                         # Control de versiones
├── cono_verificacion_conservacion.py  # Script principal
├── datos/
│   └── resultados_*.csv               # Archivos de datos generados
├── graficos/
│   ├── trayectoria_xy.png
│   ├── momento_angular_vs_tiempo.png
│   ├── energia_vs_tiempo.png
│   └── error_relativo.png
└── docs/
    └── metodologia.md                 # Detalles técnicos
```

---

## Requisitos

### Dependencias de Software
- **Python**: 3.8 o superior
- **NumPy**: Para cálculos numéricos
- **SciPy**: Integrador RK45
- **Matplotlib**: Visualización
- **Pandas**: Manejo de datos (opcional)

### Instalación de Dependencias

```bash
pip install numpy scipy matplotlib pandas
```

O usar el archivo `requirements.txt`:

```bash
pip install -r requirements.txt
```

### Especificaciones del Sistema
- RAM: ≥ 2 GB
- CPU: Procesador moderno (cualquiera)
- Disco: ≥ 100 MB de espacio libre

---

## Uso

### Ejecución Básica

```bash
python cono_verificacion_conservacion.py
```

### Parámetros Configurables

Dentro del script, es posible modificar:

```python
# Parámetros del sistema
alpha = np.radians(30)        # Ángulo del cono (radianes)
m = 1.0                        # Masa de la partícula (kg)
g = 9.8                        # Aceleración gravitatoria (m/s^2)

# Condiciones iniciales
r0 = 2.0                       # Posición radial inicial (m)
vr0 = 0.5                      # Velocidad radial inicial (m/s)
varphi0 = 0.0                  # Posición angular inicial (rad)
vphi0 = 2.0                    # Velocidad angular inicial (rad/s)

# Parámetros de integración
t_max = 10.0                   # Tiempo de integración (s)
dt = 0.01                      # Paso de tiempo recomendado (s)
```

### Salida del Programa

El programa genera:

1. **Gráficos**:
   - `trayectoria_xy.png` — Proyección 2D de la órbita
   - `momento_angular_vs_tiempo.png` — Evolución de $p_\varphi(t)$
   - `energia_vs_tiempo.png` — Evolución de $E(t)$
   - `error_relativo.png` — Error relativo acumulado

2. **Datos**:
   - `resultados_YYYYMMDD_HHMMSS.csv` — Series temporales completas

3. **Consola**:
   - Estadísticas de conservación
   - Error máximo relativo
   - Desviación estándar

---

## Metodología Numérica

### Ecuaciones de Movimiento

Sistema reducido en coordenadas cilíndricas $(r, \varphi)$:

$$\ddot{r} = \frac{p_\varphi^2}{m^2 r^3} + g \cot\alpha$$

$$\ddot{\varphi} = 0 \quad \Rightarrow \quad p_\varphi = m r^2 \dot{\varphi} = \text{constante}$$

### Cantidades Conservadas

1. **Momento angular azimutal** (exacto):
   $$p_\varphi = m r^2 \dot{\varphi} = \text{cte}$$

2. **Energía total** (exacta, si el Lagrangiano no depende explícitamente de $t$):
   $$E = \frac{1}{2}m\csc^2\alpha(\dot{r}^2 + r^2\dot{\varphi}^2) + V_{\text{ef}}(r)$$
   
   donde $V_{\text{ef}}(r) = \frac{p_\varphi^2}{2mr^2} + mgr\cot\alpha$

### Integrador Numérico

Se utiliza el método **RK45 adaptativo** (Runge-Kutta 4/5 orden) de SciPy:

- **Ventajas**: Control automático de error, paso adaptativo
- **Tolerancia relativa**: $10^{-9}$ (por defecto)
- **Tolerancia absoluta**: $10^{-12}$ (por defecto)

### Métricas de Error

**Error relativo** en $p_\varphi$:
$$\epsilon_{\varphi}(t) = \frac{|p_\varphi(t) - p_\varphi(0)|}{|p_\varphi(0)|}$$

**Error relativo** en $E$:
$$\epsilon_E(t) = \frac{|E(t) - E(0)|}{|E(0)|}$$

Se considera **conservación exitosa** si $\epsilon < 10^{-6}$ durante toda la integración.

---

## Control de Versiones

### Historial de Versiones

Ver archivo `VERSION.md` para detalles completos.

### Rama Principal
- **main**: Versión estable y validada

### Ramas de Desarrollo
- **feature/nuevos_sistemas**: Extensión a otros potenciales
- **bugfix/numerica**: Mejoras en precisión numérica
- **docs/metodologia**: Actualización de documentación

### Protocolo de Commits

```
git add cono_verificacion_conservacion.py
git commit -m "feat: implementar integrador RK45 con verificación de conservación"
git push origin main
```

**Formato recomendado**:
```
<tipo>(<componente>): <descripción concisa>

<cuerpo detallado (opcional)>

<referencias: issue #123>
```

Tipos válidos: `feat`, `fix`, `docs`, `refactor`, `test`

---

## Reproducibilidad

### Garantizar Resultados Consistentes

1. **Fijar semilla aleatoria** (si aplica):
   ```python
   np.random.seed(42)
   ```

2. **Usar exactamente las mismas versiones**:
   ```bash
   pip install -r requirements.txt --freeze
   ```

3. **Documentar parámetros** en cada ejecución:
   ```bash
   python cono_verificacion_conservacion.py --log-params
   ```

4. **Versionar datos de salida**:
   ```bash
   git add datos/resultados_*.csv
   git commit -m "data: guardar resultados con alpha=30deg, varphi0=2rad/s"
   ```

### Verificación de Reproducibilidad

Ejecutar dos veces consecutivas y comparar:

```bash
python cono_verificacion_conservacion.py > salida1.txt
python cono_verificacion_conservacion.py > salida2.txt
diff salida1.txt salida2.txt
```

Debe haber diferencias solo por precisión de punto flotante ($< 10^{-14}$).

---

## Troubleshooting

### Problema: "ModuleNotFoundError: No module named 'scipy'"
**Solución**: Instalar dependencias
```bash
pip install scipy numpy matplotlib
```

### Problema: Gráficos no se generan
**Solución**: Verificar que la carpeta `graficos/` existe
```bash
mkdir -p graficos
python cono_verificacion_conservacion.py
```

### Problema: Error relativo muy alto ($> 10^{-3}$)
**Posibles causas**:
- Paso de tiempo `dt` demasiado grande → reducir a `0.001`
- Condiciones iniciales inestables → verificar que $r_0 > 0$, $\dot{\varphi}_0 \neq 0$
- Tiempo de integración muy largo → limitar a $t_{\max} = 5$ s inicialmente

---

## Extensiones Futuras

### Mejoras Planificadas
1. Verificar conservación en otros sistemas (péndulo, órbita Kepler)
2. Implementar integrador simpléctico (mayor preservación de energía)
3. Análisis de estabilidad de órbitas periódicas
4. Interfaz interactiva (tkinter o Jupyter)

### Contribuciones
Para contribuir:
1. Fork del repositorio
2. Crear rama `feature/mi-mejora`
3. Enviar pull request con descripción detallada

---

## Validación y Pruebas

### Test de Conservación

Ejecutar script de validación:
```bash
python test_conservacion.py
```

**Criterios de aprobación**:
- ✓ $p_\varphi$ constante dentro de $10^{-6}$ error relativo
- ✓ $E$ oscila con amplitud $< 10^{-5}$ alrededor del valor nominal
- ✓ Integración completa sin NaN o infinitos

---

## Referencias Bibliográficas

- **Goldstein, H.** (2001). *Classical Mechanics* (3rd ed.). Addison-Wesley.
- **Arnol'd, V. I.** (1989). *Mathematical Methods of Classical Mechanics*. Springer.
- **Butcher, J. C.** (2008). *Numerical Methods for Ordinary Differential Equations*. Wiley.

---

## Licencia y Atribuciones

- **Código**: Desarrollado como parte del ejercicio de consolidación de Mecánica Clásica
- **Año académico**: 2026
- **Institucionalidad**: Curso de Mecánica Clásica II

---

## Contacto y Soporte

Para preguntas o reportar problemas:
- Abrir un **issue** en el repositorio
- Consultar documentación en `docs/metodologia.md`
- Revisar archivo `VERSION.md` para cambios recientes

---

## Checklist de Reproducibilidad

- [ ] Dependencias instaladas (`pip install -r requirements.txt`)
- [ ] Carpetas `graficos/` y `datos/` creadas
- [ ] Script ejecutado sin errores
- [ ] Gráficos generados en carpeta `graficos/`
- [ ] Datos guardados en `datos/resultados_*.csv`
- [ ] Error relativo < $10^{-6}$ para $p_\varphi$
- [ ] Código versionado con `git commit`
- [ ] Parámetros documentados en consola

---

**Última actualización**: 2026-08-28  
**Versión del README**: 1.0
