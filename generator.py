import random
import pandas as pd
import os

def generate_processes(num_processes=5, run_id=1, output_dir="results"):
    """
    Genera N procesos con tiempos de llegada y ráfagas de CPU aleatorios.
    """
    processes = []
    for i in range(1, num_processes + 1):
        pid = f"P{i}"
        arrival_time = random.randint(0, 20)
        burst_time = random.randint(1, 15)
        processes.append({
            "PID": pid,
            "arrival_time": arrival_time,
            "burst_time": burst_time
        })
    
    df = pd.DataFrame(processes)
    
    # Crear directorio si no existe
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, f"run_{run_id}.csv")
    
    # Guardar en CSV
    df.to_csv(file_path, index=False)
    return df
