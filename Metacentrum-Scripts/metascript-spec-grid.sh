#!/bin/bash

# seq -> FIRST INCREMENT LAST

for ssc in 1 2 3 4 5 6 7 8 9 10 20
do
  for ttfw in 0.20 0.40 0.60 0.80 1.00 1.20 1.40 1.60 1.80 2.00
  do
	for cw in 0.80 0.85 0.90 0.95 1.00 1.05 1.10 1.15 1.20 1.25
        do
		echo $ndw $ttfw $dfpt $dfpap
		qsub -v SSC=$ssc,TTFW=$ttfw,CW=$cw script-spec-grid.sh
	done
  done
done
