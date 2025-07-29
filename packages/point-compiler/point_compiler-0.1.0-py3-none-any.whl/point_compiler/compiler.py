from collections import defaultdict, deque
import operator

class Point:
    def __init__(self, name, ptype, param=None, param2=None):
        self.name = name
        self.ptype = ptype.upper()
        self.param = param
        self.param2 = param2
        self.inputs = []
        self.outputs = []
        self.value = None
        self.label = None

    def __repr__(self):
        return f"Point({self.name}, {self.ptype}, {self.param}, {self.param2})"

class PointGraph:
    def __init__(self):
        self.points = {}
        self.edges = defaultdict(list)

    def add_point(self, name, ptype, param=None, param2=None):
        self.points[name] = Point(name, ptype, param, param2)

    def connect(self, src, tgt, condition=None):
        self.edges[src].append((tgt, condition))
        self.points[tgt].inputs.append(src)
        self.points[src].outputs.append(tgt)

    def run(self, inputs):
        for name, val in inputs.items():
            if name not in self.points:
                raise ValueError(f"Input point {name} not found")
            p = self.points[name]
            if p.ptype != "INPUT":
                raise ValueError(f"Point {name} is not an INPUT point")
            p.value = val

        queue = deque([p for p in self.points.values() if p.value is not None])

        while queue:
            current = queue.popleft()
            pt = current.ptype

            if pt == "OUTPUT":
                print(f"OUTPUT {current.name}: {current.value}")
                continue
            elif pt == "OUTPUT_CHAR":
                val = current.value
                if isinstance(val, int):
                    print(chr(val), end='')
                else:
                    print(val, end='')
                continue
            elif pt == "CLEAR":
                current.value = 0
            elif pt == "EXIT":
                print("Program exited at point:", current.name)
                break
            elif pt == "ADD":
                if current.inputs:
                    input_val = self.points[current.inputs[0]].value
                    current.value = input_val + current.param
            elif pt == "MULTIPLY":
                if current.inputs:
                    input_val = self.points[current.inputs[0]].value
                    current.value = input_val * current.param
            elif pt == "CONDITIONAL":
                if current.inputs:
                    input_val = self.points[current.inputs[0]].value
                    op_str = current.param
                    threshold = current.param2
                    ops = {
                        '>': operator.gt,
                        '<': operator.lt,
                        '==': operator.eq,
                        '<=': operator.le,
                        '>=': operator.ge,
                        '!=': operator.ne,
                    }
                    if op_str not in ops:
                        raise ValueError(f"Unsupported operator in CONDITIONAL: {op_str}")
                    cond_result = ops[op_str](input_val, threshold)
                    current.value = input_val
                else:
                    cond_result = False
            elif pt == "JUMP":
                if current.inputs:
                    input_val = self.points[current.inputs[0]].value
                    current.value = input_val
            elif pt in ("AND", "OR", "XOR"):
                if len(current.inputs) < 2:
                    raise ValueError(f"{pt} requires 2 inputs")
                v1 = self.points[current.inputs[0]].value
                v2 = self.points[current.inputs[1]].value
                if v1 is None or v2 is None:
                    current.value = None
                else:
                    if pt == "AND":
                        current.value = int(bool(v1) and bool(v2))
                    elif pt == "OR":
                        current.value = int(bool(v1) or bool(v2))
                    elif pt == "XOR":
                        current.value = int(bool(v1) != bool(v2))
            elif pt == "NOT":
                if current.inputs:
                    v = self.points[current.inputs[0]].value
                    current.value = int(not bool(v)) if v is not None else None
            elif pt == "INPUT":
                pass
            else:
                raise ValueError(f"Unknown point type: {pt}")

            for tgt_name, cond in self.edges[current.name]:
                tgt = self.points[tgt_name]
                if pt in ("CLEAR", "JUMP"):
                    if cond is not None and cond != current.label:
                        continue
                elif pt == "CONDITIONAL":
                    if cond == "true" and cond_result:
                        tgt.value = current.value
                        queue.append(tgt)
                    elif cond == "false" and not cond_result:
                        tgt.value = current.value
                        queue.append(tgt)
                    continue
                tgt.value = current.value
                tgt.label = cond
                queue.append(tgt)

def parse_program(text):
    graph = PointGraph()
    inputs = {}
    lines = [line.strip() for line in text.splitlines() if line.strip() and not line.strip().startswith("#")]

    for line in lines:
        if line.startswith("point"):
            left, right = line.split(":", 1)
            _, name = left.split()
            parts = right.strip().split()
            ptype = parts[0]
            param = None
            param2 = None
            if len(parts) > 1:
                if ptype.upper() == "CONDITIONAL" and len(parts) >= 3:
                    param = parts[1]
                    try:
                        param2 = int(parts[2])
                    except ValueError:
                        param2 = parts[2]
                else:
                    try:
                        param = int(parts[1])
                    except (ValueError, IndexError):
                        param = parts[1] if len(parts) > 1 else None
            graph.add_point(name, ptype, param, param2)
        elif line.startswith("connect"):
            line = line[len("connect"):].strip()
            if "->" not in line:
                raise ValueError(f"Invalid connect line: {line}")
            src, tgt = line.split("->")
            src = src.strip()
            tgt = tgt.strip()
            src_cond = None
            tgt_cond = None
            if "." in src:
                src, src_cond = src.split(".", 1)
            if "." in tgt:
                tgt, tgt_cond = tgt.split(".", 1)
            if src_cond is not None:
                raise ValueError("Conditions on source point not supported yet")
            graph.connect(src, tgt, tgt_cond)
        elif line.startswith("input"):
            parts = line.split()
            if len(parts) >= 4 and parts[2] == "=":
                name = parts[1]
                try:
                    val = int(parts[3])
                except ValueError:
                    val = parts[3]
                inputs[name] = val
            else:
                raise ValueError(f"Invalid input line: {line}")
    return graph, inputs

def load_program_from_file(filename):
    with open(filename, 'r') as f:
        text = f.read()
    return parse_program(text)

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python pointlang.py yourprogram.pnt")
        sys.exit(1)
    filename = sys.argv[1]
    graph, inputs = load_program_from_file(filename)
    print(f"Running program '{filename}' with inputs {inputs}")
    graph.run(inputs)
