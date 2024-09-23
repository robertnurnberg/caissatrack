#!/bin/bash

# exit on errors
set -e

temp_file="_tmp_caissa_sorted_100000_cdbpv.epd"

if [ -f "$temp_file" ]; then
    echo "$temp_file already exists. Exiting."
    exit 0
fi

python ../cdblib/cdbbulkpv.py -c 24 --stable --user rob caissa_sorted_100000.epd >"$temp_file"

mv "$temp_file" caissa_sorted_100000_cdbpv.epd

python caissatrack.py >>caissatrack.csv
python extract_fens.py --shortest 1000 --ignore2folds >caissa_daily_shortest.epd
python extract_fens.py --evalMin 80 --evalMax 110 >caissa_daily_edgy.epd

git add caissa_sorted_100000_cdbpv.epd caissatrack.csv
git add caissa_daily_shortest.epd caissa_daily_edgy.epd
git diff --staged --quiet || git commit -m "update data"
git push origin main >&push.log
