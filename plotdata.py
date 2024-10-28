import argparse, ast
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from matplotlib.offsetbox import AnchoredOffsetbox, TextArea, HPacker, VPacker
from matplotlib.ticker import MaxNLocator

evalIndicatorStr, depthIndicatorStr = "", ""


def eval_indicator(d):
    global evalIndicatorStr
    evalIndicatorStr = (
        r"$\frac{1}{N} \sum_i\ \left(\min\{\frac{|e_i|}{100},2\} - 1\right)^2$"
    )
    e = NoP = 0
    for k, v in d.items():
        k = min(abs(k), 200)
        e += v * (k / 100 - 1) ** 2
        NoP += v
    return e / NoP, NoP


def depth_indicator(d):
    global depthIndicatorStr
    depthIndicatorStr = r"$\sum_i\ \frac{1}{d_i}$"
    s = 0
    for k, v in d.items():
        if k > 0:
            s += v / k
    return s


def depth_average(d):
    c = s = 0
    for k, v in d.items():
        if k > 0:
            s += v * k
            c += v
    return s / c


def count_edgy_evals(d, lower, upper):
    c = 0
    for k, v in d.items():
        if lower <= abs(k) <= upper:
            c += v
    return c


class caissadata:
    def __init__(self, prefix):
        self.prefix = prefix
        self.date = []  # datetime entries
        self.evals = []  # eval distributions
        self.depths = []  # depth distributions
        with open(prefix + ".csv") as f:
            for line in f:
                line = line.strip()
                if line.startswith("Time"):
                    continue
                if line:
                    pos1 = line.find(",{")
                    pos2 = line.find("},{")
                    dateStr, _, _ = line.partition(",")
                    dict1Str = line[pos1 + 1 : pos2 + 1].replace(";", ",")
                    dict2Str = line[pos2 + 2 :].replace(";", ",")
                    self.date.append(dateStr)
                    self.evals.append(ast.literal_eval(dict1Str))
                    self.depths.append(ast.literal_eval(dict2Str))

    def create_distribution_graph(
        self, cutOff=125, logplot=False, pv=False, negplot=False
    ):
        color, edgecolor, label = ["red", "blue"], ["yellow", "black"], [None, None]
        dictList = [None, None]  # list for the two dicts to plot
        rangeMin, rangeMax = None, None
        for Idx in [0, -1]:
            dateStr, _, _ = self.date[Idx].partition("T")
            if pv:
                dictList[Idx] = self.depths[Idx].copy()
                # negative PV lengths mean PVs that end in a terminal draw
                for key, value in list(dictList[Idx].items()):
                    if key <= -10000 or (key < 0 and not negplot):
                        newkey = -(-key % 10000) if key <= -10000 else key
                        if not negplot:
                            newkey = -newkey
                        if key != newkey:
                            dictList[Idx][newkey] = dictList[Idx].get(newkey, 0) + value
                            del dictList[Idx][key]
                mi, ma = min(dictList[Idx].keys()), max(dictList[Idx].keys())
                if negplot and mi < 0 and ma > 0:
                    negmax = max([k for k in dictList[Idx].keys() if k < 0])
                    posmin = min([k for k in dictList[Idx].keys() if k > 0])
                    cup = r"$\cup$"
                    label[
                        Idx
                    ] = f"{dateStr}   (in [{mi}, {negmax}]{cup}[{posmin}, {ma}])"
                else:
                    label[Idx] = f"{dateStr}   (in [{mi}, {ma}])"
            else:
                dictList[Idx] = self.evals[Idx].copy()
                mi, ma = min(dictList[Idx].keys()), max(dictList[Idx].keys())
                label[Idx] = f"{dateStr}   (in [{mi}, {ma}])"
                for key in [-cutOff, cutOff]:
                    if key not in dictList[Idx]:
                        dictList[Idx][key] = 0
                for key, value in list(dictList[Idx].items()):
                    if key < -cutOff:
                        dictList[Idx][-cutOff] += value
                        del dictList[Idx][key]
                    elif key > cutOff:
                        dictList[Idx][cutOff] += value
                        del dictList[Idx][key]
            mi, ma = min(dictList[Idx].keys()), max(dictList[Idx].keys())
            rangeMin = mi if rangeMin is None else min(mi, rangeMin)
            rangeMax = ma if rangeMax is None else max(ma, rangeMax)
        fig, ax = plt.subplots()
        perBin = 2 if pv else 1 if cutOff <= 100 else 3  # values per bin
        for Idx in [0, -1]:
            ax.hist(
                dictList[Idx].keys(),
                weights=dictList[Idx].values(),
                range=(rangeMin, rangeMax),
                bins=(rangeMax - rangeMin) // perBin,
                alpha=0.5,
                color=color[Idx],
                edgecolor=edgecolor[Idx],
                label=label[Idx],
            )
            if pv:
                terminal = []
                term = [
                    "2fold",
                    "50mr",  # <= -10000
                    "stalemate",  # <= -20000
                    "mate",  # <= -30000
                    "TB draw",  # <= -40000
                    "TB win",  # <= -50000
                    "TB unknown",  # <= -60000
                ]
                for step in range(7):
                    c = sum(
                        [
                            v
                            for k, v in self.depths[Idx].items()
                            if -(step + 1) * 10000 < k
                            if k <= -step * 10000
                        ]
                    )
                    if c:
                        terminal.append(f"{term[step]} ({c})")
                terminalStr = "Terminal PV leafs: " + ", ".join(terminal)
                ax.text(
                    0.05,
                    0.02 - Idx * 0.02,
                    terminalStr,
                    transform=fig.transFigure,
                    color=color[Idx],
                    fontsize=6,
                    family="monospace",
                    weight="bold",
                )
        ax.legend(fontsize=7)
        bold = (r"$\bf{depths}$" + " (PV lengths in plies)") if pv else r"$\bf{evals}$"
        fig.suptitle(f"Distribution of cdb {bold} in {self.prefix}.csv.")
        if pv:
            if negplot:
                ax.set_title(
                    "(A negative depth -d means that a PV with d plies ends in a theoretically known result, with 2folds counting as 3folds.)",
                    fontsize=6,
                    family="monospace",
                )
        else:
            ax.set_title(
                f"(Evals outside of [-{cutOff},{cutOff}] are included in the +/-{cutOff} buckets.)",
                fontsize=6,
                family="monospace",
            )
        if logplot:
            ax.set_yscale("log")
        plt.savefig(self.prefix + ("pv" if pv else "") + ".png", dpi=300)

    def create_timeseries_graph(self, plotStart=0, edgeMin=None, edgeMax=None):
        dateData = [datetime.fromisoformat(d) for d in self.date[plotStart:]]
        evalsData, depthsData, NoP = [], [], 0

        for i, d in enumerate(self.evals[plotStart:]):
            e, n = eval_indicator(d)
            evalsData.append(e)
            if i and n != NoP:
                print(f"Warning: NoP changed from {NoP} to {n} at {dateData[i]}.")
            NoP = n
        for d in self.depths[plotStart:]:
            depthsData.append(depth_indicator(d))

        fig, ax = plt.subplots()
        yColor, dateColor = "black", "black"
        evalColor, depthColor = "blue", "firebrick"
        ax2 = ax.twinx()
        if len(dateData) >= 200:
            evalDotSize, evalLineWidth, evalAlpha = 2, 0.7, 0.75
        elif len(dateData) >= 100:
            evalDotSize, evalLineWidth, evalAlpha = 5, 1, 0.75
        else:
            evalDotSize, evalLineWidth, evalAlpha = 15, 1, 0.75
        depthDotSize, depthLineWidth, depthAlpha = evalDotSize, evalLineWidth, evalAlpha
        ax.scatter(
            dateData,
            evalsData,
            color=evalColor,
            s=evalDotSize,
            alpha=evalAlpha,
        )
        ax2.scatter(
            dateData,
            depthsData,
            color=depthColor,
            s=depthDotSize,
            alpha=depthAlpha,
        )
        ax.plot(
            dateData,
            evalsData,
            color=evalColor,
            linewidth=evalLineWidth,
            alpha=evalAlpha,
        )
        ax2.plot(
            dateData,
            depthsData,
            color=depthColor,
            linewidth=evalLineWidth,
            alpha=depthAlpha,
        )
        ax.tick_params(axis="y", labelcolor=evalColor)
        ax2.tick_params(axis="y", labelcolor=depthColor)
        ax2.ticklabel_format(axis="y", style="plain")
        if max(depthsData) >= 10**6:
            plt.setp(
                ax2.get_yticklabels(),
                fontsize=8,
            )
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
        plt.setp(
            ax.get_xticklabels(),
            rotation=45,
            ha="right",
            rotation_mode="anchor",
            fontsize=6,
        )
        ax.grid(alpha=0.4, linewidth=0.5)
        fig.suptitle(f"     Progress indicators from {self.prefix}.csv.")
        plt.figtext(0.02, 0.91, evalIndicatorStr, fontsize=9, color=evalColor)
        plt.figtext(0.91, 0.91, depthIndicatorStr, fontsize=9, color=depthColor)
        pair = r"$(e_i, d_i)$"
        infty = r"$d_i=\infty$"
        noStr = str(NoP)
        if noStr.endswith("0" * 9):
            noStr = noStr[:-9] + "G"  #  :)
        elif noStr.endswith("0" * 6):
            noStr = noStr[:-6] + "M"
        elif noStr.endswith("0" * 3):
            noStr = noStr[:-3] + "K"
        ax.set_title(
            f"     Based on {noStr} (eval, depth) data points {pair}, {infty} for terminal PVs.",
            fontsize=6,
            family="monospace",
        )
        # show start of stable PV usage
        stableDate, stableColor = datetime.fromisoformat("2023-08-24"), "green"
        if stableDate > dateData[0]:
            ax.axvline(x=stableDate, color=stableColor, linestyle="--", linewidth="1")
            yPos = min(evalsData) - 0.06 * (max(evalsData) - min(evalsData))
            ax.text(
                stableDate,
                yPos,
                "stable PV",
                color=stableColor,
                ha="center",
                va="top",
                rotation="vertical",
                fontsize=6,
                family="monospace",
                weight="bold",
            )
        if not (edgeMin is None or edgeMax is None):
            edgeData = []
            for d in self.evals[plotStart:]:
                edgeData.append(count_edgy_evals(d, edgeMin, edgeMax))
            ax3 = ax.twinx()
            edgeColor = "tab:pink"
            edgeDotSize, edgeLineWidth, edgeAlpha = (
                evalDotSize / 2,
                evalLineWidth / 2,
                evalAlpha / 2,
            )
            e_i = r"$ \leq |e_i| \leq $"
            edgeStr = f"#{{{edgeMin}{e_i}{edgeMax}}}"
            ax3.scatter(
                dateData,
                edgeData,
                label=edgeStr,
                color=edgeColor,
                s=edgeDotSize,
                alpha=edgeAlpha,
            )
            ax3.plot(
                dateData,
                edgeData,
                color=edgeColor,
                linewidth=edgeLineWidth,
                alpha=edgeAlpha,
            )
            legend = ax3.legend(fontsize=6, loc="upper left", labelcolor=edgeColor)
            legend.get_frame().set_alpha(0.5)
            t = [min(edgeData), max(edgeData)]
            ax3.set_yticks(t, t)
            maxDigits = len(str(t[1]))
            labelXpos = 1.06 + 0.01 * min(0, 4 - maxDigits)
            markerSize = 24 + 3 * min(0, 4 - maxDigits)
            plt.setp(
                ax3.get_yticklabels(),
                position=(labelXpos, 0),
                fontsize=6,
                color=edgeColor,
            )
            plt.setp(
                ax3.get_yticklines(),
                markersize=markerSize,
                markeredgewidth=0.2,
            )
            ax3.tick_params(axis="y", colors=edgeColor)

        plt.savefig(self.prefix + "time.png", dpi=300)

    def create_depth_graph(self, filename, plotStart=0):
        dateData = [datetime.fromisoformat(d) for d in self.date[plotStart:]]
        depthsAvg, depthsMin, depthsMax = [], [], []

        for d in self.depths[plotStart:]:
            depthsAvg.append(depth_average(d))
            depthsMax.append(max(d.keys()))
            depthsMin.append(min([k for k in d.keys() if k > 0]))

        fig, ax = plt.subplots()
        ax2 = ax.twinx()
        dotSize, lineWidth, alpha = 2, 0.7, 0.75
        ax.scatter(
            dateData,
            depthsAvg,
            color="black",
            s=dotSize,
            alpha=alpha,
        )
        ax.scatter(
            dateData,
            depthsMax,
            color="silver",
            s=dotSize,
            alpha=alpha,
        )
        ax2.scatter(
            dateData,
            depthsMin,
            color="red",
            s=dotSize,
            alpha=alpha,
        )
        ax.plot(
            dateData,
            depthsAvg,
            color="black",
            linewidth=lineWidth,
            alpha=alpha,
        )
        ax.tick_params(axis="y", labelcolor="black")
        ax2.tick_params(axis="y", labelcolor="red")
        ax2.ticklabel_format(axis="y", style="plain")
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
        plt.setp(
            ax.get_xticklabels(),
            rotation=45,
            ha="right",
            rotation_mode="anchor",
            fontsize=6,
        )
        ax.grid(alpha=0.4, linewidth=0.5)
        fig.suptitle(f" Non terminal PV lengths from {self.prefix}.csv over time.")
        ybox1 = TextArea(
            "average length",
            textprops=dict(size=9, color="black", rotation=90, ha="left", va="bottom"),
        )
        ybox2 = TextArea(
            "(and max length)",
            textprops=dict(size=6, color="silver", rotation=90, ha="left", va="bottom"),
        )
        ybox = VPacker(children=[ybox2, ybox1], align="center", pad=0, sep=5)
        anchored_ybox = AnchoredOffsetbox(
            loc=8,
            child=ybox,
            pad=0.0,
            frameon=False,
            bbox_to_anchor=(-0.1, 0.3),
            bbox_transform=ax.transAxes,
            borderpad=0.0,
        )
        ax.add_artist(anchored_ybox)
        ax2.set_ylabel("min length", color="red")

        plt.savefig(filename, dpi=300)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Plot data stored in e.g. caissatrack.csv.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "filename",
        nargs="?",
        help="File with cdb eval and PV length statistics over time.",
        default="caissatrack.csv",
    )
    parser.add_argument(
        "--cutOff",
        help="Cutoff value for the eval distribution plot.",
        type=int,
        default=125,
    )
    parser.add_argument(
        "--logplot",
        "-l",
        action="count",
        default=0,
        help="Use logplot for the distribution plot. Once just eval plot, twice also PV depth plot.",
    )
    parser.add_argument(
        "--negplot",
        action="store_true",
        help="Plot PV lines with negative depth separately.",
    )
    parser.add_argument(
        "--onlyTime",
        action="store_true",
        help="Create only time evolution graphs.",
    )
    parser.add_argument(
        "--edgeMin",
        help="Lower value for edgy evals to count in time evolution graphs.",
        type=int,
        default=None,
    )
    parser.add_argument(
        "--edgeMax",
        help="Upper value for edgy evals to count in time evolution graphs.",
        type=int,
        default=None,
    )
    parser.add_argument(
        "--PvLengthPlot",
        help="Optional filename for time series plot of PV length statistics.",
    )
    args = parser.parse_args()

    prefix, _, _ = args.filename.partition(".")
    data = caissadata(prefix)
    if not args.onlyTime:
        data.create_distribution_graph(cutOff=args.cutOff, logplot=args.logplot)
        data.create_distribution_graph(
            pv=True, logplot=args.logplot >= 2, negplot=args.negplot
        )
    if args.edgeMin is None or args.edgeMax is None:
        args.edgeMin = args.edgeMax = None
    data.create_timeseries_graph(edgeMin=args.edgeMin, edgeMax=args.edgeMax)
    if args.PvLengthPlot:
        data.create_depth_graph(args.PvLengthPlot)
