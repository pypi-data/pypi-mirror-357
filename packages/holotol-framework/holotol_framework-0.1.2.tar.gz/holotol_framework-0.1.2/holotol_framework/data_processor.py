import numpy as np

class BiologicalDataProcessor:
    """Process biological sequences for HoloToL analysis"""

    def __init__(self):
        self.nucleotide_mapping = {'A': 0, 'T': 1, 'G': 2, 'C': 3, 'N': 4}

    def sequence_to_features(self, sequence, max_length=1000):
        """Convert DNA sequence to numerical features"""
        seq_str = str(sequence).upper()[:max_length]

        # Nucleotide composition
        composition = np.zeros(5)  # A, T, G, C, N
        for nucleotide in seq_str:
            if nucleotide in self.nucleotide_mapping:
                composition[self.nucleotide_mapping[nucleotide]] += 1

        if len(seq_str) > 0:
            composition = composition / len(seq_str)

        # GC content
        gc_content = (composition[2] + composition[3])  # G + C

        # Dinucleotide frequencies
        dinucleotides = ['AA', 'AT', 'AG', 'AC', 'TT', 'TG', 'TC', 'GG', 'GC', 'CC']
        dinuc_freq = np.zeros(len(dinucleotides))

        for i, dinuc in enumerate(dinucleotides):
            dinuc_freq[i] = seq_str.count(dinuc) / max(1, len(seq_str) - 1)

        # Combine features
        features = np.concatenate([
            composition,  # 5 features
            [gc_content], # 1 feature
            dinuc_freq    # 10 features
        ])

        return features

    def process_sequences(self, sequences):
        """Process list of sequences into feature matrix"""
        if not sequences:
            return np.array([]), []

        features_list = []
        organism_names = []

        for seq_record in sequences:
            features = self.sequence_to_features(seq_record.seq)
            features_list.append(features)

            # Extract organism name from description
            description = seq_record.description
            organism_name = self.extract_organism_name(description)
            organism_names.append(organism_name)

        return np.array(features_list), organism_names

    def extract_organism_name(self, description):
        """Extract organism name from sequence description"""
        try:
            # Look for organism name patterns
            if '[' in description and ']' in description:
                start = description.find('[') + 1
                end = description.find(']')
                return description[start:end]
            else:
                # Take first two words as organism name
                words = description.split()
                return ' '.join(words[1:3]) if len(words) >= 3 else description[:50]
        except:
            return "Unknown organism"
