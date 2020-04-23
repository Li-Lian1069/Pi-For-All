import os , re

if os.name == 'nt':
    raise OSError ('Volume is disable to use in windows.')

def getV () -> str:
    with os.popen ('amixer sget PCM','r') as p:
        return re.findall (r'\[(\d+)%\] \[',p.read ())[0]

def setV (Volume:str):
    os.popen ('amixer sset PCM ' + Volume + '%').close ()