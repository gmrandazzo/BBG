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
from sklearn.metrics import average_precision_score
from sklearn.metrics import auc
from sklearn.metrics import accuracy_score
from sklearn.model_selection import KFold
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier


def read_csv_file(fcsv):
    X = []
    y = []
    h = None
    f = open(fcsv, "r")
    for line in f:
        if "#" in line:
            h = str.split(line.strip(), ",")
        else:
            v = str.split(line.strip(), ",")
            X.append(v[1:-1])
            y.append(v[-1])
    f.close()
    return np.array(X).astype(float), np.array(y).astype(int), h


def trainmodel(x_train,
               y_train,
               x_val,
               y_val,
               x_test,
               y_test):
    hp = {'base_score': 0.5,
          'colsample_bylevel': 1,
          'colsample_bytree': 0.66,
          'gamma': 0,
          'learning_rate': 0.05,
          'max_delta_step': 1,
          'max_depth': 5,
          'min_child_weight': 5,
          'n_estimators': 3000,
          'reg_alpha': 0,
          'reg_lambda': 1,
          'scale_pos_weight': 1,
          'subsample': 0.53}
    model = XGBClassifier(**hp)
    model.fit(x_train,
              y_train,
              eval_metric='error',
              eval_set=[(x_val, y_val)],
              verbose=0)
    y_train_p = model.predict(x_train)
    y_val_p = model.predict(x_val)
    y_test_p = model.predict(x_test)
    """
    print("Train")
    print("Accuracy: %.4f" % (accuracy_score(y_train, y_train_p)))
    # print("AUC     : %.4f" % (auc(y_train, y_train_p >= 0.5)))
    print("Av PR   : %.4f" % (average_precision_score(y_train, y_train_p >= 0.5)))
    print("Validation")
    print("Accuracy: %.4f" % (accuracy_score(y_val, y_val_p)))
    # print("AUC     : %.4f" % (auc(y_val, y_val_p >= 0.5)))
    print("Av PR   : %.4f" % (average_precision_score(y_val, y_val_p >= 0.5)))
    print("Test")
    t_acc = accuracy_score(y_test, y_test_p),
    t_ap = average_precision_score(y_test, y_test_p >= 0.5)
    print("Accuracy: %.4f" % (t_acc))
    # print("AUC     : %.4f" % (auc(y_test, y_test_p >= 0.5)))
    print("Av PR   : %.4f" % (t_ap))
    print("-"*18)
    """
    t_acc = accuracy_score(y_test, y_test_p),
    t_ap = average_precision_score(y_test, y_test_p >= 0.5)
    return model, t_acc, t_ap


def build_models(X, y, h, model_path):
    path_to_model = Path(model_path)
    path_to_model.mkdir(exist_ok=True)
    kf = KFold(n_splits=5, random_state=176892, shuffle=True)
    cv = 0
    test_accuracies = []
    test_average_precisions = []
    for subsample_ids, test_ids in kf.split(X):
        x_sub = X[subsample_ids]
        y_sub = y[subsample_ids]
        x_test = X[test_ids]
        y_test = y[test_ids]
        x_train, x_val, y_train, y_val = train_test_split(x_sub, y_sub,
                                                          test_size=0.20,
                                                          random_state=651567)
        model, test_acc, test_ap = trainmodel(x_train,
                                              y_train,
                                              x_val,
                                              y_val,
                                              x_test,
                                              y_test)
        test_accuracies.append(test_acc)
        test_average_precisions.append(test_ap)
        model_fname = "%s/%d.bin" % (str(path_to_model.resolve()), cv)
        pickle.dump(model, open(model_fname, "wb"))
        cv += 1
    np.save("%s/header.npy" % (str(path_to_model.resolve())), h[1:-1])
    print("Final model results")
    print("Accuracy: %.4f" % (np.average(test_accuracies)))
    print("Avg. PR : %.4f" % (np.average(test_average_precisions)))
    return 0


def main():
    if len(sys.argv) != 3:
        print("\n Usage: %s [input features-target] [output model]")
    else:
        X, y, h = read_csv_file(sys.argv[1])
        build_models(X, y, h, sys.argv[2])
    return


if __name__ in "__main__":
    main()
