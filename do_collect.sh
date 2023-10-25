#!/bin/bash

temp_file="_tmp_caissa_sorted_100000_cdbpv.epd"

if [ -f "$temp_file" ]; then
    echo "$temp_file already exists. Exiting."
    exit 0
fi

python3 ../cdblib/cdbbulkpv.py -c 32 --stable --user rob caissa_sorted_100000.epd >"$temp_file"

mv "$temp_file" caissa_sorted_100000_cdbpv.epd

python3 caissatrack.py >>caissatrack.csv
python3 extract_fens.py --shortest 1000 --ignore2folds >caissa_daily_shortest.epd
python3 extract_fens.py --evalMin 85 --evalMax 105 >caissa_daily_edgy.epd

git add caissa_sorted_100000_cdbpv.epd caissatrack.csv
git add caissa_daily_shortest.epd caissa_daily_edgy.epd
git diff --staged --quiet || git commit -m "update data"
git push origin main >&push.log
