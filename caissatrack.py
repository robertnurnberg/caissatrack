import argparse, os, datetime

parser = argparse.ArgumentParser(
    description="Extract cdb eval and PV length statistics from an .epd file.",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)
parser.add_argument(
    "filename",
    nargs="?",
    help="file with scored FENs",
    default="caissa_sorted_100000_cdbpv.epd",
)
parser.add_argument("--debug", action="store_true")
args = parser.parse_args()

mtime = os.path.getmtime(args.filename)
mtime = datetime.datetime.fromtimestamp(mtime).isoformat()
evals = {}
pvlengths = {}
with open(args.filename) as f:
    for line in f:
        line = line.strip()
        if line:
            if line.startswith("#"):  # ignore comments
                continue
            _, _, cdb = line.partition(" cdb eval: ")
            cdb, _, pv = cdb.partition("; PV: ")
            if cdb.lstrip("-").isnumeric():
                e = int(cdb)
            elif cdb.startswith("M"):
                e = 30000 - int(cdb[1:])
            elif cdb.startswith("-M"):
                e = -30000 + int(cdb[2:])
            evals[e] = evals.get(e, 0) + 1
            l = len(pv.split())
            pvlengths[l] = pvlengths.get(l, 0) + 1


def abssort_str(d):
    # sort dictionary items by abs of key, with positive entries before negative ones
    l = []
    for key, value in sorted(d.items(), key=lambda t: abs(t[0]) + 0.5 * (t[0] < 0)):
        l.append(f"{key}: {value}")
    return "{" + ", ".join(l) + "}"


print(f"{mtime},{abssort_str(evals)},{abssort_str(pvlengths)}")
