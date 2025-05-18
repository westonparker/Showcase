# Full Streamlit app with ALTER TABLE support and column constraints

import streamlit as st

# core logic and definition
class Table:
    def __init__(self, name, primary_key, elements):
        self.name = name
        self.primary_key = primary_key
        self.elements = elements  # list of tuples (column_name, datatype, constraint)

    def to_sql(self):
        lines = []
        for col, dtype, constraint in self.elements:
            constraint_part = f" {constraint}" if constraint else ""
            if col == self.primary_key and "PRIMARY KEY" not in constraint.upper():
                constraint_part += " PRIMARY KEY"
            lines.append(f"    {col} {dtype}{constraint_part}")
        return f"CREATE TABLE {self.name} (\n" + ",\n".join(lines) + "\n);"

# state
if "tables" not in st.session_state:
    st.session_state.tables = []

if "connections" not in st.session_state:
    st.session_state.connections = []  # (from_table, from_col, to_table, to_col)

# sidebar
st.sidebar.header("Create Table")

with st.sidebar.form("create_table"):
    table_name = st.text_input("Table Name")
    primary_key = st.text_input("Primary Key Column")
    col_input = st.text_area("Columns (Enter Column Name, Type and Constraints, with spaces seperating)", height=150, help="Example:\nid INT PRIMARY KEY\nname TEXT NOT NULL\nage INT DEFAULT 0")
    submitted = st.form_submit_button("Add Table")

    if submitted and table_name and col_input:
        columns = []
        valid = True
        for line in col_input.strip().splitlines():
            parts = line.strip().split(maxsplit=2)
            if len(parts) < 2:
                st.sidebar.error(f"Invalid column format: '{line}'")
                valid = False
                break
            col_name = parts[0]
            col_type = parts[1].upper()
            constraint = parts[2] if len(parts) == 3 else ""
            columns.append((col_name, col_type, constraint))

        if not valid:
            pass
        elif primary_key not in [col for col, _, _ in columns]:
            st.sidebar.error("Primary key must be one of the defined columns.")
        else:
            st.session_state.tables.append(Table(table_name, primary_key, columns))
            st.sidebar.success(f"Table '{table_name}' added.")


st.title("SQL Table Designer")

# Tables display
st.header("Tables")
for idx, tbl in enumerate(st.session_state.tables):
    with st.expander(tbl.name):
        st.text(f"Primary Key: {tbl.primary_key}")
        for col, dtype, constraint in tbl.elements:
            constraint_text = f" ({constraint})" if constraint else ""
            st.text(f" - {col}: {dtype}{constraint_text}")

        st.markdown("---")
        with st.form(f"alter_table_{idx}"):
            st.subheader("Alter Table")

            new_col_name = st.text_input("New Column Name", key=f"new_col_{idx}")
            new_col_type = st.text_input("New Column Type", key=f"new_type_{idx}")
            new_col_constraint = st.text_input("Constraint (optional)", key=f"new_constraint_{idx}")
            remove_col = st.selectbox("Remove Column", [c[0] for c in tbl.elements if c[0] != tbl.primary_key], key=f"drop_col_{idx}")
            submitted = st.form_submit_button("Apply Changes")

            if submitted:
                updated_cols = [c for c in tbl.elements if c[0] != remove_col]
                if new_col_name and new_col_type:
                    updated_cols.append((new_col_name, new_col_type.upper(), new_col_constraint))
                tbl.elements = updated_cols
                st.success("Table updated.")


# Foreign keys
st.header("Create Foreign Key Connection")
if len(st.session_state.tables) >= 2:
    cols = st.columns(2)
    with cols[0]:
        from_table = st.selectbox("From Table", [t.name for t in st.session_state.tables], key="from_tbl")
        from_tbl_obj = next(t for t in st.session_state.tables if t.name == from_table)
        from_col = st.selectbox("From Column", [c[0] for c in from_tbl_obj.elements], key="from_col")

    with cols[1]:
        to_table = st.selectbox("To Table", [t.name for t in st.session_state.tables if t.name != from_table], key="to_tbl")
        to_tbl_obj = next(t for t in st.session_state.tables if t.name == to_table)
        to_col = st.selectbox("To Column", [c[0] for c in to_tbl_obj.elements], key="to_col")

    # Fetch types
    from_type = next(dtype for col, dtype, _ in from_tbl_obj.elements if col == from_col)
    to_type = next(dtype for col, dtype, _ in to_tbl_obj.elements if col == to_col)

    if st.button("Create Connection"):
        if from_type != to_type:
            st.error(f"Type mismatch: {from_col} ({from_type}) ≠ {to_col} ({to_type})")
        else:
            st.session_state.connections.append((from_table, from_col, to_table, to_col))
            st.success("Connection added.")
else:
    st.info("Need at least 2 tables to create a foreign key relationship.")

# output sql
st.header("Generated SQL")

sql_blocks = [tbl.to_sql() for tbl in st.session_state.tables]
for from_table, from_col, to_table, to_col in st.session_state.connections:
    sql_blocks.append(f"ALTER TABLE {to_table} ADD FOREIGN KEY ({to_col}) REFERENCES {from_table}({from_col});")

full_sql = "\n\n".join(sql_blocks)
st.code(full_sql, language="sql")

# visualization
st.header("Schema Visualization (Graph View)")

dot = "digraph G {\n"
dot += '  node [shape=record, fontname="Helvetica"];\n'

# Create record-style table nodes with ports
for tbl in st.session_state.tables:
    fields = "|".join([f"<{col}> {col} : {dtype}" for col, dtype, _ in tbl.elements])
    dot += f'  {tbl.name} [label="{{{tbl.name}|{fields}}}"];\n'

# Draw FK arrows between column ports
for from_table, from_col, to_table, to_col in st.session_state.connections:
    dot += f'  {to_table}:{to_col} -> {from_table}:{from_col} [label="{to_col} ➝ {from_col}"];\n'

dot += "}"

st.graphviz_chart(dot)
