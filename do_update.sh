#!/bin/bash

python3 plotdata.py --logplot --cutOff 200 --negplot --logplot --edgeMin 80 --edgeMax 110

git add caissatrack.png caissatrackpv.png caissatracktime.png
git diff --staged --quiet || git commit -m "update plots"
git push origin main >&push.log
