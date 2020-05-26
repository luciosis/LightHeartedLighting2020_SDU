import matplotlib.pyplot as plt
import matplotlib.dates as md
import numpy as np
from datetime import datetime as dt
import time
import statistics
import matplotlib.ticker as ticker


#filename = "logs.csv"
#filename = "logssetpointtestjacob.csv"
#filename = "logsetpointtestsimon.csv"
filename = "logs_18_05_2020.csv"
#filename = "logs_15_05_2020.csv"
isaverage = False
haszero = True
datetimeformat = '%Y-%m-%d %H:%M:%S'
#datetimeformat = '%d/%m/%Y %H.%M'
delta = []
avg = []
calclist = []
intensity_list = []

def fillDelta():
    f = open(filename, "r")
    lux = 4
    b = 5
    count = 0
    for line in f:
        if(isaverage): 
            if (count == 120):
                avg.append(statistics.mean(delta))
                delta.clear()
                count = 0

        if line.split(";")[6] != 'send' and line.split(";")[7] == "Jacob's device":
            fval = float(line.split(";")[lux])
            intensity = float(line.split(";")[lux+1])
            intensity_list.append(intensity)
            #fval = float(lightvalues.split(",")[1][:-2])
            if (fval != 0 or haszero):
                delta.append(fval)
            
            count += 1
        
        
    if (isaverage):
        calclist = avg
    else:
        calclist = delta

    f.close()


def setBucketsLog():
    ## Begin buckets
    cmax = max(calclist)
    cmin = min(calclist)
    dif = cmax-cmin
    number_of_buckets = 51
    buckets = [[] for i in range(number_of_buckets)]
    interval = dif / number_of_buckets


    log = np.logspace(start=0, stop=3, num=number_of_buckets)
    log = log*25
    zeroarr = np.array([0])
    log = np.concatenate((zeroarr, log))

    for j in range(0, len(calclist)):
        for i in range(0,len(log)):
            if (calclist[j] < 25000):
                if (calclist[j] >= log[i] and calclist[j] < log[i+1]):
                    buckets[i].append(calclist[j])



'''
# Plot without timestamps

time = []
for i in range(0, len(calclist)):
    time.append(i)

plt.plot(time,calclist)
plt.ylabel("Lux value")
plt.xlabel("Time")
plt.show()
'''
#f = open("logs_18_05_2020.csv", "r")


def plotlatency():
    f = open(filename, "r")
    slatency = []
    sdevice = "Simon's device"
    jlatency = []
    jdevice = "Jacob's device"
    fval = 0
    savg = []
    javg = []
    c = 900
    count = 0

    lc = 0

    e2e_latency = []

    for line in f:
        
        if line.split(";")[6] == 'send' and line.split(";")[5] == sdevice:
            fval = float(line.split(";")[2])
        elif line.split(";")[7] == sdevice:
            fval = float(line.split(";")[3])
        
        slatency.append(fval/float(1000000))
        
        if line.split(";")[6] == 'send' and line.split(";")[5] == jdevice:
            fval = float(line.split(";")[2])
        elif line.split(";")[7] == jdevice:
            fval = float(line.split(";")[3])
        
        if(fval/1000000 > 50):
            jlatency.append(float(1))
        else:
            jlatency.append(fval/float(1000000))
        
        '''
        if(fval/1000000 > 50):
            lc += 1

        '''

        if (line.split(";")[6] == 'recieved' and line.split(";")[5] == jdevice):
            e2e_latency.append(float(line.split(";")[2]) / float(1000000))
            print(float(line.split(";")[2]))

        

        count += 1
        if (count == c):
            savg.append(float(sum(slatency)/len(slatency)))
            javg.append(float(sum(jlatency)/len(jlatency)))
            slatency.clear()
            jlatency.clear()
            count = 0

    f.close()


    '''

    #rng = np.random.RandomState(10)  # deterministic random data
    #a = np.hstack((rng.normal(size=1000), rng.normal(loc=5, scale=2, size=1000)))
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1,)
    n, bins, patches = plt.hist(slatency, bins=50, rwidth=0.5, range=[0,1.3], histtype='bar', label="Simon")  # arguments are passed to np.histogram
    n, bins, patches = plt.hist(jlatency, bins=50, rwidth=0.5, range=[0,1.3], histtype='bar', label="Jacob")
    plt.legend(bbox_to_anchor=(1.04, 0.5), loc='upper left', ncol=1)

    plt.title("Histogram of data with 50 buckets")
    plt.xlabel("Latency in seconds")
    plt.ylabel("Observed packets with latency")

        
    #plots the histogram
    fig, ax1 = plt.subplots()
    colors = ['b','g']
    ax1.hist([slatency,jlatency],color=colors, bins=50, rwidth=0.5, range=[0,1.3], histtype='bar')
    #ax1.set_xlim(-10,10)
    ax1.set_ylabel("Count")
    plt.tight_layout()
    plt.show()
    '''
    firsttimestamp = "2020-05-12 13:25:06"
    last_line = "2020-05-18 10:16:42"

    datetime_object = dt.strptime(firsttimestamp, datetimeformat)
    last_datetime_object = dt.strptime(last_line, datetimeformat)
    #n=len(jlatency)
    n = len(javg)
    now=datetime_object.timestamp() + 7200
    last=last_datetime_object.timestamp() + 7200
    timestamps=np.linspace(now,last,n)
    dates=[dt.fromtimestamp(ts) for ts in timestamps]
    datenums=md.date2num(dates)

    n2 = len(e2e_latency)
    now2=datetime_object.timestamp() + 7200
    last2=last_datetime_object.timestamp() + 7200
    timestamps2=np.linspace(now2,last2,n2)
    dates2=[dt.fromtimestamp(ts) for ts in timestamps2]
    datenums2=md.date2num(dates2)


    plt.subplots_adjust(bottom=0.2)
    plt.xticks(rotation=60)

    ax=plt.gca()
    xfmt = md.DateFormatter("%d-%m %H:%M")
    hours = md.HourLocator(interval = 12)
    ax.xaxis.set_major_locator(hours)
    ax.xaxis.set_major_formatter(xfmt)

    
    plt.xlabel("Timestamp 12 hour apart")
    plt.ylabel("Latency in seconds")
    #plt.plot(datenums,savg, label="Simon latency")
    #plt.plot(datenums,javg, color="red", label="Jacob latency")
    
    plt.plot(datenums2,e2e_latency, "o", color="green", label="Edge to edge \nlatency")
    plt.legend(bbox_to_anchor=(1.01, 0.5), loc='upper left', ncol=1)
    plt.show()



    
    


def plotlight():
    f = open(filename, "r")
    firsttimestamp = f.readline().split(';')[2]
    last_line = f.read().splitlines()[-1].split(';')[2]

    print(firsttimestamp)
    print(last_line)
    lux = 4
    b = 5
    count = 0
    for line in f:
        if(isaverage): 
            if (count == 120):
                avg.append(statistics.mean(delta))
                delta.clear()
                count = 0

        if line.split(";")[6] != 'send' and line.split(";")[7] == "Jacob's device":
            fval = float(line.split(";")[lux])
            intensity = float(line.split(";")[lux+1])
            intensity_list.append(intensity)
            #fval = float(lightvalues.split(",")[1][:-2])
            if (fval != 0 or haszero):
                delta.append(fval)
            
            count += 1
        
        
    if (isaverage):
        calclist = avg
    else:
        calclist = delta

    datetime_object = dt.strptime(firsttimestamp, datetimeformat)
    last_datetime_object = dt.strptime(last_line, datetimeformat)
    f.close()

    #plot with timestamps
    print(len(calclist))
    n=len(calclist)
    now=datetime_object.timestamp() + 7200
    last=last_datetime_object.timestamp() + 7200
    timestamps=np.linspace(now,last,n)
    dates=[dt.fromtimestamp(ts) for ts in timestamps]
    datenums=md.date2num(dates)
    plt.subplots_adjust(bottom=0.2)
    plt.xticks(rotation=60)

    ax=plt.gca()
    xfmt = md.DateFormatter("%d-%m %H:%M")
    hours = md.HourLocator(interval = 6)
    ax.xaxis.set_major_locator(hours)
    ax.xaxis.set_major_formatter(xfmt)


    plt.xlabel("Timestamp 6 hour apart")
    plt.ylabel("Measured lux value")
    plt.plot(datenums,calclist)
    #plt.plot(datenums, calclist)
    plt.show()


def normalizedLux():
    f = open(filename, "r")
    #s = open("normalizeddata_simon_day", "w")
    #j = open("normalizeddata_jacob_day", "w")
    #l = open("normalizeddata_intensity_jacob", "w")
    ls = open("normalizeddata_intensity_simon", "w")
  
    deltajacob = []
    deltasimon = []

    print("start normalized")
    
    ''' 
    for line in f:
     
        if line.split(";")[6] != 'send' and line.split(";")[7] == "Jacob's device":
            fval = float(line.split(";")[5])
            if ((fval != 0 or haszero)):
                deltajacob.append(fval)
                
            
        

        if line.split(";")[6] != 'send' and line.split(";")[7] == "Simon's device":
            fval = float(line.split(";")[5])
            deltasimon.append(fval)
         '''

    deltasimon = intensity_list
    jmin = min(deltasimon)
    jmax = max(deltasimon)

    for i in deltasimon:
        n = (i - jmin) / (jmax - jmin)
        ls.write(str(n) + "\n")

    
    f.close()




    
def plotNormalizedData():
    '''
    #Simon normalized data
    f = open("normalizeddata_simon", "r")
    firsttimestamp = "2020-05-12 13:25:06"
    last_line = "2020-05-18 10:16:42"

    datetime_object = dt.strptime(firsttimestamp, datetimeformat)
    last_datetime_object = dt.strptime(last_line, datetimeformat)

    calclistsimon = []
    for line in f: 
        calclistsimon.append(float(line.rstrip("\n")))

    f.close()
    '''

    #Jacob normalized data
    f = open("normalizeddata_jacob", "r")
    firsttimestamp = "2020-05-12 13:25:06"
    last_line = "2020-05-18 10:16:42"

    datetime_object = dt.strptime(firsttimestamp, datetimeformat)
    last_datetime_object = dt.strptime(last_line, datetimeformat)

    calclistjacob = []
    for line in f: 
        calclistjacob.append(float(line.rstrip("\n")))

    f.close()
    

    #Jacob normalized data intenisty
    inte = open("normalizeddata_intensity_jacob", "r")
    firsttimestamp = "2020-05-12 13:25:06"
    last_line = "2020-05-18 10:16:42"

    datetime_object = dt.strptime(firsttimestamp, datetimeformat)
    last_datetime_object = dt.strptime(last_line, datetimeformat)

    calclistjacobintensity = []
    for line in inte: 
        calclistjacobintensity.append(float(line.rstrip("\n")))


    inte.close()

    '''
    #Simon normalized data intenisty
    inte = open("normalizeddata_intensity_simon", "r")
    firsttimestamp = "2020-05-12 13:25:06"
    last_line = "2020-05-18 10:16:42"

    datetime_object = dt.strptime(firsttimestamp, datetimeformat)
    last_datetime_object = dt.strptime(last_line, datetimeformat)

    calclistsimonintensity = []
    for line in inte: 
        calclistsimonintensity.append(float(line.rstrip("\n")))


    inte.close()
    '''


    #print(len(calclistsimonintensity))
    #print(len(calclistjacobintensity))

    #calclistjacobintensity = calclistjacobintensity[:len(calclistjacobintensity)-(len(calclistjacobintensity) - len(calclistsimonintensity))]


    
    #plot with timestamps
    
    n=len(calclistjacobintensity)
    now=datetime_object.timestamp() + 7200
    last=last_datetime_object.timestamp() + 7200
    timestamps=np.linspace(now,last,n)
    dates=[dt.fromtimestamp(ts) for ts in timestamps]
    datenums=md.date2num(dates)
    plt.subplots_adjust(bottom=0.2)
    plt.xticks(rotation=60)

    ax=plt.gca()
    xfmt = md.DateFormatter("%d-%m %H:%M")
    hours = md.HourLocator(interval = 12)
    ax.xaxis.set_major_locator(hours)
    ax.xaxis.set_major_formatter(xfmt)

    plt.xlabel("Timestamp 12 hour apart")
    plt.ylabel("Normalized Value")
    #plt.plot(datenums,calclistsimon, label="Simon")


    for i in range(0,len(calclistjacobintensity)):
        if (calclistjacobintensity[i] != calclistjacob[i]):
            print(i)

    

    #plt.plot(datenums, calclistsimonintensity, label="Simon normalized intensity")
    plt.plot(datenums,calclistjacob, 'o', label="Lux level")
    plt.plot(datenums,calclistjacobintensity, color="red", label="Intensity")
    plt.legend(bbox_to_anchor=(1.01, 0.5), loc='upper left', ncol=1)
    plt.show()
    
    



#plotlatency()
fillDelta()
plotlight()
#normalizedLux()
#plotNormalizedData()