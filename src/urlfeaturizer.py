#!/usr/bin/env python3
"""
Copyright (C) <2021>  Giuseppe Marco Randazzo <gmrandazzo@gmail.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import sys
import math
import pandas as pd
from cosine import text_to_vector
from cosine import get_cosine


class UrlFeaturizer(object):
    def __init__(self,
                 urls_enabled_file="urls_allowed.txt",
                 urls_disabled_file="urls_disabled.txt"):
        self.urls_enabled = self.readurlfile(urls_enabled_file)
        self.urls_disabled = self.readurlfile(urls_disabled_file)

    def readurlfile(self, furls):
        lst = []
        f = open(furls, "r")
        for line in f:
            lst.append(line.strip())
        f.close()
        return lst

    def entropy(self, url):
        string = url.strip()
        prob = [float(string.count(c)) / len(string)
                for c in dict.fromkeys(list(string))]
        entropy = sum([(p * math.log(p) / math.log(2.0)) for p in prob])
        return entropy

    def numDigits(self, url):
        digits = [i for i in url if i.isdigit()]
        return len(digits)

    def numCharacters(self, url):
        chars = [i for i in url if i.isalpha()]
        return len(chars)

    def numSpecialCharacters(self, url):
        n_schars = 0
        for ch in url:
            if ch.isdigit() and not ch.isalpha():
                n_schars += 1
            else:
                continue
        return n_schars

    def urlLength(self, url):
        return len(url)

    def numParameters(self, url):
        params = url.split('&')
        return len(params) - 1

    def numFragments(self, url):
        fragments = url.split('#')
        return len(fragments) - 1

    def numSubDomains(self, url):
        subdomains = url.split('http')[-1].split('//')[-1].split('/')
        return len(subdomains)-1

    def getAllowedDisallowedUrlsVector(self, url):
        fvect = {}
        v1 = text_to_vector(url)
        i = 0
        for aurl in self.urls_enabled:
            v2 = text_to_vector(aurl)
            fvect["fvect_AURL%.4d" % (i)] = get_cosine(v1, v2)
            i += 1
        i = 0
        for durl in self.urls_disabled:
            v2 = text_to_vector(durl)
            fvect["fvect_DURL%.4d" % (i)] = get_cosine(v1, v2)
            i += 1
        return fvect

    def get_features(self, url):
        data = {}
        data['entropy'] = self.entropy(url)
        data['numDigits'] = self.numDigits(url)
        data['numChar'] = self.numCharacters(url)
        data['numSpecialChar'] = self.numSpecialCharacters(url)
        data['urlLength'] = self.urlLength(url)
        data['numParams'] = self.numParameters(url)
        data['numFrag'] = self.numFragments(url)
        data['numSubDom'] = self.numSubDomains(url)
        data['num_%20'] = url.count("%20")
        data['num_@'] = url.count("@")
        """
        fvect = self.getAllowedDisallowedUrlsVector(url)
        for key in fvect:
            data[key] = fvect[key]
        """
        return data


def get_cutted_features(url, url_featurizer, sizemax):
    if sizemax is None:
        return url_featurizer.get_features(url)
    else:
        if len(url) >= sizemax:
            return url_featurizer.get_features(url[0:sizemax])
        else:
            return url_featurizer.get_features(url)

def getfeatures(url, url_featurizer):
    v1 = get_cutted_features(url, url_featurizer, None)
    v2 = get_cutted_features(url, url_featurizer, 50)
    v3 = get_cutted_features(url, url_featurizer, 30)
    v4 = get_cutted_features(url, url_featurizer, 20)
    feats = {}
    for key in v1.keys():
        feats[key] = v1[key]
        feats["len50_%s" % (key)] = v2[key]
        feats["len30_%s" % (key)] = v3[key]
        feats["len20_%s" % (key)] = v4[key]
    return feats

def demo():
    url = "/dns-query?dns=KhUBAAABAAAAAAAAA3d3dwZnb29nbGUDY29tAAABAAE"
    a = UrlFeaturizer()
    data = a.get_features(url)
    print(data)


def main():
    if len(sys.argv) != 3:
        print(f'Usage {sys.argv[0]} [CSV file] [OUTPUT file]') 
        return

    d = pd.read_csv(sys.argv[1])
    fo = open(sys.argv[2], "w")
    write_header = True
    header = []
    i = 0
    u = UrlFeaturizer()
    for row in d.values:
        f = getfeatures(row[0], u)
        if write_header is True:
            fo.write("#Instance")
            for item in f.keys():
                fo.write(",%s" % (item))
                header.append(item)
            fo.write(",target\n")
            write_header = False

        fo.write("Instance%d" % (i))
        for item in header:
            fo.write(",%s" % (f[item]))
        fo.write(",%s\n" % (row[1]))
        i += 1
    fo.close()


if __name__ in "__main__":
    main()
    # demo()
