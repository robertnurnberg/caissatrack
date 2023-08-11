import argparse

epdFile = "caissa_sorted_100000_cdbpv.epd"
parser = argparse.ArgumentParser(
    description="Extract FENs based on cdb eval or PV length from e.g. caissa_sorted_100000_cdbpv.epd",
)
parser.add_argument(
    "filename",
    nargs="?",
    help=f"file FENs and their cdb PVs (default: {epdFile})",
    default=epdFile,
)
parser.add_argument(
    "--shortest",
    help="Extract the given number of FENs with shortest cdb PV.",
    type=int,
)
parser.add_argument(
    "--evalMin",
    help="Lower bound for absolute cdb eval of FENs to extract.",
    type=int,
)
parser.add_argument(
    "--evalMax",
    help="Upper bound for absolute cdb eval of FENs to extract.",
    type=int,
)
args = parser.parse_args()
if args.shortest is None and args.evalMin is None and args.evalMax is None:
    raise Exception("Must specify an option.")
if args.shortest is None:
    if args.evalMin is None or args.evalMax is None:
        raise Exception("Must specify a full eval range.")
    evalMin, evalMax = abs(args.evalMin), abs(args.evalMax)
    if evalMin > evalMax:
        raise Exception(f"Empty range [{evalMin},{evalMax}].")
else:
    if not (args.evalMin is None and args.evalMax is None):
        raise Exception("Cannot specify both --shortest and eval range.")
shortest = 0 if args.shortest is None else max(0, args.shortest)
lines = []
with open(args.filename) as f:
    for line in f:
        line = line.strip()
        if line:
            if line.startswith("#"):  # ignore comments
                continue
            _, _, cdb = line.partition("; cdb eval: ")
            cdb, _, _ = cdb.partition(";")
            fen, _, pv = line.partition("; PV: ")
            l = len(pv.split())
            if shortest:
                lines.append((fen, l))
            else:
                if cdb.lstrip("-").isnumeric():
                    e = int(cdb)
                elif cdb.startswith("M"):
                    e = 30000 - int(cdb[1:])
                elif cdb.startswith("-M"):
                    e = -30000 + int(cdb[2:])
                if abs(e) >= evalMin and abs(e) <= evalMax:
                    print(f"{fen}; PV length: {l}")
if shortest:
    lines.sort(key=lambda t: t[1])
    for fen, l in lines[:shortest]:
        print(f"{fen}; PV length: {l}")
