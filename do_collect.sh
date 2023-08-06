#!/bin/bash

python3 ../cdblib/cdbbulkpv.py --user rob caissa_sorted_100000.epd > caissa_sorted_100000_cdbpv.epd
python3 caissatrack.py >> caissatrack.csv

git add caissa_sorted_100000_cdbpv.epd
git diff --staged --quiet || git commit -m "update data"
git push origin main >& push.log
