# SJF Scheduler - Simulación y Análisis

## 1. ¿Qué es SJF?

El planificador SJF (Shortest Job First) es un algoritmo utilizado por los sistemas operativos para decidir qué proceso debe ejecutar la CPU en un momento dado. El objetivo principal del scheduling es maximizar la eficiencia y minimizar los tiempos de espera del sistema.

La regla central de SJF es muy sencilla: **elige siempre el proceso disponible que requiera menos tiempo de ráfaga (burst time)**. Si hay varios procesos listos para ejecutarse en la cola, el que tarde menos en completarse tendrá prioridad absoluta sobre los demás.

Esta implementación de SJF es **No-Preemptiva**. Esto significa que una vez que a un proceso se le asigna la CPU, no puede ser interrumpido hasta que termine toda su ejecución. Si un proceso más corto llega mientras otro más largo se está ejecutando, deberá esperar pacientemente en la cola hasta que el procesador se libere.

## 2. Cómo correr el programa

Asegúrate de tener Python instalado junto con las dependencias necesarias. Puedes instalar todo ejecutando:

```bash
pip install pandas matplotlib tabulate openpyxl numpy
python sjf_scheduler.py
```

El programa generará automáticamente una carpeta `Ejecuciones/Ejecucion_X/` (donde X es un número incremental para cada ejecución) que contendrá dos subcarpetas:
- **`graficos/`**: Contiene los dashboards visuales completos para cada corrida y un gráfico comparativo final.
- **`estadisticas/`**: Contiene los archivos CSV y un reporte en Excel con todas las métricas consolidadas de todos los procesos.

## 3. Glosario de métricas

Para entender a fondo los resultados generados, aquí tienes la explicación de cada métrica.

### Para cada proceso individual:

| Término | Definición simple | Ejemplo |
|---|---|---|
| `arrival_time` | Cuándo el proceso "tocó timbre" en el sistema | Llegó en t=3 |
| `burst_time` | Cuánta CPU necesita para terminar | Necesita 5 unidades |
| `start_time` | Cuándo la CPU lo atendió por primera vez | Empezó en t=7 |
| `waiting_time` | Tiempo total parado en cola sin hacer nada | Esperó 4 unidades |
| `turnaround_time` | Tiempo total de vida en el sistema (espera + ráfaga) | Vivió 9 unidades |
| `response_time` | Cuánto tardó en ser atendido por primera vez | Tardó 4 unidades en ser visto |
| `completion_time` | Cuándo terminó y liberó la CPU | Terminó en t=12 |

### Para métricas agregadas por corrida:

| Término | Definición simple | Cómo leerlo |
|---|---|---|
| `avg_waiting_time` | Promedio de espera de todos los procesos | **Más bajo = mejor** |
| `avg_turnaround_time` | Promedio de tiempo total en el sistema | **Más bajo = procesos resueltos rápido** |
| `avg_response_time` | Promedio hasta la primer atención | **Más bajo = usuarios perciben menos latencia** |
| `throughput` | Procesos completados por unidad de tiempo | **Más alto = sistema más productivo** |
| `cpu_utilization_%` | % de tiempo que la CPU trabajó vs estuvo inactiva | **100% es ideal**, si es menor hubo huecos vacíos |
| `total_time` | Duración total de la simulación entera | No comparar directamente entre corridas sin ver el throughput. |

## 4. Cómo leer los gráficos generados

El programa produce imágenes llamadas `dashboard_corrida_X.png`. Estas tienen varias secciones:

**1. Diagrama de Gantt:**
- **Bloques de color:** CPU ocupada ejecutando el proceso correspondiente.
- **Bloques grises (IDLE):** CPU desocupada. Significa que ningún proceso había llegado aún.
- **Barra inferior (CPU Util.):** Verde para tiempo activo, Rojo para tiempo ocioso.

**2. Barras apiladas por proceso (Izquierda Inferior):**
- **Barra naranja corta + barra azul larga:** Significa que el proceso esperó poco y ejecutó mucho. ¡Excelente! ✅
- **Barra naranja larga + barra azul corta:** Significa que el proceso esperó muchísimo tiempo. Posible víctima de *starvation*. ⚠️

**3. Gráfico de dispersión WT/TAT/RT (Derecha Inferior):**
- Si las 3 líneas (Naranja, Verde, Roja) están juntas hacia abajo, la corrida fue muy eficiente.
- Si ves que un solo proceso tiene un pico altísimo respecto a los demás, encontraste un "outlier" (un caso aislado) que arruinó el promedio global de la simulación.

**4. Gráfico Comparativo Final (`comparativa_corridas.png`):**
- Sirve para enfrentar el rendimiento global.
- Si ves un `total_time` alto acompañado de una `cpu_utilization` alta (verde), no te asustes: simplemente la corrida tenía procesos con ráfagas muy largas.
- Si ves un `total_time` alto pero la `cpu_utilization` es baja (línea roja cae), hubo problemas: demasiados huecos o los procesos llegaron muy tarde.

## 5. Limitaciones del algoritmo
- **Predictivo vs Realidad:** SJF requiere conocer el `burst_time` exacto de antemano. En un sistema operativo real, esto es imposible de saber con un 100% de precisión y debe predecirse usando algoritmos exponenciales basados en el pasado.
- **Starvation (Inanición):** Un proceso muy largo podría quedarse estancado infinitamente en la cola de listos si continúan llegando procesos cortos sin parar.
- **Rigidez:** Al ser una variante No-preemptiva, el algoritmo no es reactivo frente a urgencias repentinas (ej: la llegada repentina de un micro-proceso t=1).

## 6. Estructura del proyecto
- `sjf_scheduler.py`: El script principal de la simulación y graficado.
- `requirements.txt`: El listado de dependencias de Python necesarias.
- `README.md`: Este archivo de documentación.
- `Ejecuciones/`: El directorio raíz (autogenerado) donde se guardan históricamente todas las simulaciones que realizas con el script.
