import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.decomposition import PCA

class ExtendedHoloToLFramework:
    """Extended HoloToL framework with NCBI integration"""

    def __init__(self, num_species, dimensions=16):
        self.num_species = num_species
        self.dimensions = dimensions
        self.quantum_states = self._initialize_quantum_states()
        self.entanglement_matrix = self._create_entanglement_matrix()
        self.consciousness_field = np.zeros((num_species, dimensions))
        self.organism_names = []

    def _initialize_quantum_states(self):
        """Initialize quantum states with improved normalization"""
        states = np.random.randn(self.num_species, self.dimensions) + \
                1j * np.random.randn(self.num_species, self.dimensions)
        # Normalize each state
        for i in range(self.num_species):
            norm = np.linalg.norm(states[i])
            if norm > 0:
                states[i] = states[i] / norm
        return states

    def _create_entanglement_matrix(self):
        """Create entanglement matrix with phylogenetic distance"""
        matrix = np.zeros((self.num_species, self.num_species))
        for i in range(self.num_species):
            for j in range(i+1, self.num_species):
                # Quantum fidelity-based entanglement
                fidelity = np.abs(np.vdot(self.quantum_states[i], self.quantum_states[j]))**2
                entanglement = np.sqrt(1 - fidelity)
                matrix[i,j] = matrix[j,i] = entanglement
        return matrix

    def load_biological_data(self, feature_matrix, organism_names):
        """Load biological data into quantum framework"""
        if len(feature_matrix) != self.num_species:
            raise ValueError(f"Expected {self.num_species} species, got {len(feature_matrix)}")

        self.organism_names = organism_names

        # Convert biological features to quantum states
        # Use PCA to reduce to quantum dimensions if needed
        if feature_matrix.shape[1] > self.dimensions:
            pca = PCA(n_components=self.dimensions)
            reduced_features = pca.fit_transform(feature_matrix)
        else:
            # Pad with zeros if fewer features
            reduced_features = np.zeros((self.num_species, self.dimensions))
            reduced_features[:, :feature_matrix.shape[1]] = feature_matrix

        # Normalize and convert to quantum states
        scaler = MinMaxScaler()
        normalized_features = scaler.fit_transform(reduced_features)

        # Create quantum states with phase information
        self.quantum_states = normalized_features + 1j * np.random.randn(*normalized_features.shape) * 0.1

        # Renormalize quantum states
        for i in range(self.num_species):
            norm = np.linalg.norm(self.quantum_states[i])
            if norm > 0:
                self.quantum_states[i] = self.quantum_states[i] / norm

        # Update entanglement matrix
        self.entanglement_matrix = self._create_entanglement_matrix()

    def von_neumann_entropy(self, density_matrix):
        """Calculate von Neumann entropy with numerical stability"""
        eigenvalues = np.linalg.eigvalsh(density_matrix)
        eigenvalues = np.maximum(eigenvalues, 1e-12)  # Avoid log(0)
        entropy = -np.sum(eigenvalues * np.log(eigenvalues))
        return np.real(entropy)

    def calculate_entanglement_entropy(self):
        """Calculate holographic entanglement entropy"""
        # Create reduced density matrix for first half of system
        half_size = self.num_species // 2
        subsystem_states = self.quantum_states[:half_size]

        # Simple density matrix approximation
        density_matrix = np.outer(subsystem_states.flatten(),
                                np.conj(subsystem_states.flatten()))

        return self.von_neumann_entropy(density_matrix)

    def evolutionary_dynamics(self, time_steps, dt=0.1):
        """Enhanced evolutionary dynamics with biological constraints"""
        history = []
        entropy_history = []
        consciousness_history = []

        for step in range(time_steps):
            # Build Hamiltonian with biological terms
            hamiltonian = self._build_biological_hamiltonian(step)

            # Time evolution
            U = self._safe_matrix_exponential(-1j * hamiltonian * dt)

            # Update quantum states
            old_states = self.quantum_states.copy()
            self.quantum_states = U @ self.quantum_states

            # Renormalize states
            for i in range(self.num_species):
                norm = np.linalg.norm(self.quantum_states[i])
                if norm > 0:
                    self.quantum_states[i] = self.quantum_states[i] / norm

            # Update consciousness field
            self._update_consciousness_field(dt, step)

            # Calculate observables
            entropy = self.calculate_entanglement_entropy()
            consciousness = self.calculate_complexity()

            history.append(self.quantum_states.copy())
            entropy_history.append(entropy)
            consciousness_history.append(consciousness)

            if step % 10 == 0:
                print(f"Step {step}: Entropy={entropy:.4f}, Consciousness={consciousness:.6f}")

        return {
            'states_history': history,
            'entropy_history': entropy_history,
            'consciousness_history': consciousness_history
        }

    def _build_biological_hamiltonian(self, step):
        """Build Hamiltonian with biological evolution terms"""
        hamiltonian = np.zeros((self.num_species, self.num_species), dtype=complex)

        # Diagonal terms (self-energy from fitness)
        for i in range(self.num_species):
            fitness = np.random.normal(0, 0.1)  # Fitness fluctuations
            hamiltonian[i,i] = fitness

        # Off-diagonal terms (species interactions)
        for i in range(self.num_species):
            for j in range(i+1, self.num_species):
                # Interaction strength based on phylogenetic distance
                interaction = self.entanglement_matrix[i,j] * np.exp(1j * np.random.uniform(0, 2*np.pi))
                interaction *= (0.5 + 0.5 * np.cos(step * 0.1))  # Time-varying interactions

                hamiltonian[i,j] = interaction
                hamiltonian[j,i] = np.conj(interaction)

        return hamiltonian

    def _safe_matrix_exponential(self, matrix):
        """Safely compute matrix exponential"""
        try:
            from scipy.linalg import expm
            return expm(matrix)
        except:
            # Fallback to Taylor series approximation
            return np.eye(matrix.shape[0]) + matrix + 0.5 * matrix @ matrix

    def _update_consciousness_field(self, dt, step):
        """Update consciousness field with biological constraints"""
        for i in range(self.num_species):
            # Consciousness potential from quantum state
            potential = np.linalg.norm(self.quantum_states[i])**2

            # Non-linear consciousness dynamics
            consciousness_magnitude = np.linalg.norm(self.consciousness_field[i])

            # Update with damping and driving terms
            self.consciousness_field[i] += dt * (
                potential * np.random.randn(self.dimensions) * 0.1 -
                consciousness_magnitude * self.consciousness_field[i] * 0.01 +
                0.01 * np.sin(step * 0.1) * np.random.randn(self.dimensions)
            )

    def detect_phase_transitions(self, entropy_history, threshold=0.1):
        """Detect evolutionary phase transitions"""
        if len(entropy_history) < 3:
            return []

        derivatives = np.gradient(entropy_history)
        second_derivatives = np.gradient(derivatives)

        # Find rapid changes in entropy
        transitions = []
        for i in range(1, len(second_derivatives)-1):
            if abs(second_derivatives[i]) > threshold:
                transitions.append(i)

        return transitions

    def calculate_complexity(self):
        """Calculate consciousness complexity score"""
        if self.consciousness_field.size == 0:
            return 0.0

        field_norms = np.linalg.norm(self.consciousness_field, axis=1)
        complexity = np.mean(field_norms) + np.std(field_norms)
        return complexity

    def analyze_species_correlations(self):
        """Analyze quantum correlations between species"""
        correlations = np.zeros((self.num_species, self.num_species))

        for i in range(self.num_species):
            for j in range(self.num_species):
                # Quantum correlation measure
                overlap = np.abs(np.vdot(self.quantum_states[i], self.quantum_states[j]))**2
                correlations[i,j] = overlap

        return correlations
