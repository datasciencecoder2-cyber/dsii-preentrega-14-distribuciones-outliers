# Data Science II — Pre-entrega 14

## Análisis visual de distribuciones categóricas y outliers

**Pregunta analítica:** ¿Cómo varían los importes de las cuentas y propinas de un restaurante según el día, y qué registros ameritan revisión por valores extremos?

El repositorio incluye el análisis exploratorio reproducible en un Notebook de Jupyter, tres tipos obligatorios de gráficos (barras, cajas y violín), estadísticas de asimetría y curtosis, y la detección y segmentación de casos atípicos mediante IQR (1,5 × rango intercuartílico). **No se eliminan datos automáticamente.**

## Fuente del dataset real

- **Nombre:** Tips (registro de cuentas y propinas en un restaurante).
- **Origen de la copia:** `plotly.express.data.tips()`, versión incluida en la biblioteca Plotly que permite reproducir la muestra de 244 filas. Se incluye una exportación CSV original para ejecutar este repositorio sin internet.
- **Documentación Plotly:** https://plotly.github.io/plotly.py-docs/generated/plotly.express.data.html
- **Copia pública de la colección Seaborn:** https://github.com/mwaskom/seaborn-data/blob/master/tips.csv
- **Contexto histórico y alcance:** https://iowabiostat.github.io/data-sets/tips/tips.html
- **CSV local:** `datos/tips.csv` | 244 registros × 7 variables originales.
- **SHA-256 de la copia CSV:** `22415aaf1e56e675b9a0983cb0d321697dad51f6060a44fb8ecaad7a00de9a09`.

Las observaciones proceden del registro de un restaurante, no de una encuesta representativa de todos los restaurantes. No es posible deducir causalidad por comparar grupos.

| Campo | Tipo | Significado |
| --- | --- | --- |
| `total_bill` | numérico decimal | Cuenta total (USD) |
| `tip` | numérico decimal | Propina (USD) |
| `size` | numérico entero | Cantidad de personas |
| `day` | categórico | Día (`Thur`, `Fri`, `Sat`, `Sun`) |
| `time` | categórico | `Lunch` / `Dinner` |
| `smoker` | categórico | Presencia de fumadores (`Yes` / `No`) |
| `sex` | categórico | Sexo registrado de quien pagó |

## Organización del repositorio

```text
.
├── datos/tips.csv
├── notebooks/analisis_distribuciones_outliers.ipynb  # NOTEBOOK PRINCIPAL
├── src/eda.py                                       # validaciones, stats, IQR
├── tests/test_analisis.py                           # 12 pruebas
├── graficos/                                        # PNG reproducibles
├── resultados/resumen_estadistico.csv
├── resultados/outliers_iqr.csv
├── evidencia/ejecucion.txt
├── requirements.txt
├── .gitignore
└── README.md
```

## Requisitos

Python 3.11 o superior recomendado; probado al generar el entregable con Python local y bibliotecas científicas actuales. Funciona con el CSV local, sin acceso a internet.

```powershell
py -m pip install -r requirements.txt
```

## Pasos para ejecutar

Desde la carpeta raíz del proyecto:

```powershell
py -m jupyter lab
```

Abrir `notebooks/analisis_distribuciones_outliers.ipynb` y seleccionar **Kernel → Restart Kernel and Run All Cells**. El Notebook fue guardado con resultados y gráficos visibles para poder revisarlo también desde GitHub sin ejecutarlo.

Para validar las reglas de datos y el método IQR:

```powershell
py -m unittest discover -s tests -v
```

La ejecución del notebook también puede hacerse sin abrir JupyterLab:

```powershell
py -m jupyter nbconvert --to notebook --execute --inplace notebooks/analisis_distribuciones_outliers.ipynb
```

## Metodología y hallazgos principales

1. **Carga y validación:** 244 filas; ninguna celda nula. Hay **un par de filas idénticas** en las siete columnas originales, pero **no** hay ID de transacción; podría ser una coincidencia legítima, por lo que no se elimina sin evidencia.
2. **Gráfico de barras:** sábado 87 registros, domingo 76, jueves 62 y viernes 19; son frecuencias de la muestra, **no estimaciones de tráfico habitual**.
3. **Boxplots y violines:** muestran diferencias de distribución, dispersión y valores altos por día. La geometría del violín es una estimación suavizada, no un registro adicional.
4. **Asimetría y curtosis (Fisher, exceso):** `total_bill` presenta asimetría positiva de **1,133** y curtosis de **1,218**; `tip` presenta asimetría positiva de **1,465** y curtosis de **3,648**. En ambos casos existe cola a la derecha, más marcada para las propinas.
5. **IQR global:** para `total_bill`, Q1 = 13,3475; Q3 = 24,1275; límite superior = 40,2975 USD; **9 outliers**. Para `tip`, Q1 = 2,0000; Q3 = 3,5625; límite superior = 5,90625 USD; **9 outliers**. **3 coinciden en ambas variables; en conjunto son 15 registros distintos**.

Los límites se calculan una sola vez en el conjunto completo para **exploración descriptiva**. Si se entrena un modelo predictivo posteriormente, los umbrales aprendidos del dato se estimarán exclusivamente con `train` para evitar data leakage.

## Decisiones sobre outliers

**Conservar como primera opción.** Una cuenta de USD 50,81 o una propina de USD 10 puede ser legítima. Antes de eliminar se debe revisar consistencia con tamaño del grupo, información del registro y reglas del negocio. Para modelos sensibles, se podría contrastar una transformación `log1p` sobre montos positivos o estimadores robustos y comparar métricas fuera de muestra; nunca recortar valores únicamente por superar IQR. La muestra no permite verificar el origen de cada extremo.

## Interpretación y limitaciones

- El valor de **asimetría positiva** indica una cola de importes altos; no confundir con una cola izquierda.
- La **curtosis en exceso** toma 0 como referencia gaussiana; positiva significa colas/comportamiento de extremos más pronunciados en términos estadísticos, pero no demuestra anomalías.
- Los registros son históricos y de un establecimiento; la selección de días y horarios puede estar sesgada.
- Las visualizaciones no justifican conclusiones causales sobre el comportamiento de clientes.
- `registro_ref` es un identificador **creado para este análisis**, no un ID presente en la fuente.

## Criterios de evaluación

- Notebook `.ipynb` ejecutable y README: ✓
- Barplot, Boxplot y Violin Plot generados en Python: ✓
- Cálculo explícito de skewness y kurtosis: ✓
- Detección, segmentación y listado de casos atípicos con IQR: ✓
- Comentarios, nombres descriptivos y decisiones de limpieza documentadas: ✓
