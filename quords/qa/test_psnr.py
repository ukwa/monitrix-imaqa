#!/usr/bin/python
import quords_utils
import sys

if __name__ == "__main__":

    if not sys.argv[1:]:
        print "Usage: test_psnr.py img1.png img2.png"
        sys.exit()
    img1, img2 = sys.argv[1:]

    res, th, psnr_msg = quords_utils.compare_psnr(img1, img2, 2.2)
    print "res: ", res,  ", th: ", th, ", psnr_msg: ", psnr_msg
