## PynDD(Python Dynamic DSL)
```python
from pyndd.parser import parse, translate


a = {'b': ...}
print(parse('a:#b', a=a) == a['b'])  # True
a = {'b': [ ... ], 'c': [ ... ]}
print(parse('a:#b:[..]', a=a) == a['b'])  # True
print(parse('a:#b:[1..3]', a=a) == a['b'][1:3])  # True
print(parse('a:[#b]', a=a) == [item['b'] for item in a])  # True
print(parse('a:3:[#b]', a=a) == a[3]['b'])  # True
translate('a:#b < 2')
print(a['b'] == 2)  # True
c = {'d': [ ... ]}
translate('a:[#b] < c:[#d]', a=a, c=c)
print(all([item_a['b'] == item_c['d'] for item_a, item_c in zip(a, c)]))  # True
b = [ ... ]
d = {'e': [ ... ]}
translate('a:#b:[#c] < d:[#e]')
all([item_a['b']['c'] == item_d['e'] for item_a, item_d in zip(a, d)])  # True
print(parse('a:b', b=b) == [a[item] for item in b])  # True
translate('a:[#b] < b', a=a, b=b)
print([item['b'] for item in a] == b)  # True
print(parse('a:[2..4]:[1..4]', a=a) == [item[1:4] for item in a[2:4]])  # True
e = {'abc': [ ... ], 'aabdc': [ ... ], 'acb': [ ... ]}
print(parse('e:*ab*c*', e=e) == {key: e[key] for key in ('abc', 'aabdc')})  # True
print(parse('e:*ab*c*:[1..3]', e=e) == {key: e[key][1:3] for key in ('abc', 'aabdc')})  # True
f = [ ... ]
translate('e:*ab*c* < f', e=e)
print(f == {key: e[key] for key in ('abc', 'aabdc')})  # True
translate('e:*ab*c*:[1..3] < f', e=e)
print(f == {key: e[key][1:3] for key in ('abc', 'aabdc')})  # True
```