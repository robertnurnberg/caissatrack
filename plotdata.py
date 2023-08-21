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
        dateOld, dateNew = str(self.date[0]), str(self.date[-1])
        if pv:
            dictOld, dictNew = self.depths[0], self.depths[-1]
            # negative PV lengths mean PVs that end in a terminal draw
            for d in [dictOld, dictNew]:
                for key, value in list(d.items()):
                    if key <= -10000 or (key < 0 and not negplot):
                        newkey = -(-key % 10000) if key <= -10000 else key
                        if not negplot:
                            newkey = -newkey
                        if key != newkey:
                            d[newkey] = d.get(newkey, 0) + value
                            del d[key]
            rangeOld = min(dictOld.keys()), max(dictOld.keys())
            rangeNew = min(dictNew.keys()), max(dictNew.keys())
        else:
            dictOld, dictNew = self.evals[0], self.evals[-1]
            rangeOld = min(dictOld.keys()), max(dictOld.keys())
            rangeNew = min(dictNew.keys()), max(dictNew.keys())
            for d in [dictOld, dictNew]:
                for key in [-cutOff, cutOff]:
                    if key not in d:
                        d[key] = 0
                for key, value in list(d.items()):
                    if key < -cutOff:
                        d[-cutOff] += value
                        del d[key]
                    elif key > cutOff:
                        d[cutOff] += value
                        del d[key]

        rangeMin = min(list(dictOld.keys()) + list(dictNew.keys()))
        rangeMax = max(list(dictOld.keys()) + list(dictNew.keys()))
        fig, ax = plt.subplots()
        listNew = [key for key, val in dictNew.items() for _ in range(val)]
        perBin = 2 if pv else 1 if cutOff <= 100 else 3  # values per bin
        ax.hist(
            listNew,
            range=(rangeMin, rangeMax),
            bins=(rangeMax - rangeMin) // perBin,
            density=True,
            alpha=0.5,
            color="blue",
            edgecolor="black",
            label=dateNew + f"   (in [{rangeNew[0]}, {rangeNew[1]}])",
        )
        listOld = [key for key, val in dictOld.items() for _ in range(val)]
        ax.hist(
            listOld,
            range=(rangeMin, rangeMax),
            bins=(rangeMax - rangeMin) // perBin,
            density=True,
            alpha=0.5,
            color="red",
            edgecolor="yellow",
            label=dateOld + f"   (in [{rangeOld[0]}, {rangeOld[1]}])",
        )
        ax.legend(fontsize=8)
        fig.suptitle(
            f"Distribution of cdb {'depths' if pv else 'evals'} in {self.prefix}.csv."
        )
        if pv:
            if negplot:
                ax.set_title(
                    "(A negative depth means that the PV ends in a theoretical draw.)",
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
        action="store_true",
        help="Use logplot for the eval distribution plot.",
    )
    parser.add_argument(
        "--negplot",
        action="store_true",
        help="Plot lines with negative depth separately.",
    )
    args = parser.parse_args()

    prefix, _, _ = args.filename.partition(".")
    data = matedata(prefix)
    data.create_graph(cutOff=args.cutOff, logplot=args.logplot)
    data.create_graph(pv=True, negplot=args.negplot)
