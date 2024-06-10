#!/bin/bash

python3 plotdata.py --logplot --cutOff 200 --negplot --logplot --edgeMin 70 --edgeMax 110 --PvLengthPlot pvlength.png

git add caissatrack.png caissatrackpv.png caissatracktime.png
git diff --staged --quiet || git commit -m "update plots"
git push origin main >&push.log
