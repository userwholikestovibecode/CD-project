"""Streamlit front end for the educational mini compiler."""

from pathlib import Path

import streamlit as st

from compiler.pipeline import compile_source

ROOT = Path(__file__).parent
SAMPLES = {
    path.stem.replace("_", " ").title(): path
    for path in sorted((ROOT / "samples").glob("*.c"))
}
DEFAULT = "int a = 5;\nint b = 2;\nprint(a + b * 3);"


def tree_dot(node, lines=None):
    lines = lines or []
    node_id = f"n{len(lines)}"
    label = type(node).__name__
    if hasattr(node, "name"):
        label += f"\\n{node.name}"
    elif hasattr(node, "operator"):
        label += f"\\n{node.operator}"
    elif hasattr(node, "value"):
        label += f"\\n{node.value}"
    lines.append(f'{node_id} [label="{label}"];')
    children = []
    for value in vars(node).values():
        if isinstance(value, list):
            children.extend(value)
        elif hasattr(value, "__dataclass_fields__"):
            children.append(value)
    for child in children:
        child_id = tree_dot(child, lines)
        lines.append(f"{node_id} -> {child_id};")
    return node_id


st.set_page_config(page_title="Mini Compiler", layout="wide")
st.title("Mini Compiler with Code Optimization")
st.sidebar.header("Program")
choice = st.sidebar.selectbox("Sample program", ["Custom"] + list(SAMPLES))
if choice == "Custom":
    initial = DEFAULT
else:
    initial = SAMPLES[choice].read_text(encoding="utf-8")
source = st.text_area("Source code", initial, height=220)
st.sidebar.markdown("### About Language")
st.sidebar.markdown("Statements use `int`, `float`, assignments, `print(expr);`, and `//` comments.")
st.sidebar.code("program ::= statement*\nstatement ::= type id [= expr] ; | id = expr ; | print ( expr ) ;")

if st.button("Compile", type="primary"):
    result = compile_source(source[:5000])
    status_colors = {"passed": "🟢", "failed": "🔴", "skipped": "⚪"}
    st.write("  →  ".join(f"{status_colors[p.status]} {name}" for name, p in result.phases.items()))
    phase = result.phases
    if phase["lexical"].output is not None:
        st.subheader("Tokens")
        st.dataframe(phase["lexical"].output, use_container_width=True)
    if phase["lexical"].errors:
        for error in phase["lexical"].errors:
            st.error(f"Line {error.line}: {error.message}")
    if phase["syntax"].output is not None:
        st.subheader("Syntax Tree")
        lines = []
        tree_dot(phase["syntax"].output, lines)
        st.graphviz_chart("digraph AST {\n" + "\n".join(lines) + "\n}")
    if phase["semantic"].output is not None:
        semantic = phase["semantic"].output
        st.subheader("Semantic Analysis and Symbol Table")
        st.dataframe([vars(symbol) for symbol in semantic.symbol_table.symbols()], use_container_width=True)
        for warning in semantic.warnings:
            st.warning(f"Line {warning.line}: {warning.message}")
    for error in phase["syntax"].errors + phase["semantic"].errors:
        st.error(f"Line {error.line}: {error.message}")
    if phase["intermediate_code"].output:
        st.subheader("Intermediate Code")
        st.code(phase["intermediate_code"].output.text)
    if phase["optimization"].output:
        optimization = phase["optimization"].output
        left, right = st.columns(2)
        with left:
            st.code("\n".join(item.text() for item in optimization.before))
        with right:
            st.code("\n".join(item.text() for item in optimization.after))
        st.write(f"{optimization.before_count} → {optimization.after_count} instructions")
        for log in optimization.logs:
            st.info(f"Instruction {log.instruction}: {log.rule} — {log.reason}")
    if phase["target_code"].output:
        st.subheader("Target Code")
        st.code(phase["target_code"].output.text)
    report = ["# Compilation Report", "", f"```text\n{source}\n```", ""]
    for name, item in phase.items():
        report.append(f"## {name.title()}: {item.status}")
        for error in item.errors:
            report.append(f"- Line {error.line}: {error.message}")
    st.download_button("Download full compilation report", "\n".join(report), "compilation-report.md")
