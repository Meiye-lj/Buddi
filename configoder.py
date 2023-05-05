import os
import json
import re
import time
import math
import random
import subprocess

from run_procpip import run_procpip
from collections import defaultdict



def distanceitem (listA,listB):
    lenB = 0
    lenA = 0
    for target ,deps in listB.items():
        lenB= lenB + 1 +len(deps)
    for target ,deps in listA.items():
        lenA= lenA + 1 +len(deps)
    count = 0
    countA = 0 
    countB = 0
    
    for target ,deps in listA.items():
        if target in listB:
            if str(deps) not in str(listB[target]):
                count = count + len(deps)
                # print(len(deps))
            else:
                countB = countB + 1 +len(deps)
        else:
            count = count +len(listA[target])
    
    distance = math.fabs(lenB - countB) +count
    per = round(100*(lenA - count + countB)/(lenA + lenB))
    return distance,per
    
def write_to_txt(Dir,lists,name):
    with open (Dir+name,'w') as f:
        for target,i in lists.items():
            f.writelines(str(target)+str(i)+'\n')
        f.close
    
def depsdistance():
    filelist = os.listdir(buildDir +"CJson")
    firstonfig = str()
    disavg = -1
    dis = []
    for fileitem1 in filelist:
        file1 = open(buildDir +"CJson/"+fileitem1,"r")
        makegraph1 = json.load(file1)
        distancelist = defaultdict(list)
        countdis = 0
        countper = 0
        i = 0
        Secstr = str()
        mindis = -1
        maxdis = -1
####### calculate all distance ,average dis, min dis #######
        for fileitem2 in filelist:

            if fileitem2 != fileitem1:
                file2 = open(buildDir +"CJson/"+fileitem2,"r")
                makegraph2 = json.load(file2)
                distance,per = distanceitem(makegraph1,makegraph2)
                distancelist[fileitem1+" - " + fileitem2].append(str(distance))
                # dis.append(per)
                i = i +1
                countper = countper +per
                countdis = countdis + distance
                if mindis == -1:
                    mindis = distance
                    maxdis = distance
                    firststr = fileitem1
                    Secstr = fileitem2
                else:
                    if mindis > distance:
                        mindis = distance
                        Secstr = fileitem2
                    if maxdis < distance:
                        maxdis = distance
        avgper = round(countper / i)
        dis.append(avgper)
        countavg = countdis / i
        distancelist["avg"].append(countavg)
        distancelist["Secstr"].append(Secstr)
        distancelist["mindis"].append(str(mindis))
        distancelist["maxdis"].append(str(maxdis))
        write_to_txt(buildDir + "CDistance/", distancelist,fileitem1)

def readdeps(firstconfig):
    if".json" not in firstconfig:
        firstconfig = firstconfig +".json"
    f = open(buildDir + "CDistance/" + firstconfig,"r")
    dislist = defaultdict(list)
    for lists in f.readlines():
        item , target = lists.split("[")
        target = re.findall(r"'(.*?)'", target, re.DOTALL)
        dislist[item].append(target)
    return dislist

####### Creating Order ###############################
def BuddiOrderer():
    depsdistance()
    firstconfig = minbuid()
    buildorder = []
    buildorder.append(firstconfig.strip(".json"))
    nodelist = os.listdir(buildDir+"Json")
    for i in  range(0,len(nodelist)-1):
        dislist = readdeps(firstconfig)
        firstconfig = dislist["Secstr"][0][0]
        firstconfig = firstconfig.strip(".json")
        if firstconfig not in buildorder:
            buildorder.append(firstconfig)
        else:
            mindis = float(dislist["mindis"][0][0])
            maxdis = float(dislist["maxdis"][0][0])
            for config , dis in dislist.items():
                if config != "avg" and config != "mindis" and config != "maxdis" and config != "Secstr": 
                    item, config = config.split(" - ")
                    if config.strip(".json") in  buildorder:
                        continue
                    if float(dis[0][0]) == mindis:
                        secmindis = []##search all mindis
                        for config , dis in dislist.items():
                            if config != "avg" and config != "mindis" and config != "maxdis" and config != "Secstr":
                                if float(dis[0][0]) == mindis:
                                    config = config.strip(".json")
                                    num= 0
                                    for i in config:
                                        if i == "-":
                                            config = config[num:]
                                            secmindis.append(config)
                                            break
                                    else:
                                        num = num +1                                   
                        if len(secmindis)==1:
                            item1,item2 = secmindis.split(" - ")
                            if item2 not in buildorder:
                                firstconfig = item2.strip(".json")
                        else:
                            fir ={}
                            for item in secmindis:
                                first ,second = item.split(" - ")
                                num= 0
                                Dsec = str()
                                for i in first:
                                    if i == "-":
                                        first = first[num:]
                                        first = first.strip(".json")
                                        break
                                    else:
                                        num = num +1
                                num= 0
                                for i in second:
                                    if i == "-":
                                        Dsec = second[num:]
                                        break
                                    else:
                                        num = num +1
                                sec = []
                                count = 0
                                per = 0
                                sec= [x.strip() for x in Dsec.split('--') if x != ""]
                                for i in sec:
                                    if i in first:
                                        count = count +1
                                    per = round((count*100)/len(sec))
                                fir[second]=per 
                            fir = sorted(fir.items(),key=lambda x: x[1],reverse=True)
                            for i in range(0,len(fir)):
                                if fir[i][0] not in buildorder:
                                    firstconfig = fir[i][0].strip(".json")
                                    break     
                    elif maxdis > float(dis[0][0]) :
                        maxdis = float(dis[0][0])
                        firstconfig = config.strip(".json")
                    elif i == len(nodelist)-2:
                        if float(dis[0][0]) == maxdis and config not in buildorder:
                            firstconfig = config.strip(".json")

            buildorder.append(firstconfig.strip(".json"))
    return buildorder

######################## first build ######################################
def minbuid():
    # filelist = os.listdir(buildDir +"/Json")
    filelist = os.listdir(buildDir +"CJson")
    firstonfig = str()
    dismin = 0
    dis = []
    for fileitem1 in filelist:
        file1 = open(buildDir +"/CJson/"+fileitem1,"r")
        makefile = json.load(file1)
        lenmakefile = 0
        for target,deps in makefile.items():
            lenmakefile = lenmakefile + len(deps) + 1
            i = 1
            for dep in deps:
                if dep == "-O0":
                    lenmakefile = lenmakefile - 2*len(deps) +i
                else:
                    i = i+1
        if dismin == 0 :
            dismin = lenmakefile
            firstonfig = fileitem1
        elif dismin > lenmakefile:
            dismin = lenmakefile
            firstonfig = fileitem1
        elif dismin == lenmakefile:
            dis.append(fileitem1)
    dis.append(firstonfig)
    dis = sorted(dis,key=len,reverse=False)
    firstonfig = dis[0]
    return firstonfig

        
######Output build commands and targets##################
def Cjson():
    filelist = os.listdir(buildDir+"Json")
    count = 0
    for fileitem1 in filelist:
        num = 0
        for i in fileitem1:
            if i == "-":
                item = fileitem1[num:]
                command = "./configure " + item.strip(".json")
                run_procpip(command,buildDir)
                clean_build_to_target_command(fileitem1)
                break
            else:
                num = num +1

    
def clean_build_to_target_command(pathname):
    command = 'cd '+buildDir+'&&  make -n --debug=basic'
    result = subprocess.run(
        command, shell=True, stdout=subprocess.PIPE).stdout.decode('utf-8').strip()
    dict = {}
    targetsum = []
    lines = result.splitlines()
    i = 0
    while (i < len(lines)):
        if lines[i].strip().startswith('Must remake target'):
            index = lines[i].find('\'')
            target = lines[i][index+1:-2]
            targetsum.append(target)
            i += 1
            command = ''
            while i < len(lines) and lines[i].strip().startswith('Successfully remade target') == False:
                command += lines[i].strip()
                i += 1
            deps = re.split(" ", command)
            deps=[x.strip() for x in deps if x.strip() != '']
            dict[target] = deps
        i += 1
    dict["target_sum"]=targetsum
    json_data = json.dumps(dict, indent=4)
    with open(buildDir+"CJson/"+pathname, "w") as f:
        f.write(json_data)


def readCJson():
    filelist = os.listdir(buildDir+"CJson")
    for fileitem in filelist:
        f = open(buildDir+"CJson/"+fileitem,"r")
        makefile = json.load(f)
        dir = {}
        for target ,deps in makefile.items():
            deps = re.split(" ", deps)
            deps=[x.strip() for x in deps if x.strip() != '']
            dir[target]=deps
        file = open(buildDir+"CDistance/"+fileitem,"w") 
        json_data = json.dumps(dir, indent=4)   
        file.write(json_data)

def configdis():#options distance
    filelist = os.listdir(buildDir+"Json")
    count = 0
    dir = {}
    dis = []
    for fileitem1 in filelist:
        num = 0
        for i in fileitem1:
            if i == "-":
                item = fileitem1[num:]
                item = item.strip(".json")
                break
            else:
                num = num +1
        options = [x.strip() for x in item.split('--') if x != ""]
        dir[fileitem1] = options
    for i,deps in dir.items():
        count = 0
        for n,item in dir.items():
            if i != n:
                for dep in deps :
                    if dep in str(item):
                        count = count +1
        avg = round((count*100) / (19*len(deps)))
        dis.append(avg)
    print(dis)   


def buildtime():
    buildorder = disbuildOrder()
    timelist = defaultdict(list)
    timecount = 0
    for n in range(0,3):
        comm = "make clean"
        run_procpip(comm,buildDir)
        for config in buildorder:
            num = 0
            timecm = time.time()
            for i in config:
                if i == "-":
                    item = config[num:]
                    command = "./configure " + item.strip(".json")
                    run_procpip(command,buildDir)
                    break
                else:
                    num = num +1
            timeCO = time.time()-timecm
            command = "make"
            timeA = time.time()
            run_procpip(command,buildDir)
            timeB = time.time()-timeA
            timelist[config.strip(".json")].append(timeB)
            timelist[config.strip(".json")].append(timeCO)
            timecount = timecount+ timeB 
        timelist["Timecount"].append(timecount)
        timecount = 0
    avg = 0
    for item in timelist["Timecount"]:
        avg = avg + item
    avg = avg / len(timelist["Timecount"])
    timelist["AvgTime"].append(str(avg))
    write_to_txt(buildDir,timelist,"Timecount")

buildDir =  "~/xterm-368/"

Cjson()
BuddiOrderer()
