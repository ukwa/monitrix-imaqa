# QUORDS 
# blank.py 
# OCR-based blank page analysis
#

import numpy as np
import cv2
from common import anorm, getsize
import os
import string
import timeit
import subprocess


def run_command(command):
    p = subprocess.Popen(command,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    return iter(p.stdout.readline, b'')

def ocr(name):
    for line in run_command(['tesseract', name, 'out']):
        print(line)

    response = open('out.txt', 'r')
    # build up txt 
    txt = ""
    for line in response:
        txt += line #pass
    
    if (len(txt) > 0):
        print 'OCR size: ', len(txt) #, ', txt', txt
    else:
        print 'OCR empty result'
    response.close()
    return len(txt)

if __name__ == '__main__':
    print __doc__
