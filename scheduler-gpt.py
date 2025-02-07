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
    
    #no check for if we are going over the totalTime
    for process in processes:
        arrival, burst = process['arrival'], process['burst']
        while current_time < arrival:
            print(f"Time {current_time}: idle")
            current_time += 1
        print(f"Time {current_time}: Process {process['name']} selected")
        response_times[process['name']] = current_time - arrival
        wait_times[process['name']] = current_time - arrival
        current_time += burst
        turnaround_times[process['name']] = current_time - arrival
        print(f"Time {current_time}: Process {process['name']} finished")
    
    while current_time < totalTime:
        print(f"Time {current_time}: idle")
        current_time += 1
    
    print(f"Finished at time {current_time}")
    print("\nFinal Results:")
    for name in wait_times:
        print(f"Process {name}: Wait Time = {wait_times[name]}, Turnaround Time = {turnaround_times[name]}, Response Time = {response_times[name]}")
    
    return turnaround_times

def shortest_job_first_preemptive(processes, totalTime):
    #sort processes by arrival time and burst if arrival times ie equal
    processes.sort(key=lambda x: (x['arrival'], x['burst']))
    #set up remaining time (reaminig time equals the burst time at the beginning)
    remaining_time = {p['name']: p['burst'] for p in processes}
    current_time = 0
    wait_times = {}
    turnaround_times = {}
    response_times = {}
    completed = set()
    
    #while we still have processes to finish and time to kill
    #this should be an AND not an OR
    while len(completed) < len(processes) and current_time < totalTime:
        #mark available if the arrival time is already passed and if the process is not complete
        available = [p for p in processes if p['arrival'] <= current_time and p['name'] not in completed]
        #sort available list by remainig time to find the shortest to completion
        available.sort(key=lambda x: remaining_time[x['name']])
        
        #choose the first available process
        if available:
            current_process = available[0]
            #add the process to the list of response times for metrics later
            if current_process['name'] not in response_times:
                response_times[current_process['name']] = current_time - current_process['arrival']
            print(f"Time {current_time}: Process {current_process['name']} selected") #prints "selected" for every time stamp
            #sets the remaining time of that process to its value minus one
            remaining_time[current_process['name']] -= 1
            #if the process has finished, add it to the completed list, find the turnaround time, find the wait time, and print that the process has finished
            if remaining_time[current_process['name']] == 0:
                completed.add(current_process['name'])
                turnaround_times[current_process['name']] = current_time + 1 - current_process['arrival']
                wait_times[current_process['name']] = turnaround_times[current_process['name']] - current_process['burst']
                print(f"Time {current_time + 1}: Process {current_process['name']} finished")
        #prints idle if nothing is available
        else:
            print(f"Time {current_time}: idle")
        current_time += 1
    
    print(f"Finished at time {current_time}")
    print("\nFinal Results:")
    for name in wait_times:
        print(f"Process {name}: Wait Time = {wait_times[name]}, Turnaround Time = {turnaround_times[name]}, Response Time = {response_times[name]}")
    
    return turnaround_times

#this function includes completion times for some reason
def round_robin(processes, totalTime, quantum):
    #sorts processes by arrival time
    processes.sort(key=lambda x: x['arrival'])
    current_time = 0
    completion_times = {}
    #sets up wait time list and adds each process to it
    wait_times = {p['name']: 0 for p in processes}
    turnaround_times = {}
    response_times = {}
    ready_queue = deque()
    remaining_processes = processes[:]
    #stores burst times of each process
    remaining_burst = {p['name']: p['burst'] for p in processes}
    in_queue = set()
    
    #this should be an AND not an OR for the totalTime check
    while (remaining_processes or ready_queue) and current_time < totalTime:
        #adds processes that arrive at the current time to the ready queue
        while remaining_processes and remaining_processes[0]['arrival'] == current_time:
            process = remaining_processes.pop(0)
            print(f"Time {current_time}: Process {process['name']} arrives")
            ready_queue.append(process['name'])
            in_queue.add(process['name'])
        #if there is stuff in the queue, select the first one to be run 
        if ready_queue:
            current_process = ready_queue.popleft()
            in_queue.remove(current_process)
            
            #adds the process to response time for metrics
            if current_process not in response_times:
                response_times[current_process] = current_time - next(p['arrival'] for p in processes if p['name'] == current_process)
            
            #run process for the quantum time or until it is done
            print(f"Time {current_time}: Process {current_process} selected")
            execution_time = min(quantum, remaining_burst[current_process])
            remaining_burst[current_process] -= execution_time
            current_time += execution_time
            
            #handles arrivals while a process is working
            while remaining_processes and remaining_processes[0]['arrival'] <= current_time:
                process = remaining_processes.pop(0)
                print(f"Time {process['arrival']}: Process {process['name']} arrives")
                ready_queue.append(process['name'])
                in_queue.add(process['name'])
            
            #put the process back in the queue if it isnt done
            if remaining_burst[current_process] > 0:
                ready_queue.append(current_process)
                in_queue.add(current_process)
            #otherwise, the process is finished
            else:
                print(f"Time {current_time}: Process {current_process} finished")
                completion_times[current_process] = current_time
                turnaround_times[current_process] = current_time - next(p['arrival'] for p in processes if p['name'] == current_process)
                wait_times[current_process] = turnaround_times[current_process] - next(p['burst'] for p in processes if p['name'] == current_process)
        else:
            print(f"Time {current_time}: idle")
            current_time += 1
    
    print(f"Finished at time {current_time}")
    print("\nFinal Results:")
    for name in wait_times:
        print(f"Process {name}: Wait Time = {wait_times[name]}, Turnaround Time = {turnaround_times[name]}, Response Time = {response_times[name]}")
    
    return completion_times

# Decide which function to run based on the scheduler type
if scheduler == "fcfs":
    first_come_first_serve(processes, totalTime)
elif scheduler == "sjf":
    shortest_job_first_preemptive(processes, totalTime)
elif scheduler == "rr":
    round_robin(processes, totalTime, quantum)
else:
    print("Invalid scheduler type.")
