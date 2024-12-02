# Caissatrack

Track the evaluations of the 100k most popular positions in 
[Caissabase](http://www.caissabase.co.uk) on 
[chessdb.cn](https://chessdb.cn/queryc_en/) (cdb). The positions can be
found in [`caissa_sorted_100000.epd`](caissa_sorted_100000.epd), where they
appear in sorted order according to popularity. For example, the starting
position appears first. The average depth of these positions is 14.6 plies,
with the deepest one 42 plies away from the starting position. The positions
have 30.3 pieces on average, and none has fewer than 18 pieces on the board.\
Thanks to Joost VandeVondele for preparing `caissa_sorted_100000.epd` in July 
2023.

The file [`caissa_sorted_100000_cdbpv.epd`](caissa_sorted_100000_cdbpv.epd) 
contains the current cdb evaluations and PVs for each position. It is created 
daily with the help of the script `cdbbulkpv.py` from 
[cdblib](https://github.com/robertnurnberg/cdblib), and the obtained statistics
are written to [`caissatrack.csv`](caissatrack.csv).
Moreover, each day the thousand positions with the currently shortest PVs on cdb
(ignoring PVs ending in a two-fold repetition)
are written to [`caissa_daily_shortest.epd`](caissa_daily_shortest.epd), and
the positions with absolute evaluations in the interval [80, 110]
are written to [`caissa_daily_edgy.epd`](caissa_daily_edgy.epd).

---

<p align="center"> <img src="caissatrack.png?raw=true"> </p>

---

<p align="center"> <img src="caissatrackpv.png?raw=true"> </p>

---

## Progress

The following graphs attempt to measure the progress cdb makes in exploring
and evaluating the positions in `caissa_sorted_100000.epd`.\
They plot the evolutions in time of the two (daily) indicators
```math
E = \frac{1}{N} \sum_i \left(\min\{\frac{|e_i|}{100},2\} - 1\right)^2
\qquad \text{and} \qquad
D=\sum_i \frac{1}{d_i},
```
where $(e_i, d_i)$ are the evaluation and depth values for the 100K positions,
with the convention that $d_i = \infty$ if the position's PV ends in a terminal
leaf (2-fold repetition, 50 moves rule, stalemate, checkmate or 7men EGTB).
$E$ measures how certain cdb's evaluations are, while $D$ simply sums the
inverses of the lengths of the non-resolved PVs. Note that as cdb (slowly) 
approaches the 32men EGTB, $E$ should converge to 1, while $D$
should converge to 0.\
In addition the graphs also show the evolution of the total number of "on edge"
positions. The first graph shows all available data points, while the second
graph depicts only the 100 most recent data points.

<p align="center"> <img src="caissatracktime.png?raw=true"> </p>

<p align="center"> <img src="caissatracktime-100.png?raw=true"> </p>

---

## Get involved

If you want to help improve the coverage of these positions on cdb, you could
manually or systematically explore them on [chessdb.cn](
https://chessdb.cn/queryc_en/). As an example for the latter, you could clone
this and Joost VandeVondele's repo [cdbexplore](
https://github.com/vondele/cdbexplore) via
```shell
git clone https://github.com/robertnurnberg/caissatrack && git clone https://github.com/vondele/cdbexplore && pip install -r cdbexplore/requirements.txt
```
and then from within the cloned `caissatrack` repo either run
```shell
git pull && cat caissa_daily_shortest.epd caissa_daily_edgy.epd > caissa_daily.epd && python ../cdbexplore/cdbbulksearch.py --bulkConcurrency 16 --forever --shuffle caissa_daily.epd
```
occasionally, or run
```shell
python ../cdbexplore/cdbbulksearch.py --bulkConcurrency 16 --forever --depthLimit 10 --shuffle caissa_sorted_100000.epd
```
as a long-term job.

An automated solution is to run the script [`launch_caissa_daily.sh`](
https://raw.githubusercontent.com/robertnurnberg/caissatrack/main/launch_caissa_daily.sh)
automatically via `.crontab` entries of the form
```
@reboot sleep 20 && /path_to_script/launch_caissa_daily.sh
55 6 * * * cd git/caissatrack && git pull
```
where the second entry is really only needed for server-like machines that run
24/7.

---

## Get in touch

To discuss anything cdb related, and to help cdb grow at a healthy pace, join
other (computer) chess enthusiasts at the [chessdbcn channel](
https://discord.com/channels/435943710472011776/1101022188313772083) on the
[Stockfish discord server](https://discord.gg/ZzJwPv3).
