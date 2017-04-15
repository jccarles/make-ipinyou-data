#!/usr/bin/python
import operator
import sys
import numpy as np


if len(sys.argv) < 5:
    print 'Usage: train.log.txt test.log.txt train.txt test.txt featindex.txt'
    exit(-1)

oses = ["windows", "ios", "mac", "android", "linux"]
browsers = ["chrome", "sogou", "maxthon", "safari", "firefox", "theworld", "opera", "ie"]

f1s = ["weekday", "hour", "IP", "region", "city", "adexchange", "domain", "slotid", "slotwidth", "slotheight",
       "slotvisibility", "slotformat", "creative", "advertiser"]

f1sp = ["useragent", "slotprice"]

print('only %d features will be used' % (len(f1s) + len(f1sp)))
print('these features are:')
print(f1s)
print(f1sp)


def featTrans(name, content):
    content = content.lower()
    if name == "useragent":
        operation = "other"
        for o in oses:
            if o in content:
                operation = o
                break
        browser = "other"
        for b in browsers:
            if b in content:
                browser = b
                break
        return operation + "_" + browser
    if name == "slotprice":
        price = int(content)
        if price > 100:
            return "101+"
        elif price > 50:
            return "51-100"
        elif price > 10:
            return "11-50"
        elif price > 0:
            return "1-10"
        else:
            return "0"


def feat_sorter(feat):
    s = feat.find(':')
    if feat[s + 1:] == 'other':
        return int(feat[:s]), ' '
    return int(feat[:s]), feat[s + 1:]

namecol = {}
featindex = {}


def build_feature_map():
    print('building feature map on', sys.argv[1])
    featset = set()
    fi = open(sys.argv[1], 'r')
    first = True

    for line in fi:
        s = line.strip().split('\t')
        if first:
            first = False
            for i in range(0, len(s)):
                namecol[s[i]] = i
            for i in range(len(f1s) + len(f1sp)):
                featset.add(str(i) + ':other')
            continue
        for i, f in enumerate(f1s):
            col = namecol[f]
            content = s[col]
            feat = str(i) + ':' + content
            if feat not in featset:
                featset.add(feat)
        for i, f in enumerate(f1sp):
            col = namecol[f]
            content = featTrans(f, s[col])
            feat = str(i + len(f1s)) + ':' + content
            if feat not in featset:
                featset.add(feat)
    print('feature size:', len(featset))
    for s in sorted(featset, key=feat_sorter):
        featindex[s] = len(featindex)
    featvalue = sorted(featindex.iteritems(), key=operator.itemgetter(1))
    fo = open(sys.argv[5], 'w')
    for fv in featvalue:
        fo.write(fv[0] + '\t' + str(fv[1]) + '\n')
    fo.close()


def log_2_feature(fi, fo):
    print('indexing', fi)
    fi = open(fi, 'r')
    fo = open(fo, 'w')
    first = True
    for line in fi:
        if first:
            first = False
            continue
        s = line.split('\t')
        fo.write(s[0])  # click + winning price
        for i, f in enumerate(f1s):  # every direct first order feature
            col = namecol[f]
            content = s[col]
            feat = str(i) + ':' + content
            if feat not in featindex:
                feat = str(i) + ':other'
            index = featindex[feat]
            fo.write(' ' + str(index) + ":1")
        for i, f in enumerate(f1sp):
            col = namecol[f]
            content = featTrans(f, s[col])
            feat = str(i + len(f1s)) + ':' + content
            if feat not in featindex:
                feat = str(col) + ':other'
            index = featindex[feat]
            fo.write(' ' + str(index) + ":1")
        fo.write('\n')
    fo.close()


def check_alignment(file_name):
    print('checking alignment')
    max_length = 0
    max_feat = 0
    cnt = 0
    first = True
    with open(file_name, 'r') as fin:
        for line in fin:
            cnt += 1
            line = line.strip().split()[1:]
            line = [x.split(':')[0] for x in line]
            line = [int(x) for x in line]
            if first:
                first = False
                max_length = len(line)
                max_feat = max(line)
            else:
                max_length = max(max_length, len(line))
                max_feat = max(max_feat, max(line))
            check_sum = np.sum(np.abs(np.sort(line) - line))
            if check_sum > 0:
                print('alignment test failed', cnt, check_sum)
                print(line)
                exit()
            if cnt % 100000 == 0:
                print(cnt)


build_feature_map()
log_2_feature(sys.argv[2], sys.argv[4])
check_alignment(sys.argv[4])
log_2_feature(sys.argv[1], sys.argv[3])
