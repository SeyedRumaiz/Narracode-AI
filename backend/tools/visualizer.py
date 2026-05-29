"""Visualization helpers for code flowchart generation and complexity estimation."""

from typing import Dict


def _sanitize_mermaid_label(text: str) -> str:
    """Escape mermaid flowchart labels and trim length for readability."""
    label = text.strip().replace('"', '\\"').replace('[', '\\[').replace(']', '\\]').replace('<', '&lt;').replace('>', '&gt;')
    if len(label) > 50:
        label = label[:47].rstrip() + '...'
    return label or 'step'


def generate_flowchart(code: str) -> str:
    """Generate a simple Mermaid flowchart from the given code snippet."""
    lines = [line for line in code.split('\n') if line.strip()]
    flow = ['flowchart TD']
    previous_node = 'A[Start]'
    flow.append('A[Start] --> B[Input Code]')

    for index, line in enumerate(lines[:10]):
        label = _sanitize_mermaid_label(line)
        node = f'N{index}["{label}"]'
        flow.append(f'{previous_node} --> {node}')
        previous_node = node

    flow.append(f'{previous_node} --> End[End]')
    return '\n'.join(flow)


def estimate_complexity(code: str) -> Dict[str, str]:
    """Estimate time and space complexity using a simple loop-count heuristic."""
    loops = code.count('for ') + code.count('while ')
    if loops == 0:
        time_complexity = 'O(1)'
    elif loops == 1:
        time_complexity = 'O(n)'
    elif loops == 2:
        time_complexity = 'O(n^2)'
    else:
        time_complexity = 'O(n^k)'

    return {
        'time': time_complexity,
        'space': 'O(1)',
        'explanation': 'Estimated based on loop counting heuristic',
    }
