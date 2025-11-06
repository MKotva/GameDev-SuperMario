#!/bin/bash
#PBS -l walltime=10:00:00
#PBS -l select=1:ncpus=1:mem=4gb:scratch_local=1gb:cluster=elmo1
#PBS -e /storage/praha1/home/mkotva/job_logs
#PBS -o /storage/praha1/home/mkotva/job_logs

DATADIR=/storage/praha1/home/mkotva/repo/GameDev-SuperMario
RESULTDIR=/storage/praha1/home/mkotva/results/third
ROOT=/storage/praha1/home/mkotva

echo "$PBS_JOBID is running on node `hostname -f` in a scratch directory $SCRATCHDIR" >> $DATADIR/jobs_info.txt

module add openjdk-17

# test if scratch directory is set
# if scratch directory is not set, issue error message and exit
test -n "$SCRATCHDIR" || { echo >&2 "Variable SCRATCHDIR is not set!"; exit 1; }

cp -R $DATADIR/Mario-AI-Framework $SCRATCHDIR || { echo >&2 "Error while copying input file(s)!"; exit 2; }

cd $SCRATCHDIR/Mario-AI-Framework

# compile and run Java
javac -cp src src/mff/agents/benchmark/AgentBenchmarkMetacentrum.java
java -cp src mff.agents.benchmark.AgentBenchmarkMetacentrum

# move output to data dir
mkdir -p $RESULTDIR
cp -a agent-benchmark/. $RESULTDIR/ || { echo >&2 "Error while copying output file(s) to result dir!"; exit 2; }

clean_scratch
