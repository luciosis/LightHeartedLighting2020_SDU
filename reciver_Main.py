import socket
from filelock import FileLock
from datetime import datetime

tupleOfIntensity = {}
HOSTIP = ''
HOSTPORT = 8080
i = 0
setpointsJacob = [0.0,895.0,1789.0,2683.0,3578.0,4472.0,5366.0,6265.0,7156.0,8052.0,8947.0,9850.0,10738.0,11629.0,12521.0,13423.0,14311.0,15206.0,16111.0,17002.0,17917.0,18782.0,19693.0,20573.0,21465.0,22363.0,23251.0,24146.0,25041.0,25939.0,26830.0,27722.0,28618.0,29512.0,30405.0,31299.0,32197.0,33090.0,33982.0,34884.0,35771.0,36665.0,37560.0,38485.0,39403.0,40254.0,41141.0,42062.0,42955.0,43868.0,44778.0]
setpointsSimon = [0.0,60.0,119.0,178.0,237.0,296.0,355.0,414.0,474.0,533.0,592.0,651.0,710.0,769.0,828.0,888.0,947.0,1006.0,1065.0,1124.0,1183.0,1242.0,1302.0,1362.0,1420.0,1479.0,1538.0,1597.0,1656.0,1716.0,1775.0,1834.0,1893.0,1952.0,2011.0,2070.0,2130.0,2189.0,2248.0,2307.0,2369.0,2425.0,2486.0,2544.0,2604.0,2662.0,2721.0,2780.0,2840.0,2898.0, 2903.0]
adjustedSetpoints = [0.0, 25.0,28.70384053742207,32.956418463910175,37.839031210905205,43.44502071873438,49.88155787422199,57.27169131919433,65.75669979738454,75.4987930100504,86.68421261313291,99.5267926383743,114.27204740371874,131.20186506244315,150.63989651858944,172.9577427297341,198.58205868107032,228.0027098389774,261.7821370127249,300.5661086543533,345.09606615072113,396.22329811527834,454.92521465249587,522.3240327135096,599.7082297548725,688.5571758345416,790.5694150420948,907.6951369252536,1042.1734586758382,1196.5752308065958,1373.8521846440615,1577.3933612004826,1811.0899001874745,2079.409427756677,2387.4814650535895,2741.1954903579626,3147.3135294854187,3613.5994268648196,4148.9672685938995,4763.651794908116,5469.404059873879, 6279.716078773949,7210.078757816514,8278.278037064778,9504.734908014032,10912.89580600414,12529.680840681798,14385.998433428915,16517.336200189893,18964.439375729587,21774.089748902014,25000.0]
increase = False
connectionTuple = {}
colorTime = {}


def intensityCalculator(color, intensity):
    result = tuple((0, 16) for i in range(0, 6, 6//3))
    resultList = list(result)

    if(color == 'white'):
        for i in range(0,3):
            resultList[i] = intensity * 5
    elif(color == 'red'):
        resultList[0] = intensity * 5
        resultList[1] = 0
        resultList[2] = 0
    elif(color == 'green'):
        resultList[0] = 0
        resultList[1] = intensity * 5
        resultList[2] = 0
    elif(color == 'blue'):
        resultList[0] = 0
        resultList[1] = 0
        resultList[2] = intensity * 5
        
    t = tuple(resultList)
    return '0x%02x%02x%02x' % t

def findIntensity(lightLevel):
    setpointdata = adjustedSetpoints
    for i in range(0, len(setpointdata)):
        value = setpointdata[51 - i]
        if(float(lightLevel) >= value):
            return i


with FileLock("logs.csv.lock"):
    socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    socket.bind((HOSTIP, HOSTPORT))
    connection = socket
    log = open("logs.csv", "a")

    print("file lock start")
    while True:
        message = connection.recvfrom(4096)    
        received_data = message[0].decode("utf-8")
        elements = received_data.split(";")
        if elements[len(elements) - 1] == 'level':
            if elements[len(elements)-3] not in connectionTuple:
                connectionTuple[elements[len(elements)-3]] = message[1]
                tupleOfIntensity[elements[len(elements)-3]] = '0x000000'
            else:
                if connectionTuple[elements[len(elements)-3]] != message[1]:
                    connectionTuple[elements[len(elements)-3]] = message[1]

            send_time = datetime.strptime(elements[1], "%Y-%m-%d %H:%M:%S")
            time_of_arrival = datetime.now()
            message_arrival = time_of_arrival.strftime("%Y-%m-%d %H:%M:%S")
            latency = (time_of_arrival - send_time).total_seconds() * 1000000

            # Format is:
            # Message number; send time; reception time; latency; light level;light intesity;color; device
            
            log.write("{};{};{};{};{};{};{};{};{}\n".format(elements[0], elements[1], message_arrival, latency, elements[2], findIntensity(int(elements[2])) ,elements[4], elements[5], elements[7]))

            intensityResult = intensityCalculator(elements[4], findIntensity(int(elements[2])))
            if intensityResult != tupleOfIntensity[elements[len(elements)-3]]:
                tupleOfIntensity[elements[len(elements)-3]] = intensityResult
                
                connection.sendto('{};{}'.format(str(intensityResult), 'level').encode('utf-8'), connectionTuple[elements[len(elements)-3]])
            
            log.flush()
        
        elif elements[len(elements)-1] == 'light':
            send_time = datetime.strptime(elements[1], "%Y-%m-%d %H:%M:%S")
            time_of_arrival = datetime.now()
            
            if elements[len(elements)-3] not in connectionTuple:
                connectionTuple[elements[len(elements)-3]] = message[1]
                tupleOfIntensity[elements[len(elements)-3]] = '0x000000'
            else:
                if connectionTuple[elements[len(elements)-3]] != message[1]:
                    connectionTuple[elements[len(elements)-3]] = message[1]
                     
            if elements[len(elements)-2] == 'send':
                for item in connectionTuple:
                    if item != elements[len(elements)-3]:
                        colorTime[elements[0]] = elements[1]
                        message_arrival = time_of_arrival.strftime("%Y-%m-%d %H:%M:%S")
                        latency = (time_of_arrival - send_time).total_seconds() * 1000000
                        #MeasurementCounter, Send_time, color, device name, send/recieve, type
                        connection.sendto('{};{};{};{};{};{}'.format(elements[0], elements[1], elements[2], elements[3], elements[4], elements[len(elements)-1]).encode('utf-8'), connectionTuple[item])
                        log.write("{};{};{};{};{};{};{};{}\n".format(elements[0], message_arrival, latency, elements[1], elements[2], elements[3], elements[4], elements[len(elements)-1]))
            else:

                latency = (send_time - datetime.strptime(colorTime[elements[0]], "%Y-%m-%d %H:%M:%S")).total_seconds() * 1000000
                log.write("{};{};{};{};{};{};{};{}\n".format(elements[0], message_arrival, latency, elements[1], elements[2], elements[3], elements[4], elements[len(elements)-1]))
                
            log.flush()