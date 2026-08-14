"""No-guess solver: verify a board is solvable by pure constraint propagation.

借鉴扫雷求解器的约束传播思想（如 mrgriscom/minesweepr），用两个基本规则
反复推演，判断从首次点击出发能否不靠猜测扫完全局：

规则 1（确定安全）：某数字格周围已标记雷数 == 该数字，则周围所有未翻开格都是安全的。
规则 2（确定是雷）：某数字格周围未标记未翻开格数 == 剩余雷数，则这些格全是雷。

当一个格子被翻开或标记时，会把它周围已翻开的数字格重新加入待处理集合，
保证邻居状态变化后能触发新的推理。
"""
from __future__ import annotations


def _neighbors(rows: int, cols: int, r: int, c: int):
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if not dr and not dc:
                continue
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                yield nr, nc


def is_no_guess(rows: int, cols: int, board, mine_positions, start_r: int, start_c: int) -> bool:
    """Return True if constraint propagation alone clears every safe cell."""
    revealed = [[False] * cols for _ in range(rows)]
    flagged = [[False] * cols for _ in range(rows)]
    pending: set[tuple[int, int]] = set()

    def touch(r: int, c: int) -> None:
        # 翻开/标记 (r,c) 后，它周围已翻开的数字格需要重新推理
        for nr, nc in _neighbors(rows, cols, r, c):
            if revealed[nr][nc] and board[nr][nc] > 0:
                pending.add((nr, nc))

    def reveal_cell(r: int, c: int) -> None:
        if revealed[r][c] or flagged[r][c] or board[r][c] == -1:
            return
        revealed[r][c] = True
        if board[r][c] == 0:
            stack = [(r, c)]
            while stack:
                cr, cc = stack.pop()
                for nr, nc in _neighbors(rows, cols, cr, cc):
                    if not revealed[nr][nc] and not flagged[nr][nc] and board[nr][nc] != -1:
                        revealed[nr][nc] = True
                        if board[nr][nc] == 0:
                            stack.append((nr, nc))
                        else:
                            pending.add((nr, nc))
        else:
            pending.add((r, c))
        touch(r, c)

    reveal_cell(start_r, start_c)

    while pending:
        r, c = pending.pop()
        if not revealed[r][c] or board[r][c] <= 0:
            continue
        nbrs = list(_neighbors(rows, cols, r, c))
        flagged_n = sum(1 for nr, nc in nbrs if flagged[nr][nc])
        unknown = [(nr, nc) for nr, nc in nbrs if not revealed[nr][nc] and not flagged[nr][nc]]
        remaining = board[r][c] - flagged_n
        if remaining == 0:
            for nr, nc in unknown:
                reveal_cell(nr, nc)
        elif remaining > 0 and len(unknown) == remaining:
            for nr, nc in unknown:
                flagged[nr][nc] = True
                touch(nr, nc)

    for r in range(rows):
        for c in range(cols):
            if (r, c) not in mine_positions and not revealed[r][c]:
                return False
    return True
