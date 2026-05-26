def generate_flowchart(code: str):
    # simple heuristic version (upgrade later with AST)
    lines = code.split("\n")

    flow = ["flowchart TD"]
    prev = "Start"

    flow.append(f"A[Start] --> B[Input Code]")

    for i, line in enumerate(lines[:10]):
        node = f"N{i}[{line.strip()[:20]}]"
        flow.append(f"{prev} --> {node}")
        prev = node

    flow.append(f"{prev} --> End[End]")

    return "\n".join(flow)

def estimate_complexity(code: str):
    loops = code.count("for ") + code.count("while ")

    if loops == 0:
        tc = "O(1)"
    elif loops == 1:
        tc = "O(n)"
    elif loops == 2:
        tc = "O(n^2)"
    else:
        tc = "O(n^k)"

    return {
        "time": tc,
        "space": "O(1)",
        "explanation": "Estimated based on loop counting heuristic"
    }
