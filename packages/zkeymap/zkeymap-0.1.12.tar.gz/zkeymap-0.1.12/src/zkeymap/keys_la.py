# Copyright (c) 2025 Frank David Martínez Muñoz <mnesarco>
# SPDX-License-Identifier: MIT

# ruff: noqa: ERA001

"""
Spanish Latin American key aliases.
"""

__all__ = ()

# fmt: off

from zkeymap.lang import alias, label

alias / "|"             / "GRAVE"
alias / "'"             / "MINUS"
alias / "¿"             / "EQL"
alias / ("acut", "´")   / "LBKT"  # noqa: RUF001
alias / "+"             / "RBKT"
alias / "ñ"             / "SEMI"
alias / "{"             / "SQT"
alias / "}"             / "NUHS"
alias / "<"             / "NUBS"
alias / ("comm", ",")   / "COMMA"
alias / ("dot", ".")    /  "DOT"
alias / "-"             / "SLASH"
alias / "º"             / "LS(GRAVE)"
alias / "!"             / "LS(N1)"
alias / "\""            / "LS(N2)"  # noqa: Q003
alias / "#"             / "LS(N3)"
alias / "$"             / "LS(N4)"
alias / "%"             / "LS(N5)"
alias / "&"             / "LS(N6)"
alias / "/"             / "LS(N7)"
alias / "("             / "LS(N8)"
alias / ")"             / "LS(N9)"
alias / "="             / "LS(N0)"
alias / "?"             / "LS(MINUS)"
alias / "¿"             / "LS(EQL)"
alias / "diae"          / "LS(LBRC)" / label("¨")
alias / "*"             / "LS(RBRC)"
alias / "["             / "LS(SQT)"
alias / "\\]"           / "LS(NUHS)" / label("]")
alias / ">"             / "LS(NUBS)"
alias / ";"             / "LS(COMMA)"
alias / ":"             / "LS(DOT)"
alias / "_"             / "LS(SLASH)"
alias / "¬"             / "RA(GRAVE)"
alias / "·"             / "RA(N3)"
alias / "½"             / "RA(N5)"
alias / "\\"            / "RA(MINUS)"
alias / "¸"             / "RA(N0)"  # noqa: RUF001
alias / "@"             / "RA(Q)"
alias / "ł"             / "RA(W)"
alias / "€"             / "RA(E)"
alias / "¶"             / "RA(R)"
alias / "ŧ"             / "RA(T)"
# alias / "←"             / "RA(Y)"
# alias / "↓"             / "RA(U)"
# alias / "→"             / "RA(I)"
alias / "ø"             / "RA(O)"
alias / "þ"             / "RA(P)"
alias / "¨"             / "RA(LBRC)"
alias / "~"             / "RA(RBKT)"
alias / "æ"             / "RA(A)"
alias / "ß"             / "RA(S)"
alias / "ð"             / "RA(D)"
alias / "đ"             / "RA(F)"
alias / "ŋ"             / "RA(G)"
alias / "ħ"             / "RA(H)"
alias / "ˀ"             / "RA(J)"
alias / "ĸ"             / "RA(k)"
alias / "ł"             / "RA(L)"
alias / ("`", "grv")    / "RA(NUHS)" / label("`")
alias / "«"             / "RA(Z)"
alias / "»"             / "RA(X)"
alias / "¢"             / "RA(C)"
alias / "“"             / "RA(V)"
alias / "”"             / "RA(B)"
alias / "µ"             / "RA(M)"
alias / "─"             / "RA(COMMA)"
alias / "^"             / "RA(SQT)"
