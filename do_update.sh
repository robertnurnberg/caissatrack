#!/bin/bash

python3 plotdata.py

git add caissatrack.png caissatrackpv.png
git diff --staged --quiet || git commit -m "update plots"
git push origin main >& push.log
