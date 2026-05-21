import random
import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
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
    processes_sorted = sorted(processes, key=lambda x: x['arrival_time'])
    current_time = 0
    ready_queue = []
    exec_order = []
    gantt = []
    completed = []
    idle_blocks = []
    
    remaining_processes = processes_sorted.copy()
    
    while remaining_processes or ready_queue:
        arrived_this_tick = [p for p in remaining_processes if p['arrival_time'] <= current_time]
        for p in arrived_this_tick:
            ready_queue.append(p)
            remaining_processes.remove(p)
            
        if not ready_queue:
            if remaining_processes:
                next_arrival = remaining_processes[0]['arrival_time']
                idle_blocks.append(('IDLE', current_time, next_arrival))
                current_time = next_arrival
            continue
            
        proc = min(ready_queue, key=lambda x: x['burst_time'])
        ready_queue.remove(proc)
        
        start = current_time
        end = start + proc['burst_time']
        
        exec_order.append(proc['PID'])
        gantt.append((proc['PID'], start, end))
        
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
        
    return completed, gantt, exec_order, idle_blocks

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

def plot_dashboard_corrida(completed, gantt, exec_order, idle_blocks, metrics, run_id, processes, save_path):
    fig = plt.figure(figsize=(14, 14), dpi=150)
    gs = gridspec.GridSpec(5, 2, height_ratios=[3, 0.5, 2, 3, 3], hspace=0.6, wspace=0.3)
    
    ax_gantt = fig.add_subplot(gs[0, :])
    ax_cpu = fig.add_subplot(gs[1, :])
    ax_timeline = fig.add_subplot(gs[2, :])
    ax_bars = fig.add_subplot(gs[3, 0])
    ax_scatter = fig.add_subplot(gs[3, 1])
    ax_table = fig.add_subplot(gs[4, :])
    
    colors = plt.colormaps.get_cmap('tab10')
    pid_to_color = {}
    for i, pid in enumerate(sorted(list(set([p['PID'] for p in processes])))):
        pid_to_color[pid] = colors(i % 10)
        
    max_time = max(end for _, _, end in gantt) if gantt else 0
    
    # 1. GANTT
    for pid, start, end in gantt:
        duration = end - start
        ax_gantt.broken_barh([(start, duration)], (10, 9), facecolors=(pid_to_color[pid]))
        ax_gantt.text(start + duration / 2, 14.5, pid, ha='center', va='center', color='black', fontweight='bold')
        
    for _, start, end in idle_blocks:
        duration = end - start
        ax_gantt.broken_barh([(start, duration)], (10, 9), facecolors='lightgray', hatch='//')
        ax_gantt.text(start + duration / 2, 14.5, 'IDLE', ha='center', va='center', color='black')
        
    ax_gantt.set_ylim(5, 25)
    ax_gantt.set_xlim(0, max_time + 1)
    ax_gantt.set_yticks([])
    ax_gantt.set_xlabel('Tiempo')
    ax_gantt.set_title(f'Corrida {run_id} - Gantt Chart (Orden: {" → ".join(exec_order)})')
    
    step = 1 if max_time <= 30 else max(1, int(max_time)//20)
    ax_gantt.set_xticks(range(0, int(max_time) + 2, step))
    
    # 2. CPU UTILIZATION
    cpu_util = metrics['cpu_utilization_%']
    idle_pct = 100 - cpu_util
    ax_cpu.barh([0], [cpu_util], color='limegreen', label=f'Activo ({cpu_util:.1f}%)')
    ax_cpu.barh([0], [idle_pct], left=[cpu_util], color='tomato', label=f'Idle ({idle_pct:.1f}%)')
    ax_cpu.set_xlim(0, 100)
    ax_cpu.set_yticks([])
    ax_cpu.set_xticks([0, 25, 50, 75, 100])
    ax_cpu.set_xticklabels(['0%', '25%', '50%', '75%', '100%'])
    ax_cpu.set_title('Utilización de CPU', fontsize=10, pad=5)
    ax_cpu.legend(loc='center left', bbox_to_anchor=(1.02, 0.5), fontsize=9)
    
    # 3. TIMELINE LLEGADA
    ax_timeline.set_xlim(0, max_time + 1)
    ax_timeline.set_ylim(-1, 1)
    ax_timeline.axhline(0, color='black', linewidth=1)
    ax_timeline.set_yticks([])
    ax_timeline.set_title('Línea de tiempo de llegada de procesos', fontsize=10, pad=5)
    ax_timeline.set_xticks(range(0, int(max_time) + 2, step))
    
    for p in processes:
        arr_time = p['arrival_time']
        pid = p['PID']
        ax_timeline.plot(arr_time, 0, marker='o', markersize=8, color=pid_to_color[pid], markeredgecolor='black')
        ax_timeline.annotate(pid, (arr_time, 0.2), ha='center', va='bottom', fontsize=9, fontweight='bold', color=pid_to_color[pid])
        ax_timeline.annotate(f't={arr_time}', (arr_time, -0.2), ha='center', va='top', fontsize=8)
        
    # 4. BARRAS APILADAS (WT + BURST)
    completed_sorted_pid = sorted(completed, key=lambda x: int(x['PID'][1:]))
    pids = [p['PID'] for p in completed_sorted_pid]
    arrivals = [p['Llegada'] for p in completed_sorted_pid]
    wts = [p['WT'] for p in completed_sorted_pid]
    bursts = [p['Burst'] for p in completed_sorted_pid]
    
    ax_bars.barh(pids, wts, left=arrivals, color='orange', label='Waiting Time (WT)')
    ax_bars.barh(pids, bursts, left=np.array(arrivals) + np.array(wts), color='tab:blue', label='Burst Time')
    ax_bars.set_title('Tiempos por Proceso (Waiting + Burst)', fontsize=10, pad=5)
    ax_bars.set_xlabel('Tiempo')
    ax_bars.invert_yaxis()
    ax_bars.legend(fontsize=8, loc='upper right')
    
    # 5. SCATTER WT/TAT/RT
    tats = [p['TAT'] for p in completed_sorted_pid]
    rts = [p['RT'] for p in completed_sorted_pid]
    
    ax_scatter.plot(pids, wts, marker='o', label='WT', color='orange')
    ax_scatter.plot(pids, tats, marker='s', label='TAT', color='green')
    ax_scatter.plot(pids, rts, marker='^', label='RT', color='red')
    ax_scatter.set_title('Métricas Individuales (WT, TAT, RT)', fontsize=10, pad=5)
    ax_scatter.set_ylabel('Tiempo')
    ax_scatter.legend(fontsize=8, loc='upper left')
    ax_scatter.grid(True, linestyle='--', alpha=0.6)
    
    # 6. TABLA PROCESOS
    ax_table.axis('off')
    table_data = []
    cols = ['Pos.', 'PID', 'Llegada', 'Burst', 'Inicio', 'Fin', 'WT', 'TAT', 'RT']
    completed_sorted = sorted(completed, key=lambda x: x['Pos.'])
    for p in completed_sorted:
        table_data.append([p['Pos.'], p['PID'], p['Llegada'], p['Burst'], p['Inicio'], p['Fin'], p['WT'], p['TAT'], p['RT']])
        
    table = ax_table.table(cellText=table_data, colLabels=cols, loc='center', cellLoc='center', bbox=[0.05, 0, 0.9, 1])
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    for (row, col), cell in table.get_celld().items():
        if row == 0:
            cell.set_text_props(weight='bold')
            cell.set_facecolor('#d9edf7')
            
    fig.savefig(save_path, bbox_inches='tight')
    plt.close(fig)

def plot_comparativa(all_metrics, save_path):
    df = pd.DataFrame(all_metrics)
    corridas = df['Corrida'].astype(str).tolist()
    
    wt = df['avg_waiting_time'].tolist()
    tat = df['avg_turnaround_time'].tolist()
    rt = df['avg_response_time'].tolist()
    cpu = df['cpu_utilization_%'].tolist()
    total_time = df['total_time'].tolist()
    
    x = np.arange(len(corridas))
    width = 0.25
    
    fig, ax1 = plt.subplots(figsize=(12, 6), dpi=150)
    
    rects1 = ax1.bar(x - width, wt, width, label='WT avg', color='#1f77b4')
    rects2 = ax1.bar(x, tat, width, label='TAT avg', color='#ff7f0e')
    rects3 = ax1.bar(x + width, rt, width, label='RT avg', color='#2ca02c')
    
    ax1.set_ylabel('Tiempo Promedio (Unidades)', color='black')
    ax1.set_title('Comparativa entre Corridas (Tiempos vs CPU Util. & Total Time)')
    ax1.set_xticks(x)
    ax1.set_xticklabels([f'C. {c}' for c in corridas])
    
    ax2 = ax1.twinx()
    line1 = ax2.plot(x, cpu, color='red', marker='o', linestyle='-', linewidth=2, label='CPU Util %')
    ax2.set_ylabel('CPU Utilization (%)', color='red')
    ax2.tick_params(axis='y', labelcolor='red')
    ax2.set_ylim(0, 110)
    
    ax3 = ax1.twinx()
    ax3.spines['right'].set_position(('outward', 60))      
    line2 = ax3.plot(x, total_time, color='purple', marker='s', linestyle='--', linewidth=2, label='Total Time')
    ax3.set_ylabel('Total Time', color='purple')
    ax3.tick_params(axis='y', labelcolor='purple')
    
    # Legend
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    lines3, labels3 = ax3.get_legend_handles_labels()
    ax1.legend(lines + lines2 + lines3, labels + labels2 + labels3, loc='upper left', bbox_to_anchor=(0, 1.15), ncol=5)
    
    fig.tight_layout()
    fig.savefig(save_path)
    plt.close(fig)

def main(k=5, n_procs=6):
    base_dir = "Ejecuciones"
    os.makedirs(base_dir, exist_ok=True)
    existing_execs = [d for d in os.listdir(base_dir) if d.startswith("Ejecucion_")]
    exec_num = 1
    if existing_execs:
        nums = [int(d.split("_")[1]) for d in existing_execs if d.split("_")[1].isdigit()]
        if nums:
            exec_num = max(nums) + 1
            
    current_exec_dir = os.path.join(base_dir, f"Ejecucion_{exec_num}")
    graficos_dir = os.path.join(current_exec_dir, "graficos")
    estadisticas_dir = os.path.join(current_exec_dir, "estadisticas")
    
    os.makedirs(graficos_dir, exist_ok=True)
    os.makedirs(estadisticas_dir, exist_ok=True)
    
    all_processes_data = []
    all_metrics = []
    
    for run_id in range(1, k + 1):
        seed = run_id * 42
        processes = generate_processes(n_procs, seed)
        completed, gantt, exec_order, idle_blocks = run_sjf(processes)
        metrics = compute_metrics(completed, gantt)
        
        for pos, p in enumerate(completed, 1):
            p['Pos.'] = pos
            p_data = {'Corrida': run_id, **p}
            all_processes_data.append(p_data)
            
        metrics['Corrida'] = run_id
        all_metrics.append(metrics)
        
        # Plot Dashboard for this run
        plot_path = os.path.join(graficos_dir, f'dashboard_corrida_{run_id}.png')
        plot_dashboard_corrida(completed, gantt, exec_order, idle_blocks, metrics, run_id, processes, plot_path)
        
        print(f"\n--- Corrida {run_id} ---")
        print(f"Orden SJF: {' → '.join(exec_order)}")
        
    # Plot Comparativa
    comp_plot_path = os.path.join(graficos_dir, 'comparativa_corridas.png')
    plot_comparativa(all_metrics, comp_plot_path)
    
    # Export Data
    df_metrics = pd.DataFrame(all_metrics)
    best_run = df_metrics.loc[df_metrics['avg_waiting_time'].idxmin()]
    worst_run = df_metrics.loc[df_metrics['avg_waiting_time'].idxmax()]
    
    df_all_proc = pd.DataFrame(all_processes_data)
    cols_order_all = ['Corrida', 'Pos.', 'PID', 'Llegada', 'Burst', 'Inicio', 'Fin', 'TAT', 'WT', 'RT']
    df_all_proc = df_all_proc[cols_order_all]
    
    csv_proc_path = os.path.join(estadisticas_dir, 'detalles_procesos_completos.csv')
    df_all_proc.to_csv(csv_proc_path, index=False)
    
    csv_metrics_path = os.path.join(estadisticas_dir, 'metricas_completas.csv')
    df_metrics.to_csv(csv_metrics_path, index=False)
    
    df_comp = df_metrics.copy()
    df_comp['mejor_WT'] = (df_comp['Corrida'] == best_run['Corrida'])
    df_comp['peor_WT'] = (df_comp['Corrida'] == worst_run['Corrida'])
    
    excel_path = os.path.join(estadisticas_dir, 'reporte_estadistico_completo.xlsx')
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        df_all_proc.to_excel(writer, sheet_name='Detalle_Procesos', index=False)
        df_metrics.to_excel(writer, sheet_name='Metricas_Corridas', index=False)
        df_comp.to_excel(writer, sheet_name='Comparacion', index=False)
        
    print("\n" + "="*60)
    print(" TABLA COMPARATIVA DE CORRIDAS ".center(60))
    print("="*60)
    
    df_metrics_show = df_metrics[['Corrida', 'avg_waiting_time', 'avg_turnaround_time', 'avg_response_time', 'throughput', 'cpu_utilization_%', 'total_time']].copy()
    df_metrics_show = df_metrics_show.round(2)
    print(tabulate(df_metrics_show, headers='keys', tablefmt='double_grid', showindex=False))
    
    print(f"\n[⭐] MEJOR corrida: Corrida {int(best_run['Corrida'])} (menor WT avg: {best_run['avg_waiting_time']:.2f})")
    print(f"[⚠️] PEOR corrida: Corrida {int(worst_run['Corrida'])} (mayor WT avg: {worst_run['avg_waiting_time']:.2f})")
    
    print(f"\nArchivos generados exitosamente en la carpeta: {current_exec_dir}")
    print(f" - Gráficos Dashboard guardados en: {os.path.abspath(graficos_dir)}\\")

if __name__ == '__main__':
    main()