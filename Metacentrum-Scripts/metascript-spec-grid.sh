#!/bin/bash

# seq -> FIRST INCREMENT LAST

for ssc in 1 3 4 5 6 7 8 9 10 20
do
  for ttfw in 0.20 0.40 0.60 0.80 1.00 1.20 1.40 1.60 1.80 2.00
  do
        echo $ndw $ttfw $dfpt $dfpap
	qsub -v SSC=$ssc,TTFW=$ttfw script-spec-grid.sh
  done
done
