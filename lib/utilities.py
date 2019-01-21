
import math

def elapsedTime(millis):
	milliseconds = round(millis % 60000)
	minutes = math.floor(millis / 60000)
	seconds = int(round(((millis % 60000) / 1000)))
	return pad(minutes, 2) + ":" + pad(seconds, 2) + "." + pad(milliseconds, 3)

def pad(num, size):
    s = str(num) + ""
    while (len(s) < size):
        s = "0" + s
    return s

def findInArray(arrayNames, toSearch, caseInsensitive = False):
    result = False
    if(caseInsensitive):
        for arrayName in arrayNames:
            if(arrayName.lower() == toSearch.lower()):
                result = True
                break
    else:
        for arrayName in arrayNames:
            if(arrayName == toSearch):
                result = True
                break
    return result