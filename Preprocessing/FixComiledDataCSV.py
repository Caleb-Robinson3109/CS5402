f = open("CompiledData.csv")

g = open("CompiledDataFix.csv", "w")

for line in f.readlines():
    
    if len(line) == 1 or len(line) == 0:
        continue
    lineContent = line.split(",")
    if len(lineContent) != 14:
        continue
    
    if "nan" in lineContent:
        continue
    #print(lineContent[-qq])
    g.write(line)
    if line[-1] != "\n":
        g.write("\n")
f.close()
g.close()