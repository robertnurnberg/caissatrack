import argparse, os, datetime, chess
from multiprocessing import Pool


def abssort_str(d):
    # sort dictionary items by abs(key), with positive entries before negative ones
    l = []
    for key, value in sorted(d.items(), key=lambda t: abs(t[0]) + 0.5 * (t[0] < 0)):
        l.append(f"{key}: {value}")
    return "{" + "; ".join(l) + "}"


def encode_depth(fen, pv, e):
    # use negative values to encode terminal PVs (with known result)
    d = len(pv)
    board = chess.Board(fen, chess960=True)
    for move in pv:
        board.push_uci(move)
    if board.is_fifty_moves():
        return -10000 - d  # 50mr
    if board.is_stalemate():
        return -20000 - d  # stalemate
    if board.is_checkmate():
        return -30000 - d  # checkmate
    pc = 64 - str(board).count(".")
    if pc <= 7:
        if e is None or (abs(e) > 50 and abs(e) < 20000):
            return -60000 - d  # TB unknown
        if abs(e) >= 20000:
            return -50000 - d  # TB wins
        return -40000 - d  # TB draws
    if board.is_repetition(2):  # slowest check, so test last
        return -d  # 2fold (stands for 3fold repetition)
    return d


def process_line(line):
    line = line.strip()
    if not line or line.startswith("#"):  # skip empty lines and comments
        return None, None

    _, _, cdb = line.partition(" cdb eval: ")
    cdb, _, pv = cdb.partition("; PV: ")
    pv, _, _ = pv.partition(";")
    if cdb.lstrip("-").isnumeric():
        e = int(cdb)
    elif cdb.startswith("M"):
        e = 30000 - int(cdb[1:])
    elif cdb.startswith("-M"):
        e = -30000 + int(cdb[2:])
    else:
        e = None
    fen, _, _ = line.partition(";")
    d = encode_depth(fen, pv.split(), e)
    return e, d


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
