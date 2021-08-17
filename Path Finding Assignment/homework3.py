import heapq

# BFS code
def checkIsSafe(newx, newy, currMVal, maxRockHt, grid, row, col):
    if ((newx>=0 and newx<row) and (newy>=0 and newy<col)):  
        newm  = grid[newx][newy]
        if(currMVal >= 0 and newm >= 0):
            return True
        if(currMVal >= 0):
            currMVal = 0
        if(newm >= 0):
            newm = 0 
        diff = abs(currMVal-newm)
        if(diff <= maxRockHt):
            return True
    return False

def runBFS(grid, src, dest, maxRockHt):
    row = len(grid)
    col = len(grid[0])
    visited = [[False for j in range(col)] for i in range(row)]
    f = False
    parent, queue = [], []
    x = [1, 1, 0, -1, -1, -1, 0, 1]
    y = [0, -1, -1, -1, 0, 1, 1 , 1]
    for i in range(row):
        parent.append([-1]*col)
    parent[src[0]][src[1]] = None
    queue.append((src[0], src[1]))
    visited[src[0]][src[1]] = True
    while(len(queue)):
        t = queue.pop(0)
        currx, curry = t[0], t[1]
        currMVal = grid[currx][curry]
        if(currx == dest[0] and curry == dest[1]):
            f = True
            break
        for k in range(0, 8):
            newx = currx + x[k]
            newy = curry + y[k]
            if(checkIsSafe(newx, newy, currMVal, maxRockHt, grid, row, col)):    # if move is safe-> add to queue
                if(visited[newx][newy] == False):
                    visited[newx][newy] = True
                    queue.append((newx, newy))
                    parent[newx][newy] = [currx, curry]
    if(f and parent[dest[0]][dest[1]] != -1):
        path = getPath(parent, dest, src)[::-1]
    else:
        path = "FAIL"
    return path

# USC code
def checkSafe(newx, newy, currMVal, maxht, grid, row, col):
    if((newx>=0 and newx<row) and (newy>=0 and newy<col)):
        newm  = grid[newx][newy]
        curr, new = currMVal, newm
        if(currMVal >= 0 and newm >= 0):
            return True
        if(currMVal >= 0):
            curr = 0
        if(newm >= 0):
            new = 0 
        diff = abs(curr-new)
        if(diff <= maxRockHt):
            return True
    return False

def getPath(parent, target, src):
    path = [target[::-1]]
    j, i = path[-1][0], path[-1][1]
    while(parent[i][j] is not None):
        path.append(parent[i][j][::-1])
        j, i = path[-1][0], path[-1][1]
    return path

def runUCS(grid, src, target, maxht):
    row = len(grid)
    col = len(grid[0])
    visited = set()
    f = False
    dist, parent, queue = [], [], []
    x = [1, 1, 0, -1, -1, -1, 0, 1]
    y = [0, -1, -1, -1, 0, 1, 1 , 1]
    for i in range(row):
        dist.append([float('Inf')]*col)
        parent.append([-1]*col)
    dist[src[0]][src[1]] = 0
    parent[src[0]][src[1]] = None
    heapq.heappush(queue, (0, (src[0], src[1])))
    # traverse till queue is not empty
    while(len(queue)):
        u = heapq.heappop(queue)   # [i, j] format
        if(list(u[1]) == target): # result is found
            f = True
            break
        if(u[1] in visited):
            continue
        else:
            visited.add((u[1][0], u[1][1]))
        currMVal = grid[u[1][0]][u[1][1]]
        # find 8 neighbours of u
        for k in range(8):
            newx = u[1][0] + x[k] 
            newy = u[1][1] + y[k]
            if(checkSafe(newx, newy, currMVal, maxht, grid, row, col)):
                if(k in [1,3,5,7]):     # diagonal elements
                    if(14+dist[u[1][0]][u[1][1]] < dist[newx][newy]):
                        dist[newx][newy] = 14 + dist[u[1][0]][u[1][1]]                 
                        parent[newx][newy] = [u[1][0], u[1][1]]
                        heapq.heappush(queue, (dist[newx][newy], (newx, newy)))
                else:   # non diagonal elements
                    if(10+dist[u[1][0]][u[1][1]] < dist[newx][newy]):
                        dist[newx][newy] = 10 + dist[u[1][0]][u[1][1]]
                        parent[newx][newy] = [u[1][0], u[1][1]]
                        heapq.heappush(queue, (dist[newx][newy], (newx, newy)))
    if(f and parent[target[0]][target[1]] != -1):
        path = getPath(parent, target, src)[::-1]
    else:
        path = "FAIL"
    return path

# A star Code
def calcHValue(grid, curr ,target, row, col):
    xval = (curr[1] - target[1])**2
    yval = (curr[0] - target[0])**2
    d = 9.85
    hval = d*((xval+yval)**0.5)
    return hval

def runAStar(grid, src, target, maxht):
    row = len(grid)
    col = len(grid[0])
    f = False
    cht, nht, mud, cost = 0, 0, 0, 0
    dist, parent, queue = [], [], []
    x = [1, 1, 0, -1, -1, -1, 0, 1]
    y = [0, -1, -1, -1, 0, 1, 1 , 1]
    for i in range(row):
        dist.append([float('Inf')]*col)
        parent.append([-1]*col)
    dist[src[0]][src[1]] = 0
    parent[src[0]][src[1]] = None
    heapq.heappush(queue, [0, (src[0], src[1])])
    #traverse till queue is not empty or target is reached
    while(len(queue)):
        u = heapq.heappop(queue)
        if(u[1][0] == target[0] and u[1][1] == target[1]):
            f = True
            break
        if(grid[u[1][0]][u[1][1]] < 0):
            cht = grid[u[1][0]][u[1][1]]
        else:
            cht = 0
        h = 0
        currMVal = grid[u[1][0]][u[1][1]]
        # find 8 neighbors of u 
        for k in range(8):
            newx = u[1][0] + x[k]
            newy = u[1][1] + y[k]
            if(checkSafe(newx, newy, currMVal, maxht, grid, row, col)):
                h = calcHValue(grid, [newx, newy] ,target, row, col)
                if(grid[newx][newy]<0):
                    nht = grid[newx][newy]
                    mud = 0
                else:
                    mud = grid[newx][newy]
                    nht = 0
                if(k in [1,3,5,7]):  # diagonal elements
                    cost = 14 + mud + abs(nht - cht) + dist[u[1][0]][u[1][1]]
                else:   # non diagonal elements
                    cost = 10 + mud + abs(nht - cht) + dist[u[1][0]][u[1][1]]
                if(cost < dist[newx][newy]):
                    dist[newx][newy] = cost
                    parent[newx][newy] = [u[1][0], u[1][1]]
                    heapq.heappush(queue, [ cost+h, (newx, newy)])
    if(f and parent[target[0]][target[1]] != -1):
        path = getPath(parent, target, src)[::-1]
    else:
        path = "FAIL"
    return path

#Write to Output file
def writeToFile(allPaths, zz = 1):
    # f = open("Scripts/Inputs/AStar/output"+str(zz)+".txt", "w")
    f = open("Scripts/Inputs/output11aStar.txt", "w")
    for i, val in enumerate(allPaths):
        if(val == "FAIL"):
            f.write("FAIL")
        else:
            strP = ""
            for x, y in val:
                strP += str(x)+","+str(y)+" "
            f.write(strP.strip())
        f.write('\n')
    f.close()

# file open "input.txt" and get the initial variables ready
# for zz in range(1, 11):
#     filename = "input"+str(zz) +".txt"
#     print("Started input"+ str(zz))
    # f = open("Scripts/Inputs/AStar/"+filename, "r")
f = open("Scripts/Inputs/input11.txt", "r")
algo = f.readline().split("\n")[0]
gridstruc = f.readline().split(" ")
w, h = int(gridstruc[0]), int(gridstruc[1])
src = f.readline().split(" ")
src = [int(src[0]), int(src[1])]
maxRockHt = int(f.readline().split("\n")[0])
nss = int(f.readline().split("\n")[0])
settlingSites = []
for i in range(nss):
    line = f.readline().split(" ")
    ssx, ssy = int(line[0]), int(line[1].split("\n")[0])
    settlingSites.append([ssx,ssy])
grid = []
for x in range(h):
    temprow = f.readline().split(" ")
    row = []
    tn = len(temprow)
    for i, val in enumerate(temprow):
        if(val == ""):
            None
        elif(i == tn-1):
            if(val != "" and val.split("\n")[0] != ""):
                row.append(int(val.split("\n")[0]))
            elif(val != "" and val != "\n"):
                row.append(int(val))
        else:
            row.append(int(val))
    grid.append(row)
f.close()
# run the 3 algorithms
allPaths = []
if(algo == "BFS"):      # run bfs
    src = src[::-1]
    for val in settlingSites:
        val = val[::-1]
        res = runBFS(grid, src, val, maxRockHt)
        allPaths.append(res)
elif(algo == "UCS"):    # run uniform cost search
    src = src[::-1]
    for val in settlingSites:
        val = val[::-1]
        res = runUCS(grid, src, val, maxRockHt)
        allPaths.append(res)
elif(algo == "A*"):     # run A* 
    src = src[::-1]
    for val in settlingSites:
        val = val[::-1]
        res = runAStar(grid, src, val, maxRockHt)
        allPaths.append(res)

# write to output file
writeToFile(allPaths)
