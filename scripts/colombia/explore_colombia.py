from pathlib import Path

base = Path("data/colombia")

for m in base.iterdir():

    if not m.is_dir():
        continue

    print("\n======================")
    print("MES:", m.name)
    print("======================")

    for p in m.iterdir():

        print("  ", p.name)

        if p.is_dir():

            for q in p.iterdir():
                print("     ", q.name)