import argparse

#set up parser to get input file name
parser = argparse.ArgumentParser()
parser.add_argument('filename', type=str)
args = parser.parse_args()

processCount = 0
totalTime = 0
quantum = 0 #only needed if we are using round robin
scheduler = ""
#list of dictionaries. Each process has three attributes
processes = []

#try to open the file. if successful get all the details we need
try:
  with open(args.filename, 'r') as file:

    for line in file:
      line.strip()

      if(line.startswith("processcount")):
        processCount = int(line.split()[1])

      elif(line.startswith("runfor")):
        totalTime = int(line.split()[1])

      elif(line.startswith("use")):
        scheduler = line.split()[1]

      elif(line.startswith("quantum")):
        quantum = int(line.split()[1])
      
      elif line.startswith("process"):
        newLine = line.split()
        processName = newLine[2]
        arrival = int(newLine[4])
        burst = int(newLine[6]) 
        processes.append({
            'name': processName,
            'arrival': arrival,
            'burst': burst
        })
except FileNotFoundError:
  print(args.filename + " not found")

#print to check if we got everything
print(str(processCount))
print(str(totalTime))
print(scheduler)
print(str(quantum))
for p in processes:
  print(p['name'] + " " + str(p['arrival']) + " " + str(p['burst']))

#begin chatgpt code
from collections import deque

def first_come_first_serve(processes, totalTime):
    processes.sort(key=lambda x: x['arrival'])
    current_time = 0
    wait_times = {}
    turnaround_times = {}
    response_times = {}
    
    for process in processes:
        arrival, burst = process['arrival'], process['burst']
        if current_time < arrival:
            print(f"Time {current_time}: idle")
            current_time = arrival
        print(f"Time {current_time}: Process {process['name']} selected")
        response_times[process['name']] = current_time - arrival
        wait_times[process['name']] = current_time - arrival
        current_time += burst
        turnaround_times[process['name']] = current_time - arrival
        print(f"Time {current_time}: Process {process['name']} finished")
    
    print("\nFinal Results:")
    for name in wait_times:
        print(f"Process {name}: Wait Time = {wait_times[name]}, Turnaround Time = {turnaround_times[name]}, Response Time = {response_times[name]}")
    
    return turnaround_times

def shortest_job_first_preemptive(processes, totalTime):
    processes.sort(key=lambda x: (x['arrival'], x['burst']))
    remaining_time = {p['name']: p['burst'] for p in processes}
    current_time = 0
    wait_times = {}
    turnaround_times = {}
    response_times = {}
    completed = set()
    ready_queue = []
    
    while len(completed) < len(processes):
        available = [p for p in processes if p['arrival'] <= current_time and p['name'] not in completed]
        available.sort(key=lambda x: remaining_time[x['name']])
        
        if available:
            current_process = available[0]
            if current_process['name'] not in response_times:
                response_times[current_process['name']] = current_time - current_process['arrival']
            print(f"Time {current_time}: Process {current_process['name']} selected")
            remaining_time[current_process['name']] -= 1
            current_time += 1
            if remaining_time[current_process['name']] == 0:
                completed.add(current_process['name'])
                turnaround_times[current_process['name']] = current_time - current_process['arrival']
                wait_times[current_process['name']] = turnaround_times[current_process['name']] - current_process['burst']
                print(f"Time {current_time}: Process {current_process['name']} finished")
        else:
            print(f"Time {current_time}: idle")
            current_time += 1
    
    print("\nFinal Results:")
    for name in wait_times:
        print(f"Process {name}: Wait Time = {wait_times[name]}, Turnaround Time = {turnaround_times[name]}, Response Time = {response_times[name]}")
    
    return turnaround_times

def round_robin(processes, totalTime, quantum):
    processes.sort(key=lambda x: x['arrival'])
    current_time = 0
    completion_times = {}
    process_info = {p['name']: {'arrival': p['arrival'], 'burst': p['burst'], 'status': 'arrived'} for p in processes}
    wait_times = {p['name']: 0 for p in processes}
    turnaround_times = {}
    response_times = {}
    ready_queue = deque()
    remaining_processes = processes[:]
    remaining_burst = {p['name']: p['burst'] for p in processes}
    in_queue = set()
    
    while remaining_processes or ready_queue:
        while remaining_processes and remaining_processes[0]['arrival'] == current_time:
            process = remaining_processes.pop(0)
            print(f"Time {current_time}: Process {process['name']} arrives")
            ready_queue.append(process['name'])
            in_queue.add(process['name'])
            process_info[process['name']]['status'] = 'arrived'
        
        if ready_queue:
            current_process = ready_queue.popleft()
            in_queue.remove(current_process)
            
            if current_process not in response_times:
                response_times[current_process] = current_time - process_info[current_process]['arrival']
            
            print(f"Time {current_time}: Process {current_process} selected")
            process_info[current_process]['status'] = 'selected'
            execution_time = min(quantum, remaining_burst[current_process])
            remaining_burst[current_process] -= execution_time
            current_time += execution_time
            
            while remaining_processes and remaining_processes[0]['arrival'] <= current_time:
                process = remaining_processes.pop(0)
                print(f"Time {process['arrival']}: Process {process['name']} arrives")
                ready_queue.append(process['name'])
                in_queue.add(process['name'])
                process_info[process['name']]['status'] = 'arrived'
            
            if remaining_burst[current_process] > 0:
                ready_queue.append(current_process)
                in_queue.add(current_process)
            else:
                print(f"Time {current_time}: Process {current_process} finished")
                completion_times[current_process] = current_time
                turnaround_times[current_process] = current_time - process_info[current_process]['arrival']
                wait_times[current_process] = turnaround_times[current_process] - process_info[current_process]['burst']
                process_info[current_process]['status'] = 'finished'
        else:
            print(f"Time {current_time}: idle")
            current_time += 1
    
    print("\nFinal Results:")
    for name in process_info:
        print(f"Process {name}: Wait Time = {wait_times[name]}, Turnaround Time = {turnaround_times[name]}, Response Time = {response_times[name]}")
    
    return completion_times

# Run the selected scheduler based on the variable 'scheduler'
if scheduler == "fcfs":
    first_come_first_serve(processes, totalTime)
elif scheduler == "sjf":
    shortest_job_first_preemptive(processes, totalTime)
elif scheduler == "rr":
    round_robin(processes, totalTime, quantum)
else:
    print("Invalid scheduler selected.")