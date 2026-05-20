import random
import os
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from tabulate import tabulate

def generate_processes(n, seed):
    random.seed(seed)
    processes = []
    for i in range(1, n + 1):
        processes.append({
            'PID': f'P{i}',
            'arrival_time': random.randint(0, 12),
            'burst_time': random.randint(1, 15)
        })
    return processes

def run_sjf(processes):
    processes.sort(key=lambda x: x['arrival_time'])
    current_time = 0
    ready_queue = []
    exec_order = []
    gantt = []
    completed = []
    
    # Track which processes have been added to completed
    remaining_processes = processes.copy()
    
    while remaining_processes or ready_queue:
        # Add processes that have arrived to ready_queue
        arrived_this_tick = [p for p in remaining_processes if p['arrival_time'] <= current_time]
        for p in arrived_this_tick:
            ready_queue.append(p)
            remaining_processes.remove(p)
            
        if not ready_queue:
            # CPU Idle, jump to next arrival
            if remaining_processes:
                current_time = remaining_processes[0]['arrival_time']
            continue
            
        # Select shortest job from ready queue
        # For stable sort (FIFO if same burst), min on burst_time works since ready_queue is appended in arrival order
        proc = min(ready_queue, key=lambda x: x['burst_time'])
        ready_queue.remove(proc)
        
        start = current_time
        end = start + proc['burst_time']
        
        exec_order.append(proc['PID'])
        gantt.append((proc['PID'], start, end))
        
        # Calculate metrics for process
        completion_time = end
        turnaround_time = completion_time - proc['arrival_time']
        waiting_time = turnaround_time - proc['burst_time']
        response_time = start - proc['arrival_time']
        
        comp_proc = {
            'PID': proc['PID'],
            'Llegada': proc['arrival_time'],
            'Burst': proc['burst_time'],
            'Inicio': start,
            'Fin': completion_time,
            'TAT': turnaround_time,
            'WT': waiting_time,
            'RT': response_time
        }
        completed.append(comp_proc)
        
        current_time = end
        
    return completed, gantt, exec_order

def compute_metrics(completed, gantt):
    n = len(completed)
    if n == 0:
        return {}
    
    total_burst = sum(p['Burst'] for p in completed)
    total_wt = sum(p['WT'] for p in completed)
    total_tat = sum(p['TAT'] for p in completed)
    total_rt = sum(p['RT'] for p in completed)
    
    last_end = max(end for _, _, end in gantt) if gantt else 0
    total_time = last_end
    
    throughput = n / total_time if total_time > 0 else 0
    cpu_utilization = (total_burst / total_time * 100) if total_time > 0 else 0
    
    return {
        'avg_waiting_time': total_wt / n,
        'avg_turnaround_time': total_tat / n,
        'avg_response_time': total_rt / n,
        'throughput': throughput,
        'cpu_utilization_%': cpu_utilization,
        'total_time': total_time
    }

def plot_gantt(gantt, exec_order, run_id, ax):
    colors = plt.colormaps.get_cmap('tab10')
    
    pid_to_color = {}
    for i, pid in enumerate(set(exec_order)):
        pid_to_color[pid] = colors(i % 10)
        
    for pid, start, end in gantt:
        duration = end - start
        ax.broken_barh([(start, duration)], (10, 9), facecolors=(pid_to_color[pid]))
        # Black text for better visibility depending on colors, let's use black
        ax.text(start + duration / 2, 14.5, pid, ha='center', va='center', color='black', fontweight='bold')
        
    ax.set_ylim(5, 25)
    max_time = max(end for _, _, end in gantt) if gantt else 0
    ax.set_xlim(0, max_time + 1)
    ax.set_xlabel('Unidades de Tiempo')
    ax.set_yticks([])
    
    order_str = " → ".join(exec_order)
    ax.set_title(f'Corrida {run_id} | Orden: {order_str}')
    
    # Tick marks every 1 unit might be too crowded if time is > 50, let's dynamically adjust
    step = 1 if max_time <= 30 else max(1, int(max_time)//20)
    ax.set_xticks(range(0, int(max_time) + 2, step))

def main(k=5, n_procs=6):
    os.makedirs('results', exist_ok=True)
    
    all_processes_data = []
    all_metrics = []
    
    fig, axes = plt.subplots(k, 1, figsize=(14, 3.5 * k), dpi=150)
    if k == 1:
        axes = [axes]
    
    for run_id in range(1, k + 1):
        seed = run_id * 42
        processes = generate_processes(n_procs, seed)
        completed, gantt, exec_order = run_sjf(processes)
        metrics = compute_metrics(completed, gantt)
        
        # Assign position based on exec_order
        for pos, p in enumerate(completed, 1):
            p['Pos.'] = pos
            p_data = {'Corrida': run_id, **p}
            all_processes_data.append(p_data)
            
        metrics['Corrida'] = run_id
        all_metrics.append(metrics)
        
        # Plot Gantt
        plot_gantt(gantt, exec_order, run_id, axes[run_id - 1])
        
        # Console output for this run
        print(f"\n--- Corrida {run_id} ---")
        print(f"Orden SJF: {' → '.join(exec_order)}")
        
        # Format processes table
        df_proc = pd.DataFrame(completed)
        cols_order = ['Pos.', 'PID', 'Llegada', 'Burst', 'Inicio', 'Fin', 'TAT', 'WT', 'RT']
        df_proc = df_proc[cols_order]
        print("\nTabla de Procesos:")
        print(tabulate(df_proc, headers='keys', tablefmt='psql', showindex=False))
        
        # Format metrics table
        metrics_print = {
            'WT avg': round(metrics['avg_waiting_time'], 2),
            'TAT avg': round(metrics['avg_turnaround_time'], 2),
            'RT avg': round(metrics['avg_response_time'], 2),
            'Throughput': round(metrics['throughput'], 4),
            'CPU util.%': round(metrics['cpu_utilization_%'], 2),
            'T. total': round(metrics['total_time'], 2)
        }
        print("\nTabla de Métricas:")
        print(tabulate([metrics_print], headers='keys', tablefmt='psql', showindex=False))
        
    plt.tight_layout()
    plt.savefig('results/sjf_gantt_todas_corridas.png')
    plt.close()
    
    # Comparative summary
    df_metrics = pd.DataFrame(all_metrics)
    best_run = df_metrics.loc[df_metrics['avg_waiting_time'].idxmin()]
    worst_run = df_metrics.loc[df_metrics['avg_waiting_time'].idxmax()]
    
    print("\n" + "="*60)
    print(" TABLA COMPARATIVA DE CORRIDAS ".center(60))
    print("="*60)
    
    df_metrics_show = df_metrics[['Corrida', 'avg_waiting_time', 'avg_turnaround_time', 'avg_response_time', 'throughput', 'cpu_utilization_%', 'total_time']].copy()
    df_metrics_show = df_metrics_show.round(2)
    print(tabulate(df_metrics_show, headers='keys', tablefmt='double_grid', showindex=False))
    
    print(f"\n[⭐] MEJOR corrida: Corrida {int(best_run['Corrida'])} (menor WT avg: {best_run['avg_waiting_time']:.2f})")
    print(f"[⚠️] PEOR corrida: Corrida {int(worst_run['Corrida'])} (mayor WT avg: {worst_run['avg_waiting_time']:.2f})")
    
    # Save Excel
    df_all_proc = pd.DataFrame(all_processes_data)
    cols_order_all = ['Corrida', 'Pos.', 'PID', 'Llegada', 'Burst', 'Inicio', 'Fin', 'TAT', 'WT', 'RT']
    df_all_proc = df_all_proc[cols_order_all]
    
    df_comp = df_metrics.copy()
    df_comp['mejor_WT'] = (df_comp['Corrida'] == best_run['Corrida'])
    df_comp['peor_WT'] = (df_comp['Corrida'] == worst_run['Corrida'])
    
    excel_path = 'results/sjf_resultados_completos.xlsx'
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        df_all_proc.to_excel(writer, sheet_name='Detalle_Procesos', index=False)
        df_metrics.to_excel(writer, sheet_name='Metricas_Corridas', index=False)
        df_comp.to_excel(writer, sheet_name='Comparacion', index=False)
        
    print("\nArchivos generados:")
    print(f" - {os.path.abspath(excel_path)}")
    print(f" - {os.path.abspath('results/sjf_gantt_todas_corridas.png')}")

if __name__ == '__main__':
    main()
