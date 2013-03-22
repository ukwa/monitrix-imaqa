#!/usr/bin/env python

# This file contains methods for analysis of screenshots harversted during the 
# crawl process and associated screenshots from Wayback tool.
# Parameters for a test run in order to compare two files are:
#     1. Path to the first harversted screenshot
#     2. Path to the second harversted screenshot - in our case wayback file
#     3. Output file name
#     4. Threshold for high similarity (between 0 and 100) for SIFT comparison
#     5. Threshold for small differences (between 0 and previous threshold) for SIFT comparison
#     6. Optional step for subset of the file list could be defined 
#     7. Optional theshold for image comparison with PSNR metric 
# In the case of local wayback installation we should extract the timestamp of 
# the Wayback collection from the WARC file name.
# One of the main goals of QA application is a comparison step wheere we compare two screenshots 
# using SIFT features extraction methods, PSNR metrics and OCR analysis. The second goal is 
# to detect blank pages in a digital collection.
# Additionally file size could be taken into account in order to detect empty pages.

USAGE = "Feature- and OCR-based screenshot comparison for quality assurance in digital libraries.\n" +"USAGE\n  quords_utils.py [-p,--path] [-w,--wpath] [-o,--output] [-h,--threshold1] [-d,--threshold2] [-s,--step] [-i,--thresholdpsnr]\n" + "   --path       - Path to the fist original screenshots.\n" + "    --wpath        - Path to the second screenshot from the wayback tool.\n" + "   --output     - The name of the output file in csv format. The output file contains current timestamp, wayback timestamp, original link, wayback machine link, number of SIFT features for the original file, number of SIFT features for the wayback file, number of matches, conclusion message, threshold 1, threshold 2, OCR measurement, original screenshot size, wayback file size\n" + "   --threshold1 - The threshold for high similarity (between 0 and 100)\n" + "   --threshold2 - The threshold for small differences (between 0 and threshold 1 value)\n" + "   --step       - The subset size of the original collection can be used in order to reduce calculation time by analyzing only part of collection\n" + "    --thresholdpsnr - The threshold for image comparison with PSNR method using imagemagick tool\n\n"


import time
import os
import string
import timeit
import subprocess
import compare_screenshots
import blank
import cv2
import urllib
import timeit
from pymongo import MongoClient
import Image # for file resizing
from threading import Timer

# The timestamp size for Wayback machine
TIMESTAMP_SIZE = 14

# Mongo DB name
MONGO_NAME = "monitrix"
PHANTOMJS = "/opt/phantomjs/bin/phantomjs"
RASTERIZE = "/opt/phantomjs/examples/rasterize.js"

PSNR_THRESHOLD = 3.0

# this is a message counter
count = 1

ORIG_FILE_WARN = "Warning: original file could not be created from internet by given link!"
FILE_CREATION_TIME = 5 # in seconds

def run_command(command):
    p = subprocess.Popen(command,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    return iter(p.stdout.readline, b'')

def store_in_file(current_time, execution_time, orig_link, wayback_link, wayback_timestamp, fc1, fc2, mc, msg, ocr, img1_size, img2_size, psnr_similarity, psnr_threshold, psnr_msg, orig_link_path):
    with open("output.txt", "a") as text_file:
        text_file.write("%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;\n"%(current_time, execution_time, orig_link, wayback_link, wayback_timestamp, fc1, fc2, mc, msg, ts1, ts2, ocr, img1_size, img2_size, psnr_similarity, psnr_threshold, psnr_msg, orig_link_path))

def insert_mongo(current_time, execution_time, orig_link, wayback_link, wayback_timestamp, fc1, fc2, mc, msg, ocr, img1_size, img2_size, psnr_similarity, psnr_threshold, psnr_msg, orig_link_path):
    connection = MongoClient()
    db = connection[MONGO_NAME]
    collection = db['test-collection']
    
    log = {"current_time": current_time,
           "execution_time": execution_time,
           "orig_web_url": orig_link,
           "wayback_image": wayback_link,
           "wayback_timestamp": wayback_timestamp,
           "fc1": fc1,
           "fc2": fc2,
           "mc": mc,
           "msg": msg,
           "ts1": ts1,
           "ts2": ts2,
           "ocr": ocr,
           "img1_size": img1_size,
           "img2_size": img2_size,
           "psnr_similarity": psnr_similarity,
           "psnr_threshold": psnr_threshold,
           "psnr_msg": psnr_msg,
           "orig_image": orig_link_path}
    logs = db.logs
    log_id = logs.insert(log)
    print "log_id: ", log_id, "\n\n"

# This method read image using passed link and create a file
def convert_url_to_file(link, file_name):
    try:
        print "convert link: ", link, " file_name: ", file_name
        for line in run_command([PHANTOMJS, RASTERIZE, link, file_name]):
            print (line)
    except Exception, e:
        print "Error:", e, " Image file could not be created from the passed link." 
        

# This method compares original and wayback screenshots if wayback machine
# is local and original links are stored locally with timestamp in the file name
def handleUri(link_name, counter): 
    # create screenshot from Wayback using timestamp
    link = urllib.unquote_plus(link_name)
    #print "link: ", link 
    initial_uri = link.replace('.jpg', '')
    warc_link = "http://localhost:8080/" + initial_uri.replace("http", "/http")
    #print "warc link: ", warc_link
    print " [%s] Wayback link %s" % (str(counter), warc_link)
    # create image from Wayback link
    warc_img = 'warc.png'
    try:
        for line in run_command([PHANTOMJS, RASTERIZE, warc_link, warc_img]):
            print (line)
        #timeit.default_timer # from last call
        start = timeit.default_timer()
         # compare two images
        img2 = cv2.imread(warc_img, 0)
        img2_size = os.path.getsize(warc_img)
        print "original screenshot: " + file_path + "/" + name
        img1 = cv2.imread(file_path + "/" + name, 0)
        img1_size = os.path.getsize(file_path + "/" + name)
        # threshold for high similarity between screenshots e.g. 60
        # threshold for small differencies e.g. 30
        # highest similarity is 100, minimal is 0
        fc1, fc2, mc, msg = compare_screenshots.compare_ext(img1, img2, 'sift', ts1, ts2)
        # remove temporary image
        os.remove(warc_img)
        # calculate OCR value from original image
        ocr = blank.ocr_ext(file_path + "/" + name)
        execution_time = timeit.default_timer() - start
        print "execution time: ", execution_time
        # store in CSV and MongoDB resulting timstamp in ms, URL, wayback timestamp, 
        # execution time in ms, file size, SIFT features total count, 
        # matched features count, OCR count
        import datetime
        current_time =  datetime.datetime.utcnow()
        wayback_timestamp = link[:TIMESTAMP_SIZE]
        print "wayback timestamp: ", wayback_timestamp
        #print "original link: ", orig_link
        store_in_file(current_time, execution_time, initial_uri[TIMESTAMP_SIZE:], warc_link, wayback_timestamp, fc1, fc2, mc, msg, ocr, img1_size, img2_size)
        insert_mongo(current_time, execution_time, initial_uri[TIMESTAMP_SIZE:], warc_link, wayback_timestamp, fc1, fc2, mc, msg, ocr, img1_size, img2_size)
    except Exception, e:
        print "Error:", e, " Please check if Wayback machine and MongoDB are running!" 

# This method compares original and wayback screenshots
def compare_screenshots_sift(orig_link_path, wayback_link_path):
    compare_screenshots_sift_ext(orig_link_path, wayback_link_path, False)

# This method converts passed string value to boolean value
def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1")
 
# This method compares original and wayback screenshots with optional OCR analysis
# OCR analysis will be active if ocr_flag is True
def compare_screenshots_sift_ext(orig_link_path, wayback_link_path, ocr_flag): 
    return compare_screenshots_sift_ext2(orig_link_path, wayback_link_path, ocr_flag, psnr_flag='false')

def create_file(orig_link_path, orig_img_name):
    for line in run_command([PHANTOMJS, RASTERIZE, orig_link_path, orig_img_name]):
        print (line)

# This method compares original and wayback screenshots with optional OCR and PSNR analysis
# OCR or PSNR analysis will be active if ocr_flag is True
def compare_screenshots_sift_ext2(orig_link_path, wayback_link_path, ocr_flag, psnr_flag): 
    # create screenshot from Wayback using timestamp
    print "\noriginal link: ", orig_link_path, ", wayback link: ", wayback_link_path, ", ocr flag: ", ocr_flag, ", psnr flag: ", psnr_flag 
    import datetime
    current_file_id =  timeit.default_timer()
    # create image from original link
    orig_img_name = 'qa/orig/' + str(current_file_id) + '.png'
    # create image from Wayback link
    wayback_img_name = 'wayback.png'
    try:
        # Set the timer for five seconds for file creation due to programm hanging 
        # if file could not be created from the link by internet
        t = Timer(FILE_CREATION_TIME, create_file(orig_link_path, orig_img_name))
        t.start() 
        tw = Timer(FILE_CREATION_TIME, create_file(wayback_link_path, wayback_img_name))
        tw.start() 
        if os.path.exists(orig_img_name):
            start = timeit.default_timer()
            # compare two images
            img1 = cv2.imread(orig_img_name, 0)
            img1_size = os.path.getsize(orig_img_name)
            img2 = cv2.imread(wayback_img_name, 0)
            img2_size = os.path.getsize(wayback_img_name)
            print "extract features ..."
            fc1, fc2, mc, msg = compare_screenshots.compare_ext(img1, img2, 'sift', ts1, ts2)
            ocr = 0
            if str2bool(ocr_flag):
                # calculate OCR value from original image
                print "perform OCR analysis ..."
                ocr = blank.ocr(orig_img_name)
            psnr_similarity = "None"
            psnr_threshold = ts_psnr
            psnr_msg = ""
            if str2bool(psnr_flag):
               # compare images using imagemagick tool and PSNR metric 
               print "perform PSNR analysis ..."
               psnr_similarity = "DIFFERENT"
               psnr_similarity, psnr_threshold, psnr_msg = compare_psnr(orig_img_name, wayback_img_name)
            # remove temporary images
            os.remove(wayback_img_name)
            execution_time = timeit.default_timer() - start
            print "execution time: ", execution_time
            # store in CSV and MongoDB resulting timstamp in ms, execution time in sec, 
            # original URL, wayback machine URL, wayback timestamp, SIFT features total count, 
            # matched features count, resulting message, OCR count, file sizes, PSNR value
            # and original file
            wayback_url_list = wayback_link_path.split("/")
            wayback_timestamp = wayback_url_list[-2]
            print "wayback timestamp: ", wayback_timestamp
            import datetime
            current_time =  datetime.datetime.utcnow()
            orig_img_name = 'http://127.0.0.1:8000/' + orig_img_name
            #print "original link: ", orig_link
            store_in_file(current_time, execution_time, orig_link_path, wayback_link_path, wayback_timestamp, fc1, fc2, mc, msg, ocr, img1_size, img2_size, psnr_similarity, psnr_threshold, psnr_msg, orig_img_name)
            insert_mongo(current_time, execution_time, orig_link_path, wayback_link_path, wayback_timestamp, fc1, fc2, mc, msg, ocr, img1_size, img2_size, psnr_similarity, psnr_threshold, psnr_msg, orig_img_name)
            return mc, fc1, ocr, psnr_similarity
        else:
           print "Warning: original file could not be retrieved from internet!"
    except Exception, e:
        print "Error:", e, " Please check if Wayback machine and MongoDB are running!" 

# This method compares original image passed by path with
# wayback screenshots passed by URL. Optionally comparison can be extended by
# OCR analysis. The OCR analysis will be active if ocr_flag is True
def compare_images_by_path_and_link(orig_link_path, wayback_link_name, ocr_flag, ts1=60, ts2=30): 
    return compare_images_by_path_and_link_ext(orig_link_path, wayback_link_name, ocr_flag, ts1, ts2, False, None)

# This method compares original image passed by path with
# wayback screenshots passed by URL. Optionally comparison can be extended by
# OCR and PSNR analysis. The OCR or PSNR analysis will be active if ocr_flag or respectively
# psnr_flag is True. The PSNR threshold psnr_th is a float value. 1 means that images are different
# and inf means that images are fully the same. The higher is a PSNR value the higher is the 
# image similarity
def compare_images_by_path_and_link_ext(orig_link_path, wayback_link_name, ocr_flag, ts1=60, ts2=30, psnr_flag=False, psnr_th=None): 
    # create screenshot from Wayback using timestamp
    print "\noriginal link: ", orig_link_path, ", wayback link: ", wayback_link_name, ", ocr flag: ", ocr_flag, ", high ts1: ", ts1, ", low ts2: ", ts2 
    
    # create screenshot from Wayback using timestamp
    wayback_link = urllib.unquote_plus(wayback_link_name)
    
    # create image from Wayback link
    wayback_img_name = "wayback.png"
    convert_url_to_file(wayback_link, wayback_img_name)
    print "wayback file: ", wayback_img_name
    try:
        timeit.default_timer 
        start = timeit.default_timer()
         # compare two images
        img1 = cv2.imread(orig_link_path, 0)
        img1_size = os.path.getsize(orig_link_path)
        img2 = cv2.imread(wayback_img_name, 0)
        img2_size = os.path.getsize(wayback_img_name)
        print "extract features ..."
        fc1, fc2, mc, msg = compare_screenshots.compare_ext(img1, img2, 'sift', ts1, ts2)
        ocr = 0
        if str2bool(ocr_flag):
            # calculate OCR value from original image
            print "perform OCR analysis ..."
            ocr = blank.ocr(orig_link_path)
        psnr_similarity = "DIFFERENT"
        psnr_msg = ""
        if str2bool(psnr_flag):
            # compare images using imagemagick tool and PSNR metric 
            print "perform PSNR analysis ..."
            if psnr_th is None:
                psnr_th = th_psnr
            psnr_similarity, psnr_threshold, psnr_msg = compare_psnr(orig_link_path, wayback_img_name)
        # remove temporary images
   #     os.remove(wayback_img_name)
        execution_time = timeit.default_timer() - start
        print "execution time: ", execution_time
        # store in CSV and MongoDB resulting timstamp in ms, execution time in sec, 
        # original URL, wayback machine URL, wayback timestamp, SIFT features total count, 
        # matched features count, resulting message, OCR count, file sizes
        import datetime
        current_time =  datetime.datetime.utcnow()
        wayback_url_list = wayback_link.split("/")
        wayback_timestamp = wayback_url_list[-2]
        print "wayback timestamp: ", wayback_timestamp
        #print "original link: ", orig_link
        store_in_file(current_time, execution_time, orig_link_path, wayback_link, wayback_timestamp, fc1, fc2, mc, msg, ocr, img1_size, img2_size, psnr_similarity, psnr_threshold, psnr_msg, orig_link_path)
        insert_mongo(current_time, execution_time, orig_link_path, wayback_link, wayback_timestamp, fc1, fc2, mc, msg, ocr, img1_size, img2_size, psnr_similarity, psnr_threshold, psnr_msg, orig_link_path)
        print "result message: ", msg
        return msg
    except Exception, e:
        print "Error:", e, " Please check if Wayback machine and MongoDB are running!" 

# This method checks if a given image is blank or not
def check_blank(orig_link_path): 
    print "\noriginal link: ", orig_link_path 
    # create image from original link
    orig_img_name = 'orig.png'
    try:
        for line in run_command([PHANTOMJS, RASTERIZE, orig_link_path, orig_img_name]):
            print (line)
        timeit.default_timer # from last call
        start = timeit.default_timer()
         # compare two images
        img1 = cv2.imread(orig_img_name, 0)
        img1_size = os.path.getsize(orig_img_name)
        # calculate OCR value from original image
        ocr = blank.ocr(orig_img_name)
        # remove temporary images
        os.remove(orig_img_name)
        execution_time = timeit.default_timer() - start
        print "execution time: ", execution_time
        # store in CSV and MongoDB resulting timstamp in ms, execution time in sec, 
        # original URL, wayback machine URL, wayback timestamp, SIFT features total count, 
        # matched features count, resulting message, OCR count, file sizes
        import datetime
        current_time =  datetime.datetime.utcnow()
        return ocr
    except Exception, e:
        print "Error:", e, " Please check if OCR tool is running!" 

# This method compares two images employing PSNR metric and image magick tool
# note that the analyzed images must be of the same size
def compare_psnr(img_path_1, img_path_2, psnr_threshold=PSNR_THRESHOLD):
    print "\ncompare PSNR input1: ", img_path_1, ", input2: ", img_path_2 
    # compare images
    diff_img_name = 'difference.png'
    similarity = ''
    try:
        timeit.default_timer 
        start = timeit.default_timer()
        # get sizes
        img1 = Image.open(img_path_1)
        img2 = Image.open(img_path_2)
        width1, height1 = img1.size
        width2, height2 = img2.size
        # adjust sizes if necessary
        if width1 != width2 or height1 != height2:
            print "width1: ", width1, ", width2: ", width2, ", height1: ", height1, ", height2: ", height2
            img2 = img2.resize((width1, height1), Image.ANTIALIAS)
        img2.save(img_path_2 + ".png")
        # compare -metric PSNR img1 img.2 difference.png
        for line in run_command(['sudo', 'compare', '-metric', 'PSNR', img_path_1, img_path_2 + ".png", diff_img_name]):#, '> ' + PSNR_FILE]):
            similarity = line.strip()
            #print (line)
        ##print "similarity: ", similarity
        # remove temporary images
        #os.remove(PSNR_FILE)
        os.remove(img_path_2 + ".png")
        os.remove(diff_img_name)
        execution_time = timeit.default_timer() - start
        #print "execution time: ", execution_time
    except Exception, e:
        print "Error:", e, " Please check if image magick tool is installed and passed image paths are correct!" 
    psnr_msg = "DIFFERENT"
    if float(similarity) >= psnr_threshold:
        psnr_msg = "SIMILAR"
    return similarity, psnr_threshold, psnr_msg


try:
    import sys, getopt
    #print USAGE
    
    letters = 'p:w:o:h:d:s:i:'
    keywords = ['path=', 'wpath=', 'output=', 'threshold1=', 'threshold2=', 'step=', 'thresholdpsnr=' ]
    opts, args = getopt.getopt(sys.argv[1:], letters, keywords)
    step_size = 1
    file_path="/opt/test_django/quords/origmy.png" 
    wayback_file_path = "/opt/test_django/quords/warc.png"
    output_file = "output.txt"
    ts1 = 60
    ts2 = 30
    ts_psnr = PSNR_THRESHOLD

    for o,p in opts:
        if o in ['-p','--path']:
            file_path = p
        if o in ['-w','--wpath']:
            wayback_file_path = p
        elif o in ['-o','--output']:
            output_file = p
        elif o in ['-h','--threshold1']:
            try:
                ts1 = int(p)
            except ValueError:
                print "Value for threshold 1 is not an integer. Please check!"
        elif o in ['-d','--threshold2']:
            try: 
                ts2 = int(p)
            except ValueError:
                print "Value for threshold 2 is not an integer. Please check!"
        elif o in ['-s','--step']:
            try: 
                step_size = int(p)
            except ValueError:
                print "Value for step size is not an integer. Please check!"
        elif o in ['-i','--thresholdpsnr']:
            try: 
                ts_psnr = float(p)
            except ValueError:
                print "Value for PSNR threshold is not a float. Please check!"

# These lines could be used only for testing
#    msg = compare_images_by_path_and_link_ext(file_path, wayback_file_path, 'True', ts1, ts2, 'True', ts_psnr)
#    print msg
    #print "collection path: ", file_path , ", output file: ", output_file, ", high similarity threshold: ", ts1, ", small difference threshold: ", ts2, ", step: ", step_size
except IOError:
    print "No such file: %s" % file_path

