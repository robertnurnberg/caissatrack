#!/bin/bash

python plotdata.py --cutOff 200 --negplot -ll --edgeMin 80 --edgeMax 110 --PvLengthPlot pvlength.png

git add caissatrack.png caissatrackpv.png caissatracktime.png caissatracktime-100.png
git diff --staged --quiet || git commit -m "update plots"
git push origin main >&push.log
