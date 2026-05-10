# Chess preset: maps ArUco marker IDs to chess pieces (piece + color)
# Marker IDs 1–12, two colors × six pieces.
# OSC prefix:  /chess/<piece>/<color>   e.g. /chess/pawn/white

# ── Piece constants ──────────────────────────────────────────────────────────
PAWN_W   = 1
PAWN_B   = 2
ROOK_W   = 3
ROOK_B   = 4
KNIGHT_W = 5
KNIGHT_B = 6
BISHOP_W = 7
BISHOP_B = 8
QUEEN_W  = 9
QUEEN_B  = 10
KING_W   = 11
KING_B   = 12

# ── Marker → piece name (human-readable) ─────────────────────────────────────
MARKER_LABELS = {
    PAWN_W:   "Pawn White",
    PAWN_B:   "Pawn Black",
    ROOK_W:   "Rook White",
    ROOK_B:   "Rook Black",
    KNIGHT_W: "Knight White",
    KNIGHT_B: "Knight Black",
    BISHOP_W: "Bishop White",
    BISHOP_B: "Bishop Black",
    QUEEN_W:  "Queen White",
    QUEEN_B:  "Queen Black",
    KING_W:   "King White",
    KING_B:   "King Black",
}

# ── Marker → OSC address prefix ──────────────────────────────────────────────
# Full message will be: <OSC_PREFIX[id]>  [x, y, angle, size, health]
OSC_PREFIX = {
    PAWN_W:   "/chess/pawn/white",
    PAWN_B:   "/chess/pawn/black",
    ROOK_W:   "/chess/rook/white",
    ROOK_B:   "/chess/rook/black",
    KNIGHT_W: "/chess/knight/white",
    KNIGHT_B: "/chess/knight/black",
    BISHOP_W: "/chess/bishop/white",
    BISHOP_B: "/chess/bishop/black",
    QUEEN_W:  "/chess/queen/white",
    QUEEN_B:  "/chess/queen/black",
    KING_W:   "/chess/king/white",
    KING_B:   "/chess/king/black",
}

# All valid marker IDs for this preset
MARKER_IDS = set(OSC_PREFIX.keys())
