from numpy import array,random,exp,pi,sqrt,ones,arange,append,sign,isnan,zeros,fabs,nan_to_num
import sys
import time
#import psyco
#psyco.full()
def import2D(path):
    # expecting space delimited float data, 6 line header
    data = []
    dataFile = open(path,'r')
    data = dataFile.read().split('\n')
    dataFile.close()
    global south
    south = float(data[1].split(':')[-1])
    global west
    west = float(data[3].split(':')[-1])
    data = data[6:-1]
    for i in range(len(data)):
        data[i] = map(float,data[i].split())
    return array(data)

def timePass(start,end):
    start = start.split()[3].split(':')
    end = end.split()[3].split(':')
    hr = float(end[0])-float(start[0])
    minute = float(end[1])-float(start[1])
    sec = float(end[2])-float(start[2])
    if sec < 0: 
        minute -= 1.
        sec += 60.
    if minute < 0: 
        hr -= 1.
        minute += 60.
    if hr < 0: 
        hr += 24.
    return str(int(hr))+':'+str(int(minute))+':'+str(int(sec))

def write(r,path):
    global south
    global west
    try: 
        Fout = open(path,'w')
    except:
        print 'file not found in writeWalkLoc'
        return 1
    x = r.transpose()[0]
    r = r[~isnan(x)&(x!=0)] + [west,south]
    l = len(r)
    c = [',']*l; n = [',1\n']*l
    r = r.transpose().astype('|S13')
    r = array([r[0],c,r[1],n])
    Fout.write(''.join(r.transpose().flatten()))
    Fout.close()

def getVelocities(r):
    l = len(r)
    a = float('nan'); v = zeros((l,2))*a
    r = r.transpose()
    x = r[0].astype(int); y = (rows-r[1]-1).astype(int)
    b = (y>0)&(y<rows)&(x>0)&(x<cols)
    x = x.tolist(); y = y.tolist()
    for i in arange(l)[b].tolist():
        v[i] = D[y[i]][x[i]]
    return v

###########
# input data

dx = import2D('/home/eric/Desktop/classes/CompPhys/project/secref_dx_1m')
dy = import2D('/home/eric/Desktop/classes/CompPhys/project/secref_dy_1m')
rows, cols = len(dx), len(dx[0])
A = rows*cols 
D = []
for row in range(rows):
    D.append([])
    for col in range(cols):
        D[-1].append([dx[row][col],dy[row][col]])

###########
# constants and initializations
c = 0.8 # v=-c*del(z)
D = c*array(D) # multiply D by c so that is isn't done in a loop
tau = 1/1.414/max(D.flatten()) # time step
T = 2000*tau # max time
N = 0.01*A # number of total walkers
r = zeros((N,2)) # array for walker positions
M_tau = int(N*tau/T) # number of generated walkers per iteration
#S0 = 0.000010 # mm/hr; default = 50
#rain_step = S0*T/float(N)
###########
# IC
M_walk = 0 # current number of walkers
# generate initial positions for all walkers generated during the simulation
new_walkers = random.random((int(T/tau),M_tau,2))
new_walkers[:,:,0] = new_walkers[:,:,0]*cols
new_walkers[:,:,1] = new_walkers[:,:,1]*rows
path = '/home/eric/Desktop/classes/CompPhys/project/pictures/'
p = 0; start = time.ctime()
for i in range(int(T/tau)):
    # realize new walkers
    r[M_walk:M_walk+M_tau] = new_walkers[i]
    M_walk += M_tau
    # propogate walkers
    v = getVelocities(r[:M_walk])
    G = random.normal(v*tau,sqrt(2*tau))/(4*pi*tau)
    r[:M_walk] += tau*v + G
    if i%50==0: write(r[:M_walk],path+'wdepth_'+ (len(str(int(T/tau)))-len(str(i)))*'0'+ str(i))
    sys.stderr.write('='*(i*50/int(T/tau)-p)); p = i*50/int(T/tau) # progress bar

end = time.ctime(); print timePass(start,end)
path = '/home/eric/Desktop/classes/CompPhys/project/'
fname = 'wdepth_T'+str(int(T/tau))+'_N'+str(int(N/A))+'A_c'+str(int(c*10))
#write(r,path+fname)

