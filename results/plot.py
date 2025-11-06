#!/usr/bin/env python3
import argparse
import csv
import glob
import math
import os
from collections import defaultdict
from statistics import mean

import matplotlib.pyplot as plt
import numpy as np


def parseLine(line: str):
    name, value = line.strip().split(":", 1)
    try:
        v = float(value) if (("." in value)) else float(int(value))
        return name, v
    except Exception:
        return name, value


def parseToBool(token: str):
    if token is None:
        return None

    s = str(token).strip().lower()

    if s == "true":
        return True
    if s in "false":
        return False
    return None


def computWinRate(path: str):
    with open(path, "r", newline="", encoding="utf-8") as f:
        lines = f.readlines()[2:]
    if not lines:
        return float("nan")

    bools = []
    for row in csv.DictReader(lines):
        b = parseToBool(row.get("win/fail"))
        if b is not None:
            bools.append(b)
    return mean(bools) if bools else float("nan")


def getParams(path: str):
    with open(path, "r", encoding="utf-8") as f:
        p1_name, p1_val = parseLine(f.readline())
        p2_name, p2_val = parseLine(f.readline())

    winrate = computWinRate(path)
    return (p1_name, p1_val, p2_name, p2_val, winrate)


def createMapping(values):
    nums = []
    map = {}
    rev = {}
    for v in values:
        if isinstance(v, (int, float)) and not isinstance(v, bool) and not math.isnan(float(v)):
            nums.append(float(v))
        else:
            s = str(v)
            if s not in map:
                map[s] = float(len(map))
                rev[map[s]] = s
            nums.append(map[s])
    return np.array(nums, dtype=float), map, rev


def getPoints(rootPath):
    paths = []
    for pattern in rootPath:
        paths.extend(glob.glob(pattern, recursive=True)) ##Big issue with this, I have to learn python properly 

    paths = [p for p in paths if os.path.isfile(p)]
    if not paths:
        raise SystemExit(f"No files found: {rootPath}") 

    points = []
    p1_name_set, p2_name_set = set(), set()
    for p in paths:
        try:
            p1name, p1val, p2name, p2val, winRate = getParams(p)
            points.append((p1name, p1val, p2name, p2val, winRate, p))
            p1_name_set.add(p1name)
            p2_name_set.add(p2name)
        except Exception as e:
            print(f"Skipping {p}: {e}")
    return points


def groupByParams(points):
    from collections import Counter
    p1Name = Counter([p[0] for p in points]).most_common(1)[0][0]
    p2Name = Counter([p[2] for p in points]).most_common(1)[0][0]

    bucket = defaultdict(list)
    for _, p1val, _, p2val, wr, _ in points:
        if math.isnan(wr):
            continue
        bucket[(p1val, p2val)].append(wr)

    P1Vals, P2Vals, W = [], [], []
    for (p1val, p2val), wrs in bucket.items():
        P1Vals.append(p1val)
        P2Vals.append(p2val)
        W.append(mean(wrs))

    XR = np.array(P1Vals, dtype=object)
    YR = np.array(P2Vals, dtype=object)
    X, map1, _ = createMapping(XR)
    Y, map2, _ = createMapping(YR)
    Z = np.array(W, dtype=float)
    
    return p1Name, p2Name, X, Y, Z, XR, YR, map1 if map1 else None, map2 if map2 else None


def plot(p1_name, p2_name, X, Y, Z, save=None, x_labels=None, y_labels=None):
    fig = plt.figure(figsize=(9, 7))
    ax = fig.add_subplot(111, projection="3d")

    ax.scatter(X, Y, Z, s=40, depthshade=True)
    if len(X) >= 3:
        try:
            ax.plot_trisurf(X, Y, Z, alpha=0.5)
        except Exception as e:
            print("Plotting error")

    ax.set_xlabel(p1_name)
    ax.set_ylabel(p2_name)
    ax.set_zlabel("Win rate")

    ax.set_zlim(0.0, 1.0)

    if x_labels:
        ax.set_xticks(sorted(x_labels.keys()))
        ax.set_xticklabels([x_labels[k] for k in sorted(x_labels.keys())], rotation=30, ha="right")
    if y_labels:
        ax.set_yticks(sorted(y_labels.keys()))
        ax.set_yticklabels([y_labels[k] for k in sorted(y_labels.keys())], rotation=30, ha="right")

    fig.tight_layout()
    if save:
        plt.savefig(save, dpi=150)
        print(f"Saved plot to {save}")
    plt.show()


def main():
    ap = argparse.ArgumentParser(description="3D plot of win rate vs two parameters from CSVs.")
    ap.add_argument("inputs", nargs="+")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    points = getPoints(args.inputs)
    p1n, p2n, X, Y, Z, _, _, cat1, cat2 = groupByParams(points)

    x_labels = None
    y_labels = None
    if cat1:
        x_labels = {float(idx): name for name, idx in cat1.items()}
    if cat2:
        y_labels = {float(idx): name for name, idx in cat2.items()}

    plot(p1n, p2n, X, Y, Z, save=args.out, x_labels=x_labels, y_labels=y_labels)


if __name__ == "__main__":
    main()