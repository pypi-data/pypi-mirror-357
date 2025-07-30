import ast
import fnmatch
import re
from typing import Any, List, Tuple, Union


def _resolve_get(obj: Any, key: str) -> Any:
    return obj[key] if isinstance(obj, dict) else getattr(obj, key)


def parse(expr: str, **kwargs) -> Any:
    expr = expr.replace(" ", "")
    tokens: List[Tuple[str, Union[str, Tuple[int, int], int, None]]] = []

    index = 0
    if index < len(expr) and expr[index] == "&":
        index += 1
    start = index
    while index < len(expr) and (expr[index].isalnum() or expr[index] == "_"):
        index += 1
    var_name = expr[start:index]
    tokens.append(("var", var_name))

    while index < len(expr):
        if expr[index] != ":":
            raise ValueError(f"Unexpected char: {expr[index]!r}")
        index += 1

        if expr[index] == "[":
            j = expr.find("]", index)
            if j == -1:
                raise ValueError("']' not found")
            inner = expr[index+1: j]
            index = j+1

            if inner == "-":
                tokens.append(("identity", None))
            elif re.fullmatch(r"(-?\d*)\.\.(-?\d*)", inner):
                s, e = inner.split("..")
                tokens.append(("slice", (int(s) if s else None, int(e) if e else None)))
            else:
                if inner.startswith("#"):
                    tokens.append(("map_key", inner[1:]))
                elif any(ch in inner for ch in "*?"):
                    tokens.append(("map_key", inner))
                else:
                    tokens.append(("map_keys_var", inner))
        else:
            start_segment = index
            while index < len(expr) and expr[index] != ":":
                index += 1
            segment = expr[start_segment:index]

            if segment.isdigit() or (segment.startswith("-") and segment[1:].isdigit()):
                tokens.append(("index", int(segment)))
            elif segment.startswith("#"):
                tokens.append(("attr", segment[1:]))
            elif any(ch in segment for ch in "*?"):
                tokens.append(("attr", segment))
            else:
                tokens.append(("map_keys_var", segment))

    value = kwargs[tokens[0][1]]
    first_slice_done = False

    for value_type, data in tokens[1:]:
        if value_type == "identity":
            continue

        if value_type == "slice":
            s, e = data
            if isinstance(value, dict):
                value = {k: v[s:e] for k, v in value.items()}
            elif not first_slice_done:
                value = value[s:e]
                first_slice_done = True
            else:
                value = [elem[s:e] for elem in value]

        elif value_type == "index":
            value = value[data]

        elif value_type in ("attr", "map_key"):
            key = data
            if isinstance(value, dict) and any(ch in key for ch in "*?"):
                value = {k: v for k, v in value.items() if fnmatch.fnmatch(k, key)}
            else:
                if isinstance(value, list):
                    value = [_resolve_get(item, key) for item in value]
                else:
                    value = _resolve_get(value, key)

        elif value_type == "map_keys_var":
            keys = kwargs[data]
            value = [value[k] for k in keys]

        else:
            raise RuntimeError(f"Unknown token type: {value_type}")

    return value


def _needs_parsing(expr: str) -> bool:
    expr = expr.strip()
    return any(ch in expr for ch in ":[") or any(ch in expr for ch in "*?")


def translate(expr: str, **kwargs):
    m = re.search(r"(>|<)", expr)
    if not m:
        raise ValueError("expression must contain < or >")

    op = m.group()
    left_raw, right_raw = (part.strip() for part in expr.split(op, 1))
    dest_raw, src_raw = (right_raw, left_raw) if op == ">" else (left_raw, right_raw)

    if _needs_parsing(src_raw):
        value = parse(src_raw, **kwargs)
    else:
        try:
            value = ast.literal_eval(src_raw)
        except Exception:
            value = kwargs[src_raw]

    if not _needs_parsing(dest_raw):
        kwargs[dest_raw] = value
    else:
        _assign(dest_raw, value, **kwargs)


def _tokenize(expr: str) -> List[Tuple[str, Any]]:
    expr = expr.replace(" ", "")
    tokens: List[Tuple[str, Any]] = []

    idx = 0
    if idx < len(expr) and expr[idx] == "&":
        idx += 1
    start = idx
    while idx < len(expr) and (expr[idx].isalnum() or expr[idx] == "_"):
        idx += 1
    tokens.append(("var", expr[start:idx]))

    while idx < len(expr):
        if expr[idx] != ":":
            raise ValueError(f"Unexpected char: {expr[idx]!r}")
        idx += 1

        if expr[idx] == "[":
            j = expr.find("]", idx)
            if j == -1:
                raise ValueError("']' not found")
            inner = expr[idx+1: j]
            idx = j+1

            if inner == "-":
                tokens.append(("identity", None))
            elif re.fullmatch(r"(-?\d*)\.\.(-?\d*)", inner):
                s, e = inner.split("..")
                tokens.append(("slice", (int(s) if s else None, int(e) if e else None)))
            else:
                if inner.startswith("#"):
                    tokens.append(("map_key", inner[1:]))
                elif any(ch in inner for ch in "*?"):
                    tokens.append(("map_key", inner))
                else:
                    tokens.append(("map_keys_var", inner))
        else:
            seg_start = idx
            while idx < len(expr) and expr[idx] != ":":
                idx += 1
            seg = expr[seg_start:idx]

            if seg.isdigit() or (seg.startswith("-") and seg[1:].isdigit()):
                tokens.append(("index", int(seg)))
            elif seg.startswith("#"):
                tokens.append(("attr", seg[1:]))
            elif any(ch in seg for ch in "*?"):
                tokens.append(("attr", seg))
            else:
                tokens.append(("map_keys_var", seg))

    return tokens


def _assign(path: str, value: Any, **kwargs) -> None:
    tokens = _tokenize(path)
    var_name = tokens[0][1]

    if len(tokens) == 1:
        kwargs[var_name] = value
    else:
        _write(kwargs[var_name], tokens[1:], value, **kwargs)


def _write(obj: Any, tokens: List[Tuple[str, Any]], value: Any, **kwargs) -> None:
    value_type, data = tokens[0]
    rest = tokens[1:]

    def _iter_pairs(src, _value):
        if isinstance(_value, list) and len(_value) == len(src):
            return zip(src, _value)
        return ((item, _value) for item in src)

    if value_type in ("attr", "map_key"):
        key = data

        if isinstance(obj, dict) and any(ch in key for ch in "*?"):
            for mk in [k for k in obj if fnmatch.fnmatch(k, key)]:
                v = value[mk] if isinstance(value, dict) and mk in value else value
                if rest:
                    _write(obj[mk], rest, v, **kwargs)
                else:
                    obj[mk] = v
            return

        if isinstance(obj, list):
            vals = value if isinstance(value, list) and len(value) == len(obj) else [value]*len(obj)
            for sub_obj, v in zip(obj, vals):
                if rest:
                    nxt = sub_obj[key] if isinstance(sub_obj, dict) else getattr(sub_obj, key)
                    _write(nxt, rest, v, **kwargs)
                else:
                    if isinstance(sub_obj, dict):
                        sub_obj[key] = v
                    else:
                        setattr(sub_obj, key, v)
            return

        if not rest:
            if isinstance(obj, dict):
                obj[key] = value
            else:
                setattr(obj, key, value)
        else:
            nxt = obj[key] if isinstance(obj, dict) else getattr(obj, key)
            _write(nxt, rest, value, **kwargs)

    elif value_type == "index":
        idx = data
        if not rest:
            obj[idx] = value
        else:
            _write(obj[idx], rest, value, **kwargs)

    elif value_type == "slice":
        s, e = data
        sub = obj[s:e]
        if not rest:
            obj[s:e] = value
        else:
            for sub_obj, sub_value in _iter_pairs(sub, value):
                _write(sub_obj, rest, sub_value, **kwargs)

    elif value_type == "map_keys_var":
        keys = kwargs[data]
        if not rest:
            for k, sub_value in _iter_pairs(keys, value):
                obj[k] = sub_value
        else:
            for k, sub_value in _iter_pairs(keys, value):
                _write(obj[k], rest, sub_value, **kwargs)

    elif value_type == "identity":
        _write(obj, rest, value, **kwargs)

    else:
        raise RuntimeError(f"Unhandled token type: {value_type}")
