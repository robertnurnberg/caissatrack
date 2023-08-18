#!/bin/bash

python3 plotdata.py --logplot --cutOff 200

git add caissatrack.png caissatrackpv.png
git diff --staged --quiet || git commit -m "update plots"
git push origin main >& push.log
