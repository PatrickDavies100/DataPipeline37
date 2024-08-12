# processes.py

# Initialize a list to hold processes
processes = []


def add_process(process):
    """Add a process to the list."""
    processes.append(process)


def remove_process(process):
    """Remove a process from the list."""
    if process in processes:
        processes.remove(process)


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