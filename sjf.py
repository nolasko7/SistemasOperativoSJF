import pandas as pd

def run_sjf(processes_df):
    """
    Ejecuta el algoritmo SJF (Shortest Job First) No-Preemptivo.
    """
    # Convertir DataFrame a lista de diccionarios y ordenar inicialmente por llegada
    processes = processes_df.to_dict('records')
    processes.sort(key=lambda x: x['arrival_time'])
    
    n = len(processes)
    completed = 0
    current_time = 0
    
    result = []
    is_completed = [False] * n
    
    total_burst = sum(p['burst_time'] for p in processes)
    
    while completed != n:
        # Buscar el proceso que ya haya llegado con la ráfaga (burst) más corta
        min_burst = float('inf')
        idx_to_run = -1
        
        for i in range(n):
            if processes[i]['arrival_time'] <= current_time and not is_completed[i]:
                if processes[i]['burst_time'] < min_burst:
                    min_burst = processes[i]['burst_time']
                    idx_to_run = i
                # En caso de empate en ráfaga, el primero que llegó se prioriza
                # (como ya está ordenado por arrival_time, no es necesario hacer más)
        
        if idx_to_run != -1:
            # Encontramos un proceso para ejecutar
            p = processes[idx_to_run]
            start_time = current_time
            completion_time = start_time + p['burst_time']
            turnaround_time = completion_time - p['arrival_time']
            waiting_time = turnaround_time - p['burst_time']
            response_time = start_time - p['arrival_time']
            
            result.append({
                'PID': p['PID'],
                'arrival_time': p['arrival_time'],
                'burst_time': p['burst_time'],
                'start_time': start_time,
                'completion_time': completion_time,
                'turnaround_time': turnaround_time,
                'waiting_time': waiting_time,
                'response_time': response_time
            })
            
            is_completed[idx_to_run] = True
            completed += 1
            current_time = completion_time
        else:
            # Ningún proceso ha llegado en el tiempo actual, avanzar 1 tick
            current_time += 1
            
    result_df = pd.DataFrame(result)
    
    # Calcular Métricas
    first_arrival = min(p['arrival_time'] for p in processes) if n > 0 else 0
    time_elapsed = current_time - first_arrival
    
    avg_wt = result_df['waiting_time'].mean()
    avg_tat = result_df['turnaround_time'].mean()
    throughput = n / time_elapsed if time_elapsed > 0 else 0
    cpu_utilization = (total_burst / time_elapsed * 100) if time_elapsed > 0 else 0
    
    metrics = {
        'avg_waiting_time': avg_wt,
        'avg_turnaround_time': avg_tat,
        'throughput': throughput,
        'cpu_utilization': cpu_utilization
    }
    
    return result_df, metrics
