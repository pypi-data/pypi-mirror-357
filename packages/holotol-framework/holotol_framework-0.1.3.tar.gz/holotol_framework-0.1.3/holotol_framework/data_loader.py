import numpy as np
import pandas as pd
from Bio import Entrez, SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
import time
import warnings
warnings.filterwarnings('ignore')

# Set your email for NCBI access (required)
Entrez.email = "karlambrosius@outlook.com.au"
Entrez.tool = "HoloToLFramework"

class NCBIDataLoader:
    """NCBI dataset loader with rate limiting and error handling"""

    def __init__(self, email="karlambrosius@outlook.com.au"):
        Entrez.email = email
        self.rate_limit_delay = 0.34  # 3 requests per second max

    def search_organisms(self, organism_query, max_results=50):
        """Search for organisms in NCBI nucleotide database"""
        try:
            print(f"Searching NCBI for: {organism_query}")
            handle = Entrez.esearch(
                db="nucleotide",
                term=organism_query,
                retmax=max_results,
                idtype="acc"
            )
            search_results = Entrez.read(handle)
            handle.close()
            time.sleep(self.rate_limit_delay)
            return search_results["IdList"]
        except Exception as e:
            print(f"Search error: {e}")
            return []

    def fetch_sequences(self, id_list, batch_size=40):
        """Fetch sequence data from NCBI with batch processing"""
        sequences = []

        for i in range(0, len(id_list), batch_size):
            batch_ids = id_list[i:i+batch_size]
            try:
                print(f"Fetching batch {i//batch_size + 1}: {len(batch_ids)} sequences")

                # Fetch sequence data
                handle = Entrez.efetch(
                    db="nucleotide",
                    id=batch_ids,
                    rettype="fasta",
                    retmode="text"
                )

                # Parse sequences
                batch_sequences = list(SeqIO.parse(handle, "fasta"))
                sequences.extend(batch_sequences)
                handle.close()

                time.sleep(self.rate_limit_delay)

            except Exception as e:
                print(f"Fetch error for batch {i//batch_size + 1}: {e}")
                continue

        return sequences

    def get_organism_dataset(self, organism_name, gene_name="", max_sequences=40):
        """Get complete dataset for specific organism"""
        query = f"{organism_name}[Organism]"
        if gene_name:
            query += f" AND {gene_name}[Gene]"

        # Search for sequences
        id_list = self.search_organisms(query, max_sequences)

        if not id_list:
            print(f"No sequences found for {organism_name}")
            return []

        # Fetch sequences
        sequences = self.fetch_sequences(id_list[:max_sequences])
        return sequences
