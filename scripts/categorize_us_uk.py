import csv

reader = csv.reader(open("ubuntu_list.csv"))

for row in reader:
    us = row[0]
    uk = row[1]
    if uk.replace("ou", "o") == us:
        print(us, uk, "ou/o", sep=",")
    elif uk.replace("re", "er") == us:
        print(us, uk, "re/or", sep=",")
    elif uk.replace("re", "ere") == us:
        print(us, uk, "re/or", sep=",")
    elif uk.replace("ring", "ering") == us:
        print(us, uk, "re/or", sep=",")
    elif uk.replace("or", "er") == us:
        print(us, uk, "er/or", sep=",")
    elif uk.replace("ce", "se") == us:
        print(us, uk, "ce/se", sep=",")
    elif uk.replace("ine", "in") == us:
        print(us, uk, "ine/in", sep=",")
    elif uk.replace("ogue", "og") == us:
        print(us, uk, "ogue/og", sep=",")
    elif uk.replace("ally", "ly") == us:
        print(us, uk, "ally/ly", sep=",")
    elif us.replace("yz", "ys") == uk:
        print(us, uk, "yz/ys", sep=",")
    elif us.replace("iz", "is") == uk:
        print(us, uk, "iz/is", sep=",")
    elif uk.replace("ae", "e") == us:
        print(us, uk, "ae/e", sep=",")
    elif uk.replace("-", "") == us:
        print(us, uk, "hyphen", sep=",")
    elif us.replace("ll", "l") == uk:
        print(us, uk, "double", sep=",")
    elif us.replace("l", "ll") == uk:
        print(us, uk, "double", sep=",")
    elif row[2] == "Y" and len(set(us).intersection(set(uk))) < max(len(set(us)), len(set(uk))) - 2:
        print(us, uk, "semantic", sep=",")
    elif row[2] == "Y":
        print(us, uk, "unknown " + row[3], sep=",")
    else:
        print(us, uk, "unknown", sep=",")
