#!/usr/bin/python
'''
Feature-based image comparison for web crawling using Heritrix and Wayback.

USAGE
  bl_compare_screenshots.py [ <image1> <image2> ]

'''

import quords_utils

if __name__ == '__main__':
    print __doc__

    import sys, getopt
    opts, args = getopt.getopt(sys.argv[1:], '', ['feature='])
    opts = dict(opts)
    feature_name = opts.get('--feature', 'sift')
    try: fn1, fn2 = args
    except:
        fn1 = 'warc.png'
        fn2 = 'http://www.schk.sk/index.png'

    res = quords_utils.compare_images_by_path_and_link(fn1, fn2, "false", 50, 10)
    print "comparison result for original screenshot: ", fn1, " and wayback link: ", fn2, " is: ", res
