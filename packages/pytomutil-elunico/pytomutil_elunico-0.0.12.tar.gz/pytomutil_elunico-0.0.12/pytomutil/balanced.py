class UnbalancedBracketError(ValueError):
    ...


class WrongBracketsError(ValueError):
    ...


def balanced(s):
    tk = []
    obracs = {"(": ")", "{": "}", "[": "]"}
    cbracs = set(obracs.values())
    for c in s:
        if c in obracs:
            tk.append(obracs[c])
        elif c in cbracs:
            if not tk:
                raise UnbalancedBracketError("No open bracket to match " + c)
            if (t := tk.pop()) != c:
                raise WrongBracketsError(f"Wrong close bracket: expected {t}; got {c}")
    if tk:
        raise UnbalancedBracketError(f"Too many open brackets. Expected {tk[-1]}")


balanced("((()()(([[()(([]))]]))))")
