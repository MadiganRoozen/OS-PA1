
import argparse

#set up parser to get input file name
parser = argparse.ArgumentParser()
parser.add_argument('filename', type=str)
args = parser.parse_args()

processCount = 0
totalTime = 0
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
for p in processes:
  print(p['name'] + " " + str(p['arrival']) + " " + str(p['burst']))
