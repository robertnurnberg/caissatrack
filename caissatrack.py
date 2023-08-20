import argparse, os, datetime, chess
from multiprocessing import Pool


def abssort_str(d):
    # sort dictionary items by abs(key), with positive entries before negative ones
    l = []
    for key, value in sorted(d.items(), key=lambda t: abs(t[0]) + 0.5 * (t[0] < 0)):
        l.append(f"{key}: {value}")
    return "{" + "; ".join(l) + "}"


def pv_ends_in_draw(fen, pv):
    # detect if the final position is a stalemate, draw by 50mr, or a 2-fold
    board = chess.Board(fen)
    for move in pv:
        board.push_uci(move)
    return board.is_stalemate() or board.can_claim_draw() or board.is_repetition(2)


def process_line(line):
    line = line.strip()
    if not line or line.startswith("#"):  # skip empty lines and comments
        return None, None

    _, _, cdb = line.partition(" cdb eval: ")
    cdb, _, pv = cdb.partition("; PV: ")
    if cdb.lstrip("-").isnumeric():
        e = int(cdb)
    elif cdb.startswith("M"):
        e = 30000 - int(cdb[1:])
    elif cdb.startswith("-M"):
        e = -30000 + int(cdb[2:])
    fen, _, _ = line.partition(";")
    pv = pv.split()
    l = -len(pv) if pv_ends_in_draw(fen, pv) else len(pv)
    return e, l


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
parser.add_argument(
    "--time",
    help="time to be used for .csv entry (use .epd time stamp if None)",
)
args = parser.parse_args()
mtime = args.time
if mtime is None:
    mtime = os.path.getmtime(args.filename)
    mtime = datetime.datetime.fromtimestamp(mtime).isoformat(timespec="seconds")

lines = []
with open(args.filename) as f:
    lines = f.readlines()

with Pool(processes=os.cpu_count()) as pool:
    results = pool.map(process_line, lines)

evals = {}
pvlengths = {}
for e, l in results:
    if e is not None:
        evals[e] = evals.get(e, 0) + 1
        pvlengths[l] = pvlengths.get(l, 0) + 1

print(f"{mtime},{abssort_str(evals)},{abssort_str(pvlengths)}")
