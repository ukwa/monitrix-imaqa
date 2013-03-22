# ====================
# qa/views.py
# ====================

from django.http import HttpResponse
from django.core import serializers

from simple_rest import Resource

from .models import BlankPage
from .models import Compare
from .models import CompareCollection

import quords_utils
import os
import sys

#from kolejny.galery.models import Photo

#def photo(request):
#    photos = Photo.objects.all()
#    return render_to_response('photo.html', {'photos' : photos}, context_instance=RequestContext(request))

def check_key_in_dict(dictionary, key_name):
    res = ''
    if key_name in dictionary:
        res = dictionary[key_name]
    return res

class Compares(Resource):

    def get(self, request, file_path=None, **kwargs):
        print "request: ", request.REQUEST
        res = request.REQUEST
        img1 = check_key_in_dict(res, 'i1')
        img2 = check_key_in_dict(res, 'i2')
        ocr_flag = check_key_in_dict(res, 'ocr')
        psnr_flag = check_key_in_dict(res, 'psnr')
        print "image 1: ", img1, ", image 2: ", img2, ", ocr flag: ", ocr_flag, ", psnr flag: ", psnr_flag
        print "path: ", request.path
        if request.path.find("compare") > 0:
            print "compare screenshots"
            mc, fc1, ocr, psnr = quords_utils.compare_screenshots_sift_ext2(img1, img2, ocr_flag, psnr_flag)
            res = "{siftMatchedPoints: " + str(mc) + ", totalSiftPoints: " + str(fc1) + ", ocrMatch: " + str(ocr) + ", psnrSimilarity: " + str(psnr) + "}"
            return HttpResponse(res, content_type='application/json', status=200)

class CompareCollections(Resource):

    def get(self, request, file_path=None, **kwargs):
        print "request: ", request.REQUEST
        res = request.REQUEST
        seeds = check_key_in_dict(res, 'seed')
        ocr_flag = check_key_in_dict(res, 'ocr')
        psnr_flag = check_key_in_dict(res, 'psnr')
        print "seed file: ", seeds, ", ocr flag: ", ocr_flag, ", psnr flag: ", psnr_flag
        print "path: ", request.path
        if request.path.find("comparecollection") > 0:
            print "compare screenshots of the whole collection"
            res = ''
            f = open(seeds, 'r')
            for line in f.readlines():
                try:
                    links = line.split("\t")
                    orig_link = links[1].replace("\n", "").replace(" ", "")
                    wayback_link = links[0].replace("\n", "").replace(" ", "")
                    mc, fc1, ocr, psnr = quords_utils.compare_screenshots_sift_ext2(orig_link, wayback_link, ocr_flag, psnr_flag)
                    res += "{siftMatchedPoints: " + str(mc) + ", totalSiftPoints: " + str(fc1) + ", ocrMatch: " + str(ocr) + ", psnrSimilarity: " + str(psnr) + "}\n"
                except Exception, e:
                    print "Log URI error: ", e
            f.close()
            return HttpResponse(res, content_type='application/json', status=200)

class BlankPages(Resource):

    def get(self, request, image_path=None, **kwargs):
        print "request: ", request.REQUEST
        res = request.REQUEST
        img1 = check_key_in_dict(res, 'i1')
        print "image 1: ", img1
        print "path: ", request.path
        if request.path.find("blank") > 0:
            print "check for blank page"
            ocr = quords_utils.check_blank(img1)
            res = "{ocrMatch: " + str(ocr) + "}"
            return HttpResponse(res, content_type='application/json', status=200)

