#!/usr/bin/env python3
import argparse
import csv
import glob
import math
import os
from collections import defaultdict, Counter
from statistics import mean, median, pstdev

import matplotlib.pyplot as plt
import numpy as np

FUNCS = {
    "mean": lambda xs: mean(xs) if xs else float("nan"),
    "median": lambda xs: median(xs) if xs else float("nan"),
}


def parseLine(line: str):
    name, value = line.strip().split(":", 1)
    try:
        v = float(value) if (("." in value)) else float(int(value))
        return name, v
    except Exception:
        return name, value


def getValue(token):
    if token is None:
        return None
    s = str(token).strip().lower()

    if s == "true":
        return 1.0
    if s in "false":
        return 0.0
    
    try:
        return float(s)
    except ValueError:
        pass
    return None


def getValues(path: str, valueName : str):
    with open(path, "r", newline="", encoding="utf-8") as f:
        lines = f.readlines()[2:]

    if not lines:
        return float("nan")

    rowHeader = csv.DictReader(lines)

    lower_map = {h.lower(): h for h in rowHeader.fieldnames}
    key = valueName.lower()
    if key not in lower_map:
        raise ValueError(f"Column with given name is not in the file.")
    col = lower_map[key]

    values = []
    for row in rowHeader:
        value = getValue(row.get(col))
        if value is not None and not math.isnan(value):
            values.append(value)

    return values


def getParams(path: str, valueName : str):
    with open(path, "r", encoding="utf-8") as f:
        p1_name, p1_val = parseLine(f.readline())
        p2_name, p2_val = parseLine(f.readline())

    values = getValues(path, valueName)
    if values == []:
        return p1_name, p1_val, p2_name, p2_val, []
    return p1_name, p1_val, p2_name, p2_val, values


def getPoints(rootPath: str, value_col : str):
    paths = []
    for pattern in rootPath:
        paths.extend(glob.glob(pattern, recursive=True)) ##Big issue with this, I have to learn python properly

    paths = [p for p in paths if os.path.isfile(p)]
    if not paths:
        raise SystemExit("No input files matched.")

    points = []
    for path in paths:
        try:
            p1name, p1value, p2name, p2value, values = getParams(path, value_col)
            if values:
                points.append((p1name, p1value, p2name, p2value, values))
        except Exception as e:
            print(f"Skipping {path}: {e}")

    if not points:
        raise SystemExit("NO data found!")
    return points


def groupByParams(points, agregationFunction):
    p1Name = Counter([r[0] for r in points]).most_common(1)[0][0]
    p2Name = Counter([r[2] for r in points]).most_common(1)[0][0]

    bucket = defaultdict(list)
    p1Values, p2Values = set(), set()
    for _, p1value, _, p2value, values in points:
        if not values:
            continue
        bucket[(p1value, p2value)].extend(values)
        p1Values.add(p1value)
        p2Values.add(p2value)

    xValues = sort(list(p1Values))
    yValues = sort(list(p2Values))

    computedValues = np.full((len(yValues), len(xValues)), np.nan)
    for i, y in enumerate(yValues):
        for j, x in enumerate(xValues):
            xs = bucket.get((x, y), [])
            computedValues[i, j] = FUNCS[agregationFunction](xs) if xs else np.nan

    return p1Name, p2Name, computedValues, xValues, yValues


def sort(values):
    try:
        _ = [float(v) for v in values]  #Checkign if all values are float
        return sorted(values, key=lambda x: float(x))
    except Exception:
        return sorted([str(v) for v in values], key=lambda s: (s.lower(), s))
    


def plotHeat(p1Name, p2Name, computedValues, xValues, yValues, zValueName, save):
    _, axis = plt.subplots(figsize=(8, 6))
    finite = computedValues[np.isfinite(computedValues)]
    if finite.size == 0 or np.nanmin(computedValues) == np.nanmax(computedValues):
        verticalMin, verticlMax = 0.0, 1.0
    else:
        verticalMin, verticlMax = float(np.nanmin(computedValues)), float(np.nanmax(computedValues))

    image = axis.imshow(computedValues, origin="lower", aspect="auto", cmap="viridis", vmin=verticalMin, vmax=verticlMax)

    axis.set_xlabel(p1Name)
    axis.set_ylabel(p2Name)
    axis.set_xticks(np.arange(len(xValues)))
    axis.set_xticklabels(xValues, rotation=45, ha="right")
    axis.set_yticks(np.arange(len(yValues)))
    axis.set_yticklabels(yValues)

    cbar = plt.colorbar(image, ax=axis)
    cbar.set_label(f"{zValueName}")

    nodeY, nodeX = computedValues.shape
    for i in range(nodeY):
        for j in range(nodeX):
            value = computedValues[i, j]
            text = f"{value}"
            color = "white" if (np.isfinite(value) and value < 0.5) else "black"
            axis.text(j, i, text, ha="center", va="center", color=color, fontsize=9, clip_on=True)

    axis.set_title(zValueName)
    plt.tight_layout()
    if save:
        plt.savefig(save, dpi=150)
        print(f"Saved to {save}")
    plt.show()


def plot3D(p1Name, p2Name, computedValues, xValues, yValues, zValueName, save):
    xIDS, yIDS = np.meshgrid(np.arange(len(xValues)), np.arange(len(yValues)))
    
    mask = np.isfinite(computedValues)
    X = xIDS[mask].ravel()
    Y = yIDS[mask].ravel()
    Z = computedValues[mask].ravel()

    fig = plt.figure(figsize=(9, 7))
    axis = fig.add_subplot(111, projection="3d")
    
    axis.scatter(X, Y, Z, s=40, depthshade=True)
    if X.size >= 3:
        try:
            axis.plot_trisurf(X, Y, Z, alpha=0.5)
        except Exception as e:
            print("Plotting error")

    axis.set_xlabel(p1Name)
    axis.set_ylabel(p2Name)
    axis.set_zlabel(zValueName)
    axis.set_xticks(np.arange(len(xValues)))
    axis.set_xticklabels(xValues, rotation=30, ha="right")
    axis.set_yticks(np.arange(len(yValues)))
    axis.set_yticklabels(yValues)
    axis.set_title(zValueName)

    fig.tight_layout()
    if save:
        plt.savefig(save, dpi=150)
        print(f"Saved plot to {save}")
    plt.show()


def main():
    ap = argparse.ArgumentParser(description="3D plot of win rate vs two parameters from CSVs.")
    ap.add_argument("inputs", nargs="+")
    ap.add_argument("--value-col", required=True)
    ap.add_argument("--aggreg", default="mean", choices=sorted(FUNCS.keys()))
    ap.add_argument("--plot", choices=["heatmap", "3d"], default="heatmap")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    p1name, p2name, grid, X, Y = groupByParams(getPoints(args.inputs, args.value_col), args.aggreg)

    if args.plot == "heatmap":
        plotHeat(p1name, p2name, grid, X, Y, args.value_col, args.out)
    else:
        plot3D(p1name, p2name, grid, X, Y, args.value_col, args.out)


if __name__ == "__main__":
    main()
