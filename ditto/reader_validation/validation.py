from create_compare import create_output_dir, create_dict
from create_excel import write_to_excel
from create_plots import plots
import os

# Path to the directory which contains test cases
current_dir = os.path.realpath(os.path.dirname(__file__))
small_tests_dir = os.path.join(current_dir, "../../tests/data/small_cases")

# Create the output directory
output_dir = create_output_dir(small_tests_dir)

# Create a dictionary of all the readers outputs (Each Node will have R0, X0, R1, X1 values) from the output saved in output_dir
comp_values = create_dict(output_dir)

# Writing the output to excel as output.xlsx in the current directory
write_to_excel(comp_values)

# Plotting the sequence impedance values of all readers
plots(comp_values)
