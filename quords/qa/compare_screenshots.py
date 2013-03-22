'''
Feature-based image matching sample.

USAGE
  compare_screenshots.py [--feature=<sift|surf|orb>[-flann]] [ <image1> <image2> ]

  --feature  - Feature to use. Can be sift, surf of orb. Append '-flann' to feature name
                to use Flann-based matcher instead bruteforce.

'''

import numpy as np
import cv2
from common import anorm, getsize

FLANN_INDEX_KDTREE = 1  
FLANN_INDEX_LSH    = 6


def init_feature(name):
    chunks = name.split('-')
    if chunks[0] == 'sift':
        detector = cv2.SIFT()
        norm = cv2.NORM_L2
    elif chunks[0] == 'surf':
        detector = cv2.SURF(800)
        norm = cv2.NORM_L2
    elif chunks[0] == 'orb':
        detector = cv2.ORB(400)
        norm = cv2.NORM_HAMMING
    else:
        return None, None
    if 'flann' in chunks:
        if norm == cv2.NORM_L2:
            flann_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
        else:
            flann_params= dict(algorithm = FLANN_INDEX_LSH,
                               table_number = 6, 
                               key_size = 12,     
                               multi_probe_level = 1) 
        matcher = cv2.FlannBasedMatcher(flann_params, {})  
    else:
        matcher = cv2.BFMatcher(norm)
    return detector, matcher


def filter_matches(kp1, kp2, matches, ratio = 0.75):
    mkp1, mkp2 = [], []
    for m in matches:
        if len(m) == 2 and m[0].distance < m[1].distance * ratio:
            m = m[0]
            mkp1.append( kp1[m.queryIdx] )
            mkp2.append( kp2[m.trainIdx] )
    p1 = np.float32([kp.pt for kp in mkp1])
    p2 = np.float32([kp.pt for kp in mkp2])
    kp_pairs = zip(mkp1, mkp2)
    return p1, p2, kp_pairs


def compare(img1, img2, feature_name):
    detector, matcher = init_feature(feature_name)
    kp1, desc1 = detector.detectAndCompute(img1, None)
    kp2, desc2 = detector.detectAndCompute(img2, None)
    print 'img1 - %d features, img2 - %d features' % (len(kp1), len(kp2))

    raw_matches = matcher.knnMatch(desc1, trainDescriptors = desc2, k = 2) #2
    p1, p2, kp_pairs = filter_matches(kp1, kp2, raw_matches)
    if len(p1) >= 4:
        H, status = cv2.findHomography(p1, p2, cv2.RANSAC, 5.0)
        res = len(status)*100/len(kp1)
        msg = "VERY DIFFERENT"
        if res > 30:
            msg = "OK"
        print '%d matched => result %s\n' % (len(status), msg)
    else:
        H, status = None, None
        print '%d matches found, not enough for homography estimation' % len(p1)

# ts1 is a threshold for high similarity between snapshots
# ts2 is a threshold for small differencies
# return features count for original image, features count for wayback image,
#        matches count and text message
def compare_ext(img1, img2, feature_name, ts1, ts2):
    print "compare_ext begin"
    detector, matcher = init_feature(feature_name)
    kp1, kp2 = None, None
    kp1, desc1 = detector.detectAndCompute(img1, None)
    kp2, desc2 = detector.detectAndCompute(img2, None)
    print 'img1 - %d features, img2 - %d features' % (len(kp1), len(kp2))

    raw_matches = matcher.knnMatch(desc1, trainDescriptors = desc2, k = 2) #2
    p1, p2, kp_pairs = filter_matches(kp1, kp2, raw_matches)
    mc = 0
    msg = "VERY DIFFERENT"
    if len(p1) >= 4:
        H, status = cv2.findHomography(p1, p2, cv2.RANSAC, 5.0)
        res = len(status)*100/len(kp1)
        if res > ts1:
            msg = "VERY SIMILAR"
        elif res > ts2:
            msg = "SIMILAR"
        print '%d matched => result %s\n' % (len(status), msg)
        mc = len(status)
    else:
        mc = len(p1) 
        print '%d matches found, not enough for homography estimation' % len(p1)
    return len(kp1), len(kp2), mc, msg


if __name__ == '__main__':
    print __doc__

    import sys, getopt
    opts, args = getopt.getopt(sys.argv[1:], '', ['feature='])
    opts = dict(opts)
    feature_name = opts.get('--feature', 'sift')
    try: fn1, fn2 = args
    except:
        fn1 = '../c/box.png'
        fn2 = '../c/box_in_scene.png'

    img1 = cv2.imread(fn1, 0)
    img2 = cv2.imread(fn2, 0)
    detector, matcher = init_feature(feature_name)
    if detector != None:
        print 'using', feature_name
    else:
        print 'unknown feature:', feature_name
        sys.exit(1)

    kp1, desc1 = detector.detectAndCompute(img1, None)
    kp2, desc2 = detector.detectAndCompute(img2, None)
    print 'img1 - %d features, img2 - %d features' % (len(kp1), len(kp2))

    def match_and_draw(win):
        print 'matching...'
        raw_matches = matcher.knnMatch(desc1, trainDescriptors = desc2, k = 2) #2
        p1, p2, kp_pairs = filter_matches(kp1, kp2, raw_matches)
        if len(p1) >= 4:
            H, status = cv2.findHomography(p1, p2, cv2.RANSAC, 5.0)
            print '%d matched' % (len(status))
        else:
            H, status = None, None
            print '%d matches found, not enough for homography estimation' % len(p1)

    match_and_draw('compare_screenshots')
