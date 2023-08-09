# Caissatrack

Track the evaluations of the 100k most popular positions in 
[Caissabase](http://www.caissabase.co.uk) on 
[chessdb.cn](https://chessdb.cn/queryc_en/) (cdb). The positions can be
found in [`caissa_sorted_100000.epd`](caissa_sorted_100000.epd), where they
appear in sorted order according to popularity. For example, the starting
position appears first. Thanks to Joost VandeVondele for preparing
`caissa_sorted_100000.epd` in July 2023.

The file [`caissa_sorted_100000_cdbpv.epd`](caissa_sorted_100000_cdbpv.epd) is created daily with the help of the script `cdbbulkpv.py` from [cdblib](https://github.com/robertnurnberg/cdblib), and the obtained statistics are written to [`caissatrack.csv`](caissatrack.csv).
In addition, the file [`caissa_daily100.epd`](caissa_daily100.epd) contains the
hundred positions with the currently shortest PVs on cdb.

---

<p align="center"> <img src="caissatrack.png?raw=true"> </p>

---

<p align="center"> <img src="caissatrackpv.png?raw=true"> </p>

---

If you want to help improve the coverage of these positions on cdb, you could
manually or systematically explore the positions in `caissa_daily100.epd` or `caissa_sorted_100000.epd`.
One way to do this is to clone [cdbexplore](https://github.com/vondele/cdbexplore) and then run either
```
python ../cdbexplore/cdbbulksearch.py --bulkConcurrency 16 --forever --depthLimit 10 caissa_daily100.epd
```
or
```
python ../cdbexplore/cdbbulksearch.py --bulkConcurrency 16 --forever --depthLimit 10 --shuffle caissa_sorted_100000.epd
```
