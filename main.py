from generator import generate_processes
from sjf import run_sjf
from runner import run_multiple_times
from gantt import plot_gantt
from tabulate import tabulate
import pandas as pd

def main():
    print("="*60)
    print(" Simulación SJF (Shortest Job First) No-Preemptivo ".center(60))
    print("="*60)
    
    # ---------------------------------------------------------
    # PASO 1 y 2: Ejemplo de generación y explicación
    # ---------------------------------------------------------
    print("\n--- PASO 1 y 2: Generación de tabla y proceso ---")
    df_test = generate_processes(num_processes=5, run_id="demo", output_dir="results")
    print("\nProcesos Generados Aleatoriamente:")
    print(tabulate(df_test, headers='keys', tablefmt='psql', showindex=False))
    
    # ---------------------------------------------------------
    # PASO 3 y 4: Ejecutar SJF en la corrida de prueba y métricas
    # ---------------------------------------------------------
    print("\n--- PASO 3 y 4: Ejecución Algoritmo SJF y Métricas ---")
    result_df, metrics = run_sjf(df_test)
    
    print("\nOrden de Ejecución y Resultados Finales:")
    cols_to_show = ['PID', 'arrival_time', 'burst_time', 'start_time', 'completion_time', 'waiting_time', 'turnaround_time']
    print(tabulate(result_df[cols_to_show], headers='keys', tablefmt='psql', showindex=False))
    
    print("\nMétricas de la corrida de demostración:")
    metrics_df = pd.DataFrame([{k: round(v, 2) for k, v in metrics.items()}])
    print(tabulate(metrics_df, headers='keys', tablefmt='psql', showindex=False))
    
    # Crear Gantt de demostración
    plot_gantt(result_df, "demo")
    print("\n[INFO] Diagrama de Gantt guardado en 'results/gantt_run_demo.png'")
    
    # ---------------------------------------------------------
    # PASO 5: Múltiples corridas
    # ---------------------------------------------------------
    print("\n--- PASO 5: Ejecutando 5 corridas distintas ---")
    summary_df = run_multiple_times(num_runs=5, num_processes=6, plot=True)
    
    print("\nResumen de las 5 corridas (Tabla Comparativa):")
    # Redondeamos para visualización
    summary_df_rounded = summary_df.round(2)
    print(tabulate(summary_df_rounded, headers='keys', tablefmt='psql', showindex=False))
    
    # Identificar la mejor y la peor
    best_wt = summary_df.loc[summary_df['avg_waiting_time'].idxmin()]
    worst_wt = summary_df.loc[summary_df['avg_waiting_time'].idxmax()]
    
    print(f"\n[🏆] La MEJOR corrida (menor WT) fue la Run {int(best_wt['run_id'])} con WT promedio de {best_wt['avg_waiting_time']:.2f}")
    print(f"[⚠️] La PEOR corrida (mayor WT) fue la Run {int(worst_wt['run_id'])} con WT promedio de {worst_wt['avg_waiting_time']:.2f}")
    
    print("\n[✔] Finalizado. Todos los CSVs y gráficos Gantt se han guardado en la carpeta 'results/'.")

if __name__ == "__main__":
    main()
