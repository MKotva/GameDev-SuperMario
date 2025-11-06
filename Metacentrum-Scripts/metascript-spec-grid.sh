#!/bin/bash

# seq -> FIRST INCREMENT LAST

for ssc in 3 6 9 10
do
  for ttfw in 0.20 0.40 0.60 0.80 1.00 1.20 1.40 1.60 1.80 2.00
  do
	for vw in -0.06 -0.04 -0.03 -0.01 0.01 0.03 0.04 0.06
        do
		echo $ndw $ttfw $dfpt $dfpap
		qsub -v SSC=$ssc,TTFW=$ttfw,VW=$vw script-spec-grid.sh
	done
  done
done
