#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Train or evaluate a single classifier with its given set of hyperparameters.

Created on Wed Sep 29 14:23:48 2021

@author: lbechberger
"""

import argparse, pickle
from sklearn.dummy import DummyClassifier
from sklearn.metrics import accuracy_score, cohen_kappa_score, f1_score, balanced_accuracy_score
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.naive_bayes import ComplementNB
from sklearn.pipeline import make_pipeline
from mlflow import log_metric, log_param, set_tracking_uri

# setting up CLI
parser = argparse.ArgumentParser(description = "Classifier")
parser.add_argument("input_file", help = "path to the input pickle file")
parser.add_argument("-s", '--seed', type = int, help = "seed for the random number generator", default = None)
parser.add_argument("-e", "--export_file", help = "export the trained classifier to the given location", default = None)
parser.add_argument("-i", "--import_file", help = "import a trained classifier from the given location", default = None)

# <--- Classifier --->
parser.add_argument("-m", "--majority", action = "store_true", help = "majority class classifier")
parser.add_argument("-f", "--frequency", action = "store_true", help = "label frequency classifier")
parser.add_argument("-u", "--uniform", action = "store_true", help = "uniform (random) classifier")
parser.add_argument("--knn", type = int, help = "k nearest neighbor classifier with the specified value of k", default = None)
parser.add_argument("--knn_weights", type = str, help = "weight function of knn, uniform or distance", default = "uniform")
parser.add_argument("--tree", action = "store_true", help = "decision tree classifier", default = None)
parser.add_argument("--tree_depth", type = int, help = "max depth of decision tree", default = None)
parser.add_argument("--tree_criterion", type = str, help = "criterion to measure split quality, gini or entropy", default = "gini")
parser.add_argument("--svm", type = str, help = "support vector machine with specified kernel: linear, polynomial, rbf, or sigmoid", default = None)
parser.add_argument("--randforest", type = int, help = "random forest classifier with specified value as # of trees in forest", default = None)
parser.add_argument("--forest_criterion", type = str, help = "criterion to measure split quality, gini or entropy", default = "gini")
parser.add_argument("--forest_max_depth", type = int, help = "max depth of trees in forest", default = None)
parser.add_argument("--mlp", nargs = "+", type = int, help = "multilayer perceptron classifier, values resemble hidden layer sizes (1 value per layer)", default = None)
parser.add_argument("--bayes", action = "store_true", help = "complement naive bayes classifier")

# <--- Evaluation metrics --->
parser.add_argument("-a", "--accuracy", action = "store_true", help = "evaluate using accuracy")
parser.add_argument("-k", "--kappa", action = "store_true", help = "evaluate using Cohen's kappa")
parser.add_argument("-f1", "--f1_score", action = "store_true", help = "evaluate using F1 score")
parser.add_argument("-ba", "--balanced_accuracy", action = "store_true", help = "evaluate using balanced accuracy score")

# <--- Param optimization --->
parser.add_argument("--log_folder", help = "where to log the mlflow results", default = "data/classification/mlflow")

args = parser.parse_args()

# load data
with open(args.input_file, 'rb') as f_in:
    data = pickle.load(f_in)

set_tracking_uri(args.log_folder)

if args.import_file is not None:
    # import a pre-trained classifier
    with open(args.import_file, 'rb') as f_in:
        input_dict = pickle.load(f_in)
    
    classifier = input_dict["classifier"]
    for param, value in input_dict["params"].items():
        log_param(param, value)
    
    log_param("dataset", "validation")

else:   # manually set up a classifier
    
    if args.majority:
        # majority vote classifier
        print("    majority vote classifier")
        log_param("classifier", "majority")
        params = {"classifier": "majority"}
        classifier = DummyClassifier(strategy = "most_frequent", random_state = args.seed)
        
    elif args.frequency:
        # label frequency classifier
        print("    label frequency classifier")
        log_param("classifier", "stratified")
        params = {"classifier": "stratified"}
        classifier = DummyClassifier(strategy = "stratified", random_state = args.seed)
        
    elif args.uniform:
        # uniform classifier
        print("    uniform classifier")
        log_param("classifier", "uniform")
        params = {"classifier": "uniform"}
        classifier = DummyClassifier(strategy = "uniform", random_state = args.seed)
    
    elif args.knn is not None:
        # k nearest neighbour classifier
        print("    {0} nearest neighbor classifier, {1} weights".format(args.knn, args.knn_weights))
        
        log_param("classifier", "knn")
        log_param("k", args.knn)
        log_param("weights", args.knn_weights)
        params = {"classifier": "knn", 
                  "k": args.knn, 
                  "weights": args.knn_weights}
        
        standardizer = StandardScaler()
        knn_classifier = KNeighborsClassifier(n_neighbors = args.knn, weights = args.knn_weights, n_jobs = -1)
        classifier = make_pipeline(standardizer, knn_classifier)
        
    elif args.tree is not None:
        # decision tree classifier
        print("    decision tree with max depth {0}, {1} split criterion".format(args.tree_depth, args.tree_criterion))
        
        log_param("classifier", "tree")
        log_param("criterion", args.tree_criterion)
        log_param("max_depth", args.tree_depth)
        params = {"classifier": "tree", 
                  "criterion": args.tree_criterion, 
                  "max_depth": args.tree_depth}
        
        #standardizer = StandardScaler()
        classifier = DecisionTreeClassifier(criterion = args.tree_criterion, max_depth = args.tree_depth)
        #classifier = make_pipeline(standardizer, decision_tree)
    
    elif args.svm is not None:
        # support vector machine
        print("    svm classifier, kernel: {0}".format(args.svm))
        
        log_param("classifier", "svm")
        log_param("kernel", args.svm)
        params = {"classifier": "svm", 
                  "kernel": args.svm}
        
        standardizer = StandardScaler()
        svm_classifier = SVC(kernel = args.svm, gamma = "auto")
        classifier = make_pipeline(standardizer, svm_classifier)
        
    elif args.randforest is not None:
        # random forest classifier
        print("    random forest classifier with {0} trees, max depth {1}, {2} criterion".format(args.randforest, args.forest_max_depth, args.forest_criterion))
        
        log_param("classifier", "random forest")
        log_param("nr trees", args.randforest)
        log_param("max depth", args.forest_max_depth)
        log_param("criterion", args.forest_criterion)
        params = {"classifier": "random forest", 
                  "nr trees": args.randforest,
                  "max depth": args.forest_max_depth,
                  "criterion": args.forest_criterion}
        
        classifier = RandomForestClassifier(n_estimators = args.randforest, criterion = args.forest_criterion, max_depth = args.forest_max_depth, n_jobs = -1)
        
    elif args.mlp is not None:
        # multilayer perceptron
        print("    multilayer perceptron with hidden layer size {0}".format(args.mlp))
        
        log_param("classifier", "mlp")
        log_param("hidden layer sizes", args.mlp)
        params = {"classifier": "mlp",
                  "hidden layer sizes": args.mlp}
        
        standardizer = StandardScaler()
        mlp_classifier = MLPClassifier(hidden_layer_sizes = tuple(args.mlp))
        classifier = make_pipeline(standardizer, mlp_classifier)
        
    elif args.bayes:
        # gaussian naive bayes
        print("    complement NB classifier")
        
        log_param("classifier", "complementNB")
        params = {"classifier": "complementNB"}
        
        #standardizer = StandardScaler()
        classifier = ComplementNB()
        #classifier = make_pipeline(standardizer, nb_classifer)
        
    classifier.fit(data["features"], data["labels"].ravel())
    log_param("dataset", "training")

# now classify the given data
prediction = classifier.predict(data["features"])

# collect all evaluation metrics
evaluation_metrics = []
if args.accuracy:
    evaluation_metrics.append(("Accuracy", accuracy_score))
if args.kappa:
    evaluation_metrics.append(("Cohens_kappa", cohen_kappa_score))
if args.f1_score:
    evaluation_metrics.append(("F1_score", f1_score))
if args.balanced_accuracy:
    evaluation_metrics.append(("Balanced_accuracy", balanced_accuracy_score))

# compute and print them
for metric_name, metric in evaluation_metrics:
    metric_value = metric(data["labels"], prediction)
    print("    {0}: {1}".format(metric_name, metric_value))
    log_metric(metric_name, metric_value)
    
# export the trained classifier if the user wants us to do so
if args.export_file is not None:
    output_dict = {"classifier": classifier, "params": params}
    with open(args.export_file, 'wb') as f_out:
        pickle.dump(output_dict, f_out)