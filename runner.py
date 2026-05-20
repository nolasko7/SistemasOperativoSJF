import pandas as pd
from generator import generate_processes
from sjf import run_sjf
from gantt import plot_gantt

def run_multiple_times(num_runs=5, num_processes=5, plot=True):
    """
    Ejecuta múltiples corridas del algoritmo, almacena los resultados y genera un resumen comparativo.
    """
    all_metrics = []
    
    for run_id in range(1, num_runs + 1):
        # Fase 1: Generar procesos
        df_processes = generate_processes(num_processes=num_processes, run_id=run_id, output_dir="results")
        
        # Fase 2 y 3: Correr SJF y calcular métricas
        result_df, metrics = run_sjf(df_processes)
        
        # Guardar resultados de la corrida
        result_df.to_csv(f"results/result_run_{run_id}.csv", index=False)
        
        # Añadir run_id para identificar las métricas
        metrics['run_id'] = run_id
        all_metrics.append(metrics)
        
        # Fase 5: Gantt
        if plot:
            plot_gantt(result_df, run_id)
            
    # Fase 4: Comparación entre corridas
    summary_df = pd.DataFrame(all_metrics)
    
    # Reordenar columnas para mejor lectura
    summary_df = summary_df[['run_id', 'avg_waiting_time', 'avg_turnaround_time', 'throughput', 'cpu_utilization']]
    
    # Guardar tabla de resumen
    summary_df.to_csv("results/summary.csv", index=False)
    
    return summary_df
