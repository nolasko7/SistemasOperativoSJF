import matplotlib.pyplot as plt
import os

def plot_gantt(result_df, run_id, output_dir="results"):
    """
    Genera y guarda un diagrama de Gantt de la ejecución de procesos.
    """
    fig, ax = plt.subplots(figsize=(10, 3))
    
    # Colores para distinguir los procesos
    colors = plt.colormaps.get_cmap('tab20')
    
    for i, row in result_df.iterrows():
        pid = row['PID']
        start = row['start_time']
        duration = row['burst_time']
        
        # Dibujar barra
        ax.broken_barh([(start, duration)], (10, 9), facecolors=(colors(i % 20)))
        
        # Poner nombre del proceso en el centro de la barra
        ax.text(start + duration / 2, 14.5, pid, ha='center', va='center', color='black', fontweight='bold')
        
    ax.set_ylim(5, 25)
    max_time = result_df['completion_time'].max()
    ax.set_xlim(0, max_time + 2)
    ax.set_xlabel('Unidades de Tiempo')
    ax.set_yticks([])
    ax.set_title(f'Diagrama de Gantt - SJF (Corrida {run_id})')
    
    # Marcas en el eje X para mayor claridad
    ax.set_xticks(range(0, int(max_time) + 3, max(1, int(max_time)//20)))
    
    plt.tight_layout()
    
    # Guardar gráfico
    os.makedirs(output_dir, exist_ok=True)
    plt.savefig(os.path.join(output_dir, f'gantt_run_{run_id}.png'))
    plt.close()
