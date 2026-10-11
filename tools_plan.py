"""Remove built topics from the course plan: python tools_plan.py "Title one" "Title two" """
import re, sys
s = open('src/syllabus.py', encoding='utf-8').read()
for title in sys.argv[1:]:
    s, k = re.subn(r'\("[IVX]+\.[A-Z]", "[^"]+", "' + re.escape(title) + r'"\),\s*', '', s)
    print(("removed " if k == 1 else "NOT FOUND ") + title)
s = s.replace('("III.D", "9, 14", "MLC effects in IMRT")', '("III.D", "14", "MLC effects in IMRT")')
open('src/syllabus.py', 'w', encoding='utf-8').write(s)
