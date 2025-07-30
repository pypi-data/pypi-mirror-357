# PynDD (Python Dynamic DSL)

A lightweight Python library for dynamic data structure parsing and manipulation using a custom Domain Specific Language (DSL).

## Installation

```bash
pip install pyndd
```

## Quick Start

```python
from pyndd.parser import parse, translate

# Basic usage
data = {'users': [{'name': 'Alice', 'age': 30}, {'name': 'Bob', 'age': 25}]}
names = parse('data:users:[#name]', data=data)
print(names)  # ['Alice', 'Bob']
```

## DSL Syntax Guide

### Basic Structure

The DSL uses a colon-separated syntax: `variable:accessor1:accessor2:...`

### Accessors

#### 1. Dictionary/Object Access (`#key`)

```python
data = {'user': {'name': 'Alice', 'age': 30}}
name = parse('data:#user:#name', data=data)
print(name)  # 'Alice'
```

#### 2. List/Array Access by Index (`number`)

```python
data = {'items': ['a', 'b', 'c', 'd']}
item = parse('data:#items:1', data=data)
print(item)  # 'b'
```

#### 3. Slice Access (`[start..end]`)

```python
data = {'items': ['a', 'b', 'c', 'd', 'e']}
subset = parse('data:#items:[1..4]', data=data)
print(subset)  # ['b', 'c', 'd']

# Open-ended slices
beginning = parse('data:#items:[..2]', data=data)  # ['a', 'b']
ending = parse('data:#items:[2..]', data=data)     # ['c', 'd', 'e']
all_items = parse('data:#items:[..]', data=data)   # ['a', 'b', 'c', 'd', 'e']
```

#### 4. Map Operations (`[#key]`)

Extract specific fields from each item in a list:

```python
data = {'users': [
    {'name': 'Alice', 'age': 30},
    {'name': 'Bob', 'age': 25}
]}
names = parse('data:#users:[#name]', data=data)
print(names)  # ['Alice', 'Bob']

ages = parse('data:#users:[#age]', data=data)
print(ages)  # [30, 25]
```

#### 5. Pattern Matching (`*pattern*`)

Match keys using wildcards:

```python
data = {
    'user_alice': {'score': 100},
    'user_bob': {'score': 85},
    'admin_charlie': {'score': 95}
}

# Get all user_* entries
users = parse('data:user_*', data=data)
print(users)  # {'user_alice': {'score': 100}, 'user_bob': {'score': 85}}

# Get scores from user_* entries
user_scores = parse('data:user_*:[#score]', data=data)
print(user_scores)  # [100, 85]
```

#### 6. Variable-based Key Access

Use variables to specify keys dynamically:

```python
data = {'items': ['x', 'y', 'z']}
indices = [0, 2]
selected = parse('data:#items:indices', data=data, indices=indices)
print(selected)  # ['x', 'z']
```

### Complex Examples

#### Chaining Operations

```python
data = {
    'departments': [
        {
            'name': 'Engineering',
            'employees': [
                {'name': 'Alice', 'skills': ['Python', 'JavaScript']},
                {'name': 'Bob', 'skills': ['Java', 'C++']}
            ]
        },
        {
            'name': 'Marketing',
            'employees': [
                {'name': 'Charlie', 'skills': ['SEO', 'Content']}
            ]
        }
    ]
}

# Get all employee names
all_names = parse('data:#departments:[#employees]:[#name]', data=data)
print(all_names)  # [['Alice', 'Bob'], ['Charlie']]

# Get skills of first employee in each department
first_skills = parse('data:#departments:[#employees]:0:[#skills]', data=data)
print(first_skills)  # [['Python', 'JavaScript'], ['SEO', 'Content']]
```

#### Nested Slicing

```python
data = {
    'matrix': [
        [1, 2, 3, 4],
        [5, 6, 7, 8],
        [9, 10, 11, 12]
    ]
}

# Get middle 2x2 submatrix
submatrix = parse('data:#matrix:[1..3]:[1..3]', data=data)
print(submatrix)  # [[6, 7], [10, 11]]
```

## Data Modification with `translate()`

The `translate()` function allows you to modify data using assignment operations.

### Basic Assignment

```python
data = {'user': {'name': 'Alice'}}
translate('data:#user:#age < 30', data=data)
print(data)  # {'user': {'name': 'Alice', 'age': 30}}
```

### Bulk Assignment

```python
data = {'users': [{'name': 'Alice'}, {'name': 'Bob'}]}
translate('data:#users:[#age] < 25', data=data)
print(data)  # {'users': [{'name': 'Alice', 'age': 25}, {'name': 'Bob', 'age': 25}]}
```

### Copy Data Between Structures

```python
source = {'items': [1, 2, 3]}
target = {}
translate('target:#copied < source:#items', source=source, target=target)
print(target)  # {'copied': [1, 2, 3]}
```

## Advanced Features

### Pattern-based Operations

```python
config = {
    'db_host': 'localhost',
    'db_port': 5432,
    'db_name': 'myapp',
    'cache_host': 'redis-server',
    'cache_port': 6379
}

# Get all database-related configs
db_config = parse('config:db_*', config=config)
print(db_config)  # {'db_host': 'localhost', 'db_port': 5432, 'db_name': 'myapp'}
```

### Identity Operation (`[[unit_tests](../Doctor/scripts/unit_tests)-]`)

The identity operation `[-]` can be used to pass through values unchanged:

```python
data = {'items': [1, 2, 3]}
same = parse('data:#items:[-]', data=data)
print(same)  # [1, 2, 3]
```

## Error Handling

The parser will raise `ValueError` for malformed expressions:

```python
try:
    parse('invalid syntax here', data={})
except ValueError as e:
    print(f"Parse error: {e}")
```

## Performance Notes

- The DSL parser is lightweight and suitable for runtime data manipulation
- Complex nested operations are supported but consider performance for deeply nested structures
- Pattern matching uses Python's `fnmatch` module internally

## License

MIT License