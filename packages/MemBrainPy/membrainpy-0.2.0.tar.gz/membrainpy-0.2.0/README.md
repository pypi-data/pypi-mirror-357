````markdown
# MemBrainPy: Biblioteca de Sistemas P en Python

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue) ![License](https://img.shields.io/badge/license-MIT-green)

MemBrainPy es una librería en Python que implementa y simula **Sistemas P** (P‐systems) en modo máx-paralelo, basados en el formalismo de P-Lingua. Permite:

- Definir estructuras jerárquicas de membranas y multiconjuntos de objetos.  
- Especificar reglas de evolución, comunicación, disolución y creación de membranas.  
- Cargar definiciones en formato `.pli` con el módulo de lectura  
  (`Lector.py`).  
- Simular lapso a lapso y registrar estadísticas en tablas y CSV.  
- Visualizar dinámicamente la simulación con Matplotlib.  
- Generar ejemplos de sistemas P estándar (suma, resta, división…)  
  mediante funciones de conveniencia.

---

## 📥 Instalación

Instala MemBrainPy con pip:

```bash
pip install membrainpy
````

O clona el repositorio y, desde la raíz del proyecto:

```bash
git clone https://github.com/tu-usuario/membrainpy.git
cd membrainpy
pip install .
```

---

## 🚀 Primeros pasos

```python
from membrainpy.SistemaP import SistemaP, Membrana, Regla, simular_lapso

# 1. Crear un sistema vacío y definir la membrana piel
sis = SistemaP(output_membrane="skin")
m0 = Membrana("skin", resources={})
sis.add_membrane(m0)

# 2. Añadir una membrana hija con recursos y reglas
m1 = Membrana("m1", resources={"a": 5, "b": 3})
# Regla: consume 2·a → produce 1·c en la piel
r = Regla(left={"a":2}, right={"c_out":1}, priority=1)
m1.add_regla(r)
sis.add_membrane(m1, parent_id="skin")

# 3. Simular un lapso
lap = simular_lapso(sis, rng_seed=42)
print("Recursos tras consumo:", lap.consumos)
print("Producciones:", lap.producciones)
```

---

## 📦 Estructura de módulos

* **`SistemaP.py`**
  Núcleo de clases: `SistemaP`, `Membrana`, `Regla`, simulador por lapso, generación de máximales, estadísticas y exportación a DataFrame/CSV.
* **`Lector.py`**
  Parser de archivos P-Lingua (`.pli`): lee jerarquía (`@mu`), multiconjuntos (`@ms(id)`), reglas y construye un `SistemaP`.
* **`funciones.py`**
  Fábrica de sistemas P elementales para operaciones aritméticas (suma, resta, división, paridad, etc.).
* **`operaciones_avanzadas.py`**
  Multiplicación y potencia mediante simulaciones sucesivas de sistemas P básicos.
* **`visualizadorAvanzado.py`**
  Visualización paso a paso de la simulación con Matplotlib: dibuja estructuras, recursos y reglas aplicadas.
* **`configurador.py`**
  Interfaz gráfica (Tkinter) para construir interactivamente un Sistema P: añadir membranas, recursos, reglas y definir membrana de salida.
* **`tests_sistemas.py`**
  Suite de tests tipo `unittest` que cubre sistemas básicos, anidados, con conflictos y casos de uso avanzados.

---

## 📖 Ejemplo de uso con P-Lingua

```python
from membrainpy.Lector import leer_sistema

# Suponiendo un archivo ejemplo.pli en el disco
sis = leer_sistema("ejemplo.pli")

# Simular 10 pasos y exportar estadísticas
from membrainpy.SistemaP import registrar_estadisticas
df = registrar_estadisticas(sis, lapsos=10, rng_seed=0, csv_path="resultados.csv")
print(df.head())
```

---

## 🔧 Testing

Ejecuta la batería de tests con:

```bash
pytest
```

O bien:

```bash
python -m unittest discover -v
```

---

## 🤝 Contribuir

1. Haz un *fork* del proyecto y crea una rama (`git checkout -b feature/nueva-función`).
2. Añade tests en `tests_sistemas.py` y asegúrate de que pasan todos.
3. Abre un *pull request* describiendo tu contribución.

---

## 📚 Referencias

* Pérez-Hurtado et al. (2009). *Un entorno de programación para Membrane Computing (P-Lingua)* fileciteturn0file7
* Sempere, J. M. (s.f.). *Computación con membranas. Sistemas P* fileciteturn0file8
* Gh. Păun (2002). *Membrane Computing. An Introduction.* Springer.

---

## 📝 Licencia

Este proyecto está bajo licencia **MIT**. Véase el archivo [LICENSE](LICENSE) para más detalles.

```
```
