import json
import time
from .data_loader import NCBIDataLoader
from .data_processor import BiologicalDataProcessor
from .framework import ExtendedHoloToLFramework

def comprehensive_ncbi_holotol_pipeline():
    """Complete pipeline integrating NCBI data with HoloToL framework"""

    print("=== HoloToL Framework with NCBI Real Dataset Integration ===\n")

    # Initialize data loader and processor
    ncbi_loader = NCBIDataLoader()
    bio_processor = BiologicalDataProcessor()

    # Define organism datasets to analyze
    datasets = {
        'bacteria': ['Escherichia coli', 'Bacillus subtilis', 'Streptococcus pyogenes'],
        'vertebrates': ['Homo sapiens', 'Mus musculus', 'Danio rerio'],
        'plants': ['Arabidopsis thaliana', 'Oryza sativa', 'Zea mays'],
        'fungi': ['Saccharomyces cerevisiae', 'Candida albicans']
    }

    results = {}

    for kingdom, organisms in datasets.items():
        print(f"\n--- Processing {kingdom.upper()} dataset ---")

        all_sequences = []
        all_names = []

        # Collect sequences for each organism
        for organism in organisms:
            print(f"Fetching data for {organism}...")
            sequences = ncbi_loader.get_organism_dataset(organism, max_sequences=5)

            if sequences:
                all_sequences.extend(sequences)
                all_names.extend([organism] * len(sequences))
                print(f"Retrieved {len(sequences)} sequences for {organism}")
            else:
                print(f"No sequences found for {organism}")

        if not all_sequences:
            print(f"No data available for {kingdom}")
            continue

        # Process sequences into features
        feature_matrix, organism_names = bio_processor.process_sequences(all_sequences)

        if feature_matrix.size == 0:
            print(f"No valid features extracted for {kingdom}")
            continue

        print(f"Extracted features: {feature_matrix.shape}")
        print(f"Species: {len(set(organism_names))}")

        # Initialize HoloToL framework
        num_species = len(all_sequences)
        framework = ExtendedHoloToLFramework(num_species)

        # Load biological data
        framework.load_biological_data(feature_matrix, organism_names)

        # Run evolutionary simulation
        print(f"Running quantum evolution simulation for {kingdom}...")
        evolution_results = framework.evolutionary_dynamics(time_steps=25)

        # Analyze results
        entropy_history = evolution_results['entropy_history']
        consciousness_history = evolution_results['consciousness_history']

        # Detect phase transitions
        transitions = framework.detect_phase_transitions(entropy_history)

        # Calculate final metrics
        final_complexity = framework.calculate_complexity()
        species_correlations = framework.analyze_species_correlations()

        # Store results
        results[kingdom] = {
            'num_species': num_species,
            'organisms': list(set(organism_names)),
            'entropy_history': entropy_history,
            'consciousness_history': consciousness_history,
            'phase_transitions': transitions,
            'final_complexity': final_complexity,
            'species_correlations': species_correlations.tolist(),
            'final_entropy': entropy_history[-1] if entropy_history else 0
        }

        # Print summary
        print(f"\n{kingdom.upper()} RESULTS:")
        print(f"Species count: {num_species}")
        print(f"Final complexity: {final_complexity:.6f}")
        print(f"Phase transitions at steps: {transitions}")
        print(f"Final entropy: {entropy_history[-1]:.4f}" if entropy_history else "N/A")

        # Brief pause between datasets
        time.sleep(1)

    # Generate comprehensive report
    print("\n=== COMPREHENSIVE ANALYSIS REPORT ===")

    for kingdom, data in results.items():
        print(f"\n{kingdom.upper()}:")
        print(f"  Species analyzed: {data['num_species']}")
        print(f"  Complexity score: {data['final_complexity']:.6f}")
        print(f"  Phase transitions: {len(data['phase_transitions'])}")
        print(f"  Final entropy: {data['final_entropy']:.4f}")
        print(f"  Organisms: {', '.join(data['organisms'][:3])}{'...' if len(data['organisms']) > 3 else ''}")

    # Save results
    with open('holotol_ncbi_results.json', 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to 'holotol_ncbi_results.json'")
    print("Analysis complete!")

    return results

# Run the complete pipeline
if __name__ == "__main__":
    # Make sure to set your email in the NCBIDataLoader class
    results = comprehensive_ncbi_holotol_pipeline()
