# HoloToL Framework Python Package

## Overview

The `holotol_framework` is a Python package designed for integrating biological sequence data from NCBI with a conceptual "HoloToL" (Holographic Tree of Life) framework. It provides tools for:

*   **NCBI Data Loading:** Efficiently searching and fetching nucleotide sequences from the NCBI database with rate limiting and error handling.
*   **Biological Data Processing:** Converting raw DNA sequences into numerical features (e.g., nucleotide composition, GC content, dinucleotide frequencies) suitable for analysis.
*   **Extended HoloToL Framework:** A conceptual framework that models biological species as quantum states, exploring evolutionary dynamics, entanglement, and a "consciousness field" based on biological features.
*   **Comprehensive Pipeline:** A complete workflow to fetch data for various organisms, process it, load it into the HoloToL framework, and simulate evolutionary dynamics.

This package is intended for research and conceptual exploration of biological systems through a quantum-inspired lens.

## Installation

To install the `holotol_framework` package, follow these steps:

1.  **Clone the repository** (if you haven't already):
    \`\`\`bash
    git clone <repository_url>
    cd holotol-framework-package
    \`\`\`
    (Replace `<repository_url>` with the actual URL of your repository.)

2.  **Navigate to the root directory** of the package (where `setup.py` is located).

3.  **Install the package** using pip:
    \`\`\`bash
    pip install .
    \`\`\`

This will install the `holotol_framework` package and all its required dependencies.

## Dependencies

The package relies on the following Python libraries:

*   `numpy`
*   `pandas`
*   `biopython`
*   `scikit-learn`
*   `scipy`

These will be automatically installed when you run `pip install .`.

## Usage

### Running the Comprehensive Pipeline

The package includes a comprehensive pipeline that fetches data, processes it, and runs the HoloToL simulation. You can execute it directly from the command line:

\`\`\`bash
python -m holotol_framework.pipeline
\`\`\`

**Important:** Before running, ensure you have set your NCBI email address in the `holotol_framework/data_loader.py` file. NCBI requires an email for Entrez access.

### Using Individual Components

You can also import and use the individual classes and functions in your own Python scripts:

\`\`\`python
from holotol_framework.data_loader import NCBIDataLoader
from holotol_framework.data_processor import BiologicalDataProcessor
from holotol_framework.framework import ExtendedHoloToLFramework
from holotol_framework.pipeline import comprehensive_ncbi_holotol_pipeline

# --- Example 1: Run the full pipeline ---
print("Running the comprehensive HoloToL pipeline...")
results = comprehensive_ncbi_holotol_pipeline()
print("\nPipeline results saved to 'holotol_ncbi_results.json'")

# --- Example 2: Using individual components ---
print("\n--- Demonstrating individual components ---")

# Initialize data loader (IMPORTANT: Set your NCBI email)
loader = NCBIDataLoader(email="your.email@example.com")

# Fetch sequences for a specific organism
print("Fetching sequences for Homo sapiens...")
sequences = loader.get_organism_dataset("Homo sapiens", max_sequences=5)

if sequences:
    # Process sequences into features
    processor = BiologicalDataProcessor()
    features, names = processor.process_sequences(sequences)

    if features.size > 0:
        print(f"Processed {len(sequences)} sequences into features of shape {features.shape}")

        # Initialize HoloToL framework
        framework = ExtendedHoloToLFramework(num_species=len(sequences))

        # Load biological data into the framework
        framework.load_biological_data(features, names)

        # Run evolutionary simulation
        print("Running quantum evolution simulation...")
        evolution_results = framework.evolutionary_dynamics(time_steps=25)

        print("\nSimulation complete. Final entropy:", evolution_results['entropy_history'][-1])
        print("Final consciousness complexity:", framework.calculate_complexity())
    else:
        print("No valid features extracted.")
else:
    print("No sequences found for Homo sapiens.")
\`\`\`

## Important Notes

*   **NCBI Email:** You **must** set your email address in the `NCBIDataLoader` class (located in `holotol_framework/data_loader.py`) for NCBI Entrez access. This is a requirement from NCBI.
    \`\`\`python
    # In holotol_framework/data_loader.py
    Entrez.email = "your.email@example.com" # <--- CHANGE THIS
    \`\`\`
*   **Rate Limiting:** The `NCBIDataLoader` includes a rate limit to comply with NCBI's usage policies. Do not modify this unless you understand the implications.
*   **Conceptual Framework:** The "HoloToL" framework is a conceptual model. Its quantum mechanics and consciousness aspects are theoretical constructs for exploring biological data.

## License

This project is open-sourced under the MIT License. See the `LICENSE` file for more details.
