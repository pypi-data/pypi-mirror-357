"""
Syllabification algorithm based on the alphabet of the Epa language.
"""

V_OPEN_BASE: set = {"a", "e", "o"}
V_OPEN_ACCE: set = {"á", "é", "ó"}
V_OPEN_CIRC: set = {"â", "ê", "ô"}

V_OPEN_FULL: set = V_OPEN_BASE | V_OPEN_ACCE | V_OPEN_CIRC

V_CLOS_BASE: set = {"i", "u"}
V_CLOS_ACCE: set = {"í", "ú"}
V_CLOS_CIRC: set = {"î", "û"}

V_CLOS_FULL: set = V_CLOS_BASE | V_CLOS_ACCE | V_CLOS_CIRC

V_FULL: set = V_OPEN_FULL | V_CLOS_FULL


C_PLOS_ALVE: set = {"d", "t"}

C_PLOS_OTHE: set = {"p", "k", "q", "c", "b", "g"}
C_FRIC_LADE: set = {"f"}
C_OBST_LIQU: set = C_PLOS_OTHE | C_FRIC_LADE

C_LIQU_LATE: set = {"l"}
C_LIQU_FLAP: set = {"r"}
C_LIQU: set = C_LIQU_LATE | C_LIQU_FLAP

C_CODA: set = {"n", "h"}

C_FULL: set = C_PLOS_ALVE | C_OBST_LIQU | C_LIQU | C_CODA | {"ç", "x", "y", "m", "ñ", "s", "z"}


FULL_SET: set = V_FULL | C_FULL


def unpack_list(l: list[str|list[str]]) -> list[str]:
    """
    From a list[str|list[str]], turns the inner list[str] into a merged str item.
    Example: unpack_list(["a", ["b", "c"]]) -> ["a", "bc"]
    """
    for i in range(len(l)):
        if type(l[i]) == list:
            l[i] = "".join(j for j in l[i])
    return l


def rule(w: list[str], lower, upper, range) -> list[str]:
    """
    Creates a merging rule for strings on a list.
    param 1: a list of strings
    param 2: lower limit, aka what the last character of the previous string must be.
    param 3: upper limit, aka what the first character of the following string must be.
    param 4: range "inclusive" to merge 3 items or "exclusive" to merge 2 items.
    Example: rule(["q", "u", "e"], "q", "u", "inclusive") -> ["que"]
    """
    r: int = 3 if range == "inclusive" else 2
    l: list = []
    i: int = 0
    while i < len(w):
        if w[i][-1] in lower and i + 1 < len(w) and w[i+1][0] in upper:
            l.append(w[i:i+r])
            i += r
        else:
            l.append(w[i])
            i += 1
    return unpack_list(l)


def syllabify(x: str) -> list:

    """
    Given a string in EPA, splits by syllables.
    Example: syllabify("andalûh") -> ['an', 'da', 'lûh']
    """

    x: str = " " if len(x) == 0 else x

    x: str = x.lower()
    x: str = x.strip()
    x: str = x.replace("-", "")
    x: list[str] = list(x)

    x: list[str] = rule(x, "q", "u", "inclusive")                  # qu
    x: list[str] = rule(x, "r", "r", "inclusive")                  # rr
    x: list[str] = rule(x, C_OBST_LIQU, C_LIQU, "inclusive")       # /p, k, b, g, f/ + /r, l/
    x: list[str] = rule(x, C_PLOS_ALVE, C_LIQU_FLAP, "inclusive")  # /d, t/ + /r/
    x: list[str] = rule(x, V_CLOS_FULL, V_OPEN_FULL, "exclusive")  # /i, u/ + /a, e, o/
    x: list[str] = rule(x, C_FULL, V_FULL, "exclusive")            # CV

    # handles n and h in coda position
    l: list = []
    i: int = 0
    while i < len(x):
        if x[i][-1] in V_FULL and i + 2 < len(x) and x[i+1] in C_CODA and x[i+2][0] not in V_FULL:
            l.append(x[i:i+2])
            i += 2
        else:
            l.append(x[i])
            i += 1
    l: list[str] = unpack_list(l)

    # handles n and h in end of word
    if len(l) >= 2 and l[-1] in C_CODA:
        l[-2] = l[-2] + l[-1]
        l.pop()

    # handles coda r and m
    for i in range(len(l)):
        if len(l[i]) == 1 and i + 1 < len(l) and i != 0:
            if l[i] in "r" or l[i] in "m":
                if l[i+1][0] in C_FULL and l[i-1][-1] in V_FULL:
                    l[i-1] = l[i-1] + l[i]
                    l[i] = ""
    l: list[str] = [i for i in l if i != ""]

    # handles germination for coda syllable
    for i in range(len(l)):
        if len(l[i]) == 1 and i + 1 < len(l) and i != 0:
            if l[i] == l[i+1][0]:
                l[i-1] = l[i-1] + l[i]
                l[i] = ""
            elif l[i] == l[i-1][-1]:
                l[i+1] = l[i] + l[i+1]
                l[i] = ""
    l: list[str] = [i for i in l if i != ""]


    return l
