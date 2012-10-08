d = {'a': 1, 'b': 0, 'c': None, 'd': '', 'e': [], 'f': False, 'g': True}

for k, v in d.items():
  print k, v,
  if v:
    print 'true',
  else:
    print 'false',
  print d.get(k) or 'ASS'

print [None or ''] or 'Q'