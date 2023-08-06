# Caissatrack

Track the evaluations of the 100k most popular positions in 
[Caissabase](http://www.caissabase.co.uk) on 
[chessdb.cn](https://chessdb.cn/queryc_en/) (cdb). The positions can be
found in [`caissa_sorted_100000.epd`](caissa_sorted_100000.epd), where they
appear in sorted order according to popularity. For example, the starting
positions appears first. Thanks to Joost VandeVondele for preparing
the file `caissa_sorted_100000.epd` in July 2023.

The file [`caissa_sorted_100000_cdbpv.epd`](caissa_sorted_100000_cdbpv.epd) is periodically created with the help of the script `cdbbulkpv.py` from [cdblib](https://github.com/robertnurnberg/cdblib), and the obtained statistics are written to [`caissatrack.csv`](caissatrack.csv).

---

<p align="center"> <img src="caissatrack.png?raw=true"> </p>

---

<p align="center"> <img src="caissatrackpv.png?raw=true"> </p>

---

If you want to help improving the coverage of these positions on cdb,
you could run the command 
```
python cdbbulksearch.py --bulkConcurrency 16 --forever --depthLimit 10 --shuffle caissa_sorted_100000.epd
```
from time to time after having cloned
[cdbexplore](https://github.com/vondele/cdbexplore).
