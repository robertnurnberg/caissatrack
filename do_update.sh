#!/bin/bash

python3 plotdata.py --logplot --cutOff 200 --negplot --logplot --edgeMin 85 --edgeMax 105

git add caissatrack.png caissatrackpv.png caissatracktime.png 
git diff --staged --quiet || git commit -m "update plots"
git push origin main >& push.log
