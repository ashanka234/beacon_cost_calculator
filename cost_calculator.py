import streamlit as st

# Initialize session state for storing entries if not already present
if 'cost_entries' not in st.session_state:
    st.session_state.cost_entries = []

# Function to format numbers in Indian numbering system
def indian_format(n):
    s = str(n)
    if '.' in s:
        main, decimal = s.split('.')
    else:
        main, decimal = s, ''
    # Reverse the main string to place commas
    main = main[::-1]
    # Place the first comma after the first three digits, then every two
    parts = [main[:3]] + [main[i:i+2] for i in range(3, len(main), 2)]
    formatted = ','.join(parts)[::-1]
    return formatted if not decimal else f"{formatted}.{decimal}"

# Function to calculate cost based on inputs
def calculate_cost(type, **kwargs):
    daily_cost = kwargs['cost_per_month'] / 30
    margin_multiplier = 1 + (kwargs['margin'] / 100)
    return daily_cost * kwargs['days'] * margin_multiplier

# Function to add new cost entry
def add_cost_entry(type, description, **kwargs):
    if type in ['person_cost', 'service_cost']:
        kwargs['cost_per_month'] = kwargs['cost_per_unit'] * kwargs['units']
    cost = calculate_cost(type, **kwargs)
    entry = {"type": type, "description": description, "cost": cost}
    st.session_state.cost_entries.append(entry)

# Function to remove a cost entry
def remove_cost_entry(index):
    del st.session_state.cost_entries[index]

# Function to reset all entries
def clear_all_entries():
    st.session_state.cost_entries = []

# Page layout
st.title("Campaign Cost Calculator")

# Using session_state to track current expense type and force a UI update on change
expense_type = st.selectbox("Select Expense Type", ["person_cost", "service_cost", "direct_cost"],
                            index=0, key='expense_selector', on_change=lambda: setattr(st.session_state, 'expense_type', expense_type))
description = st.text_input("Description of the Cost", key='desc_input')

with st.form("cost_form"):
    # Fields dynamically adjust based on the expense type
    if expense_type == "person_cost":
        salary = st.number_input("Salary per Month", step=100, key=f'salary_input_{expense_type}')
        people = st.number_input("Number of People Required", step=1, key=f'people_input_{expense_type}')
    elif expense_type == "service_cost":
        cost_per_user = st.number_input("Cost per User per Month", step=1, key=f'cpu_input_{expense_type}')
        users = st.number_input("Number of Users", step=1, key=f'users_input_{expense_type}')
    elif expense_type == "direct_cost":
        cost_per_month = st.number_input("Cost per Month", step=100, key=f'cpm_input_{expense_type}')

    days = st.number_input("Number of Days", step=1, key=f'days_input_{expense_type}')
    margin = st.number_input("Profit Margin (%)", step=1, format="%d", key=f'margin_input_{expense_type}')
    submit_button = st.form_submit_button("Add Cost")

if submit_button:
    kwargs = {
        'days': days,
        'margin': margin
    }
    if expense_type == "person_cost":
        kwargs.update({'cost_per_unit': salary, 'units': people})
    elif expense_type == "service_cost":
        kwargs.update({'cost_per_unit': cost_per_user, 'units': users})
    elif expense_type == "direct_cost":
        kwargs.update({'cost_per_month': cost_per_month})
    add_cost_entry(expense_type, description, **kwargs)

# Display entries with an option to remove each
for index, entry in enumerate(st.session_state.cost_entries):
    st.write(f"{entry['description']}: INR {indian_format(entry['cost'])}")
    if st.button(f"Remove {index}", key=f"remove_{index}"):
        remove_cost_entry(index)

if st.button("Clear All"):
    clear_all_entries()

# Display total cost
total_cost = sum(entry['cost'] for entry in st.session_state.cost_entries)
st.markdown(f"<h1 style='font-size:2em; font-weight:bold;'>Total Cost: INR {indian_format(total_cost)}</h1>", unsafe_allow_html=True)
