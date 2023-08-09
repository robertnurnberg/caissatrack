import argparse

parser = argparse.ArgumentParser(
    description="Extract FENs with shortest cdb PV from e.g. caissa_sorted_100000_cdbpv.epd",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)
parser.add_argument(
    "filename",
    nargs="?",
    help="file FENs and their cdb PVs",
    default="caissa_sorted_100000_cdbpv.epd",
)
parser.add_argument(
    "-n",
    help="number of FENs to extract",
    type=int,
    default=100,
)
args = parser.parse_args()
lines = []
with open(args.filename) as f:
    for line in f:
        line = line.strip()
        if line:
            if line.startswith("#"):  # ignore comments
                continue
            fen, _, pv = line.partition("; PV: ")
            l = len(pv.split())
            lines.append((fen, l))
lines.sort(key=lambda t: t[1])
for fen, l in lines[: args.n]:
    print(f"{fen}; PV length: {l}")
