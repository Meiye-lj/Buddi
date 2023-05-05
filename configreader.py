##obtain all static deps
import os
import json
import random
from run_procpip import run_procpip

#random generate configuration
def configmaker():
    path = Dir + "configtxt/config.txt"
    f= open(path,"r")
    size = []
    for it in f.readlines():
        it = it.strip()
        size.append(it)
    for id in range(1,21):
        config = str()
        i = random.randint(1,8)
        for n in range(0,i):
            idex = random.randint(0,len(size)-1)
            if size[idex] not in config:
                if "--disable" in size[idex] and "--disable" in config:
                    if size[idex][5:] not in config:
                        config = config + " " + size[idex]
                elif "--enable" in size[idex] and "--enable" in config:
                        if size[idex][4:] not in config:
                            config = config + " " + size[idex]
                elif "--with" in size[idex] and "--with" in config:
                        if size[idex][6:] not in config:
                            config = config + " " + size[idex]
                elif "--without" in size[idex] and "--without" in config:
                        if size[idex][9:] not in config:
                            config = config + " " + size[idex]
                else:
                    config = config + " " + size[idex]

        with open (Dir+"Json/"+ "C" + str(id) + config + ".json","w") as J:
            json.dump(config,J)
    # print(config)



Dir = "~/xterm-368/"

configmaker()