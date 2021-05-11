#!/bin/env bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

OUTDIR=${1:-/s2s-obs/}

cd $OUTDIR

for t in tmin; do 
    mkdir -p $t;
    for i in {1979..2021}; do
      wget http://iridl.ldeo.columbia.edu/SOURCES/.NOAA/.NCEP/.CPC/.temperature/.daily/.${t}/T/%281%20Jan%20${i}%29%2831%20Dec%20${i}%29RANGEEDGES/data.nc -O $t/data.$i.nc;
    done;
done

for t in tmax; do 
  mkdir -p $t;
  for i in {1979..2021}; do 
    wget http://iridl.ldeo.columbia.edu/SOURCES/.NOAA/.NCEP/.CPC/.temperature/.daily/.${t}/T/%281%20Jan%20${i}%29%2831%20Dec%20${i}%29RANGEEDGES/data.nc -O $t/data.$i.nc;
   done;
done

for t in rain; do
  mkdir -p $t;
  for i in {1979..2021}; do 
    wget http://iridl.ldeo.columbia.edu/SOURCES/.NOAA/.NCEP/.CPC/.UNIFIED_PRCP/.GAUGE_BASED/.GLOBAL/.v1p0/.extREALTIME/.rain/T/%280000%201%20Jan%20${i}%29%280000%2031%20Dec%20${i}%29RANGEEDGES/data.nc -O $t/data.$i.nc;
  done;
done

echo "data downloaded"
