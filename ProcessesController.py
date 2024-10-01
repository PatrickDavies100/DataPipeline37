# processes.py

# Initialize a list to hold processes
processes = []
temp_processes = []


def add_process(process: tuple) -> None:
    """Add a process to the list."""
    processes.append(process)


def remove_process_by_i(process, i: int):
    """Remove a process from the list."""
    del processes[i]


def clear_processes():
    """Clear all processes."""
    processes.clear()


def get_processes():
    """Return the current list of processes."""
    return processes


def print_processes():
    current_processes = get_processes()
    print("Current process:")
    for i, step in enumerate(current_processes, 1):
        blah = str({step[1]})
        if {step[1]} == {-1}:
            blah = "*"
        print(f"{i}. {step[0]}: " + blah)


def add_temp_process(temp_process: str) -> None:
    """Add a process to the list."""
    temp_processes.append(temp_process)


def remove_temp_process_by_i(temp_process, i: int):
    """Remove a process from the list."""
    del temp_processes[i]


def clear_temp_processses():
    """Clear all temp_processes."""
    temp_processes.clear()


def get_temp_processes():
    """Return the current list of temp_processes."""
    return temp_processes


def print_temp_processes():
    current_temp_processes = get_temp_processes()
    print("Current temp_process:")
    for i, step in enumerate(current_temp_processes, 1):
        blah = str({step[1]})
        if {step[1]} == {-1}:
            blah = "*"
        print(f"{i}. {step[0]}: " + blah)

# Add processes:
# processes.add_process("Step 1: Preheat the oven to 180°C.")
# processes.add_process("Step 2: Mix flour and sugar.")
# processes.add_process("Step 3: Bake for 20 minutes.")

# Modify processes
# processes.remove_process("Step 3: Bake for 20 minutes.")
# processs.add_process("Step 3: Bake for 25 minutes.")

# Access processes


# Clear all processes
# processes.clear_processes()