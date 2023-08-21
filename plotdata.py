import argparse, ast
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from matplotlib.ticker import MaxNLocator


class matedata:
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
                    dateStr, _, _ = line.partition("T")
                    dict1Str = line[pos1 + 1 : pos2 + 1].replace(";", ",")
                    dict2Str = line[pos2 + 2 :].replace(";", ",")
                    self.date.append(dateStr)
                    self.evals.append(ast.literal_eval(dict1Str))
                    self.depths.append(ast.literal_eval(dict2Str))

    def create_graph(self, cutOff=125, logplot=False, pv=False, negplot=False):
        color, edgecolor, label = ["red", "blue"], ["yellow", "black"], [None, None]
        dictList = [None, None]  # list for the two dicts to plot
        rangeMin, rangeMax = None, None
        for Idx in [0, -1]:
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
                    label[Idx] = (
                        str(self.date[Idx])
                        + f"   (in [{mi}, {negmax}]{cup}[{posmin}, {ma}])"
                    )
                else:
                    label[Idx] = str(self.date[Idx]) + f"   (in [{mi}, {ma}])"
            else:
                dictList[Idx] = self.evals[Idx]
                mi, ma = min(dictList[Idx].keys()), max(dictList[Idx].keys())
                label[Idx] = str(self.date[Idx]) + f"   (in [{mi}, {ma}])"
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
        for Idx in [-1, 0]:
            listIdx = [key for key, val in dictList[Idx].items() for _ in range(val)]
            ax.hist(
                listIdx,
                range=(rangeMin, rangeMax),
                bins=(rangeMax - rangeMin) // perBin,
                density=True,
                alpha=0.5,
                color=color[Idx],
                edgecolor=edgecolor[Idx],
                label=label[Idx],
            )
            if pv:
                terminal = []
                term = [
                    "2fold",
                    "50 mr",  # <= -10000
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
                    0.1,
                    0.02 - Idx * 0.02,
                    terminalStr,
                    transform=fig.transFigure,
                    color=color[Idx],
                    fontsize=6,
                    family="monospace",
                    weight="bold",
                )
        ax.legend(fontsize=8)
        fig.suptitle(
            f"Distribution of cdb {'depths' if pv else 'evals'} in {self.prefix}.csv."
        )
        if pv:
            if negplot:
                ax.set_title(
                    "(A negative depth means that the PV ends in a theoretically known result, with 2folds counting as 3folds.)",
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
        action="count",
        default=0,
        help="Use logplot for the distribution plot. Once just eval plot, twice also PV depth plot.",
    )
    parser.add_argument(
        "--negplot",
        action="store_true",
        help="Plot PV lines with negative depth separately.",
    )
    args = parser.parse_args()

    prefix, _, _ = args.filename.partition(".")
    data = matedata(prefix)
    data.create_graph(cutOff=args.cutOff, logplot=args.logplot)
    data.create_graph(pv=True, logplot=args.logplot >= 2, negplot=args.negplot)
