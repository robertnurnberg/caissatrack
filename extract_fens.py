import argparse


def pv_ends_in_twofold(fen, pv):
    import chess

    board = chess.Board(fen)
    for move in pv:
        board.push_uci(move)
    return board.is_repetition(2)


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
    "--ignore2folds",
    action="store_true",
    help="Ignore FENs whose cdb PV ends in a twofold repetition.",
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
    if args.ignore2folds:
        raise Exception("Option --ignore2folds not supported with eval range.")
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
            epd, _, pv = line.partition("; PV: ")
            pv, _, _ = pv.partition(";")
            pv = pv.split()
            if shortest:
                lines.append((epd, pv))
            else:
                if cdb.lstrip("-").isnumeric():
                    e = int(cdb)
                elif cdb.startswith("M"):
                    e = 30000 - int(cdb[1:])
                elif cdb.startswith("-M"):
                    e = -30000 + int(cdb[2:])
                if abs(e) >= evalMin and abs(e) <= evalMax:
                    print(f"{epd}; PV length: {len(pv)}")

if shortest:
    lines.sort(key=lambda t: len(t[1]))
    count = 0
    for epd, pv in lines:
        fen, _, _ = epd.partition(";")
        if not args.ignore2folds or not pv_ends_in_twofold(fen, pv):
            print(f"{epd}; PV length: {len(pv)}")
            count += 1
        if count == shortest:
            break
