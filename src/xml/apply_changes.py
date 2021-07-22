data = [s.split(":") for s in open("changes.txt").readlines()]

changes = {}

for l in data:
    if l[0] not in changes:
        changes[l[0]] = {}
    changes[l[0]][int(l[1])] = ":".join(l[2:])

for f, c in changes.items():
    with open(f) as out:
        src = list(out.readlines())
    with open(f, "w") as out:
        line_no = 1
        for line in src:
            if line_no in c:
                out.write(c[line_no])
            else:
                out.write(line)
            line_no += 1
