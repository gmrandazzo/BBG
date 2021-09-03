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
import numpy as np
import pickle
from pathlib import Path
from urlfeaturizer import UrlFeaturizer
from urlfeaturizer import getfeatures

def load_models(mpath):
    header = None
    models = []
    model_path = Path(mpath)
    for fbin in model_path.glob("**/*.bin"):
        models.append(pickle.load(open(fbin, "rb")))
    header = np.load("%s/header.npy" % (model_path.resolve()))
    return models, header


def predict(url, models, header):
    u = UrlFeaturizer()
    features = getfeatures(url, u)
    vector = [[features[key] for key in header]]
    vector = np.array(vector)
    predictions = []
    for model in models:
        predictions.append(model.predict(vector))
    predictions = np.array(predictions)
    res = {"prediction": np.average(predictions),
           "stdev": np.std(predictions)}
    return res


def main():
    if len(sys.argv) != 3:
        print("\nUsage: %s [url] [model path]" % (sys.argv[0]))
    else:
        models, header = load_models(sys.argv[2])
        res = predict(sys.argv[1], models, header)
        print("%.4f %.4f" % (res["prediction"], res["stdev"]))
        return 0


if __name__ in "__main__":
    main()
