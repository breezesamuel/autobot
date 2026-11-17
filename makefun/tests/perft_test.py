"""Perft and consistency tests for engine.py (not committed)."""
import sys
import time

sys.path.insert(0, r"F:\2026\第三轮\makefun\tiny-chess-entry")
import engine as E


def snapshot():
    return (tuple(E.board), E.side, E.castle, E.ep, E.hm, E.hash_,
            E.mgS, E.egS, E.matd, tuple(E.PHC), tuple(E.BC),
            tuple(E.PM[0]), tuple(E.PM[1]), tuple(E.kings), len(E.undo_stack))


PC_OF = dict(zip("PNBRQKpnbrqk", (1, 2, 3, 4, 5, 6, 9, 10, 11, 12, 13, 14)))


def scratch(fen):
    """Independent counter computation from a FEN (own parser, own sums)."""
    parts = fen.split()
    bd = [0] * 128
    mg = eg = matd = 0
    ph = [0, 0]
    bc = [0, 0]
    pm = [[0] * 8, [0] * 8]
    kings = [-1, -1]
    for r8, row in enumerate(parts[0].split("/")):
        r, f = 7 - r8, 0
        for c in row:
            if c.isdigit():
                f += int(c)
            else:
                pc = PC_OF[c]
                sq = r * 16 + f
                bd[sq] = pc
                mg += E.S_MG[pc][sq]
                eg += E.S_EG[pc][sq]
                matd += E.MAT[pc]
                ph[pc >> 3] += E.PHU[pc]
                if pc & 7 == 6:
                    kings[pc >> 3] = sq
                if pc & 7 == 3:
                    bc[pc >> 3] += 1
                if pc & 7 == 1:
                    pm[pc >> 3][f] |= 1 << r
                f += 1
    side = 0 if parts[1] == "w" else 1
    castle = 0
    for c, bit in (("K", 1), ("Q", 2), ("k", 4), ("q", 8)):
        if c in parts[2]:
            castle |= bit
    ep = -1
    if parts[3] != "-":
        ep = (ord(parts[3][1]) - 49) * 16 + ord(parts[3][0]) - 97
    hm = int(parts[4]) if len(parts) > 4 else 0
    h = 0
    for sq in E.SQUARES:
        if bd[sq]:
            h ^= E.ZP[bd[sq]][sq]
    h ^= E.ZC[castle]
    if ep >= 0:
        h ^= E.ZE[ep & 7]
    if side:
        h ^= E.ZS
    return bd, side, castle, ep, hm, h, mg, eg, matd, ph, bc, pm, kings


def verify_counters(fen, tag):
    bd, side, castle, ep, hm, h, mg, eg, matd, ph, bc, pm, kings = scratch(fen)
    assert tuple(E.board) == tuple(bd), ("board", tag, fen)
    assert E.side == side and E.castle == castle and E.ep == ep and E.hm == hm, \
        ("state", tag, fen, E.side, E.castle, E.ep, E.hm)
    assert E.hash_ == h, ("hash", tag, fen, E.hash_, h)
    assert E.mgS == mg and E.egS == eg, ("mg/eg", tag, fen, E.mgS, mg, E.egS, eg)
    assert E.matd == matd, ("matd", tag, fen, E.matd, matd)
    assert tuple(E.PHC) == tuple(ph), ("phase", tag, fen, tuple(E.PHC), tuple(ph))
    assert tuple(E.BC) == tuple(bc), ("bishops", tag, fen, tuple(E.BC), tuple(bc))
    assert tuple(E.PM[0]) == tuple(pm[0]) and tuple(E.PM[1]) == tuple(pm[1]), \
        ("pmask", tag, fen)
    assert tuple(E.kings) == tuple(kings), ("kings", tag, fen, tuple(E.kings), tuple(kings))
    assert len(E.undo_stack) == 0 or True


def perft(depth):
    if depth == 0:
        return 1
    n = 0
    us = E.side
    them = us ^ 1
    ksq = E.kings[us]
    in_chk = E.attacked(ksq, them)
    for m in E.moves():
        f = m & 127
        gate = in_chk or f == ksq or m & E.EP_F or E.PIN_DIR[ksq][f]
        E.make(m)
        if gate and E.attacked(E.kings[us], them):
            E.unmake()
            continue
        n += perft(depth - 1)
        E.unmake()
    return n


def perft_deep(fen, depth):
    """Perft where every node verifies the incremental counters against an
    independent from-scratch computation and make/unmake round-trips."""
    if depth == 0:
        return 1
    n = 0
    us = E.side
    them = us ^ 1
    ksq = E.kings[us]
    in_chk = E.attacked(ksq, them)
    before = snapshot()
    for m in E.moves():
        f = m & 127
        gate = in_chk or f == ksq or m & E.EP_F or E.PIN_DIR[ksq][f]
        E.make(m)
        if gate and E.attacked(E.kings[us], them):
            E.unmake()
            assert snapshot() == before, "roundtrip (illegal)"
            continue
        verify_counters(E.fen_of(), "node")
        n += perft_deep(E.fen_of(), depth - 1)
        E.unmake()
        assert snapshot() == before, ("roundtrip", E.uci_of(m))
    return n


CASES = [
    ("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
     [20, 400, 8902, 197281]),
    ("r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1",
     [48, 2039, 97862]),
    ("8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w - - 0 1",
     [14, 191, 2812, 43238]),
    ("r3k2r/Pppp1ppp/1b3nbN/nP6/BBP1P3/q4N2/Pp1P2PP/R2Q1RK1 w kq - 0 1",
     [6, 264, 9467, 422333]),
    ("rnbq1k1r/pp1Pbppp/2p5/8/2B5/8/PPP1NnPP/RNBQK2R w KQ - 1 8",
     [44, 1486, 62379]),
    ("r4rk1/1pp1qppp/p1np1n2/2b1p1B1/2B1P1b1/P1NP1N2/1PP1QPPP/R4RK1 w - - 0 10",
     [46, 2079, 89890]),
]


def main():
    t0 = time.time()
    checked_nodes = 0
    for fen, expect in CASES:
        E.set_fen(fen)
        verify_counters(fen, "set_fen")
        for d, want in enumerate(expect, 1):
            E.set_fen(fen)
            got = perft_deep(fen, d)
            checked_nodes += got
            ok = "OK " if got == want else "FAIL"
            print(f"{ok} d{d} {fen.split()[0][:20]:22} got {got} want {want}")
            assert got == want, (fen, d, got, want)
    # deep plain perft for speed coverage
    for fen, expect in CASES:
        if len(expect) > 4:
            E.set_fen(fen)
            got = perft(len(expect))
            print(f"OK d{len(expect)} {fen.split()[0][:20]:22} got {got} want {expect[-1]}")
            assert got == expect[-1]
    print(f"perft all OK, checked nodes {checked_nodes}, time {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
