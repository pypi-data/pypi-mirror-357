from ProtPeptigram.logger import CONSOLE as console
import pandas as pd
import numpy as np
import re
import os
from io import StringIO
from typing import List, Dict, Union, Optional, Tuple, Set
from Bio import SeqIO

class PeptideDataProcessor:
    """
    Process peptide data from PEAKS Online output for visualization with ImmunoViz.
    
    This class handles:
    1. Loading and parsing PEAKS output CSV files
    2. Filtering contaminants and iRT peptides
    3. Extracting protein IDs from Accession column
    4. Mapping peptides to protein sequences to determine start/end positions
    5. Formatting data for ImmunoViz visualization
    """
    
    def __init__(self, 
                 peaks_file: str = None, 
                 fasta_file: str = None,
                 contaminant_keywords: List[str] = None,
                 sample_prefix:str = "Intensity"): #sample_prefix: str = "Intensity_"):
        """
        Initialize the PeptideDataProcessor.
        
        Parameters:
        -----------
        peaks_file : str, optional
            Path to the PEAKS output CSV file
        fasta_file : str, optional
            Path to the FASTA file containing protein sequences
        contaminant_keywords : List[str], optional
            List of keywords to identify contaminant proteins
        sample_prefix : str, optional
            Prefix for sample intensity columns (default: "Intensity")
        """
        # Set default contaminant keywords if not provided
        if contaminant_keywords is None:
            self.contaminant_keywords = [
                "CONTAM", "CONT_", "REV_", "iRT", "REVERSE" ,"DECOY" #, "sp|", "tr|", "keratin", "KRT"
                
            ]
        else:
            self.contaminant_keywords = contaminant_keywords
            
        self.sample_prefix = sample_prefix
        self.peaks_data = None
        self.protein_sequences = {}
        self.peptide_df = None
        
        # Load data if provided
        if peaks_file is not None:
            self.load_peaks_data(peaks_file)
        
        if fasta_file is not None:
            self.load_protein_sequences(fasta_file)
    
    def load_peaks_data(self, file_path: str) -> pd.DataFrame:
        """
        Load peptide data from PEAKS output CSV file.
        
        Parameters:
        -----------
        file_path : str
            Path to the PEAKS output CSV file
            
        Returns:
        --------
        pd.DataFrame: Loaded data
        """
        try:
            self.peaks_data = pd.read_csv(file_path)
            console.log(f"Loaded {len(self.peaks_data)} peptide entries from {file_path}", style="bold green")
            self.peaks_data = self.peaks_data.rename(columns=lambda x: str(x).capitalize())
            # Check required columns
            required_cols = ['Peptide', 'Accession']
            missing_cols = [col for col in required_cols if col not in self.peaks_data.columns]
            
            if missing_cols:
                raise ValueError(f"Missing required columns: {', '.join(missing_cols)}")

                
            # Find intensity columns
            self.intensity_cols = [col for col in self.peaks_data.columns if col.startswith(self.sample_prefix)]
            
            if not self.intensity_cols:
                console.log(f"Warning: No columns with prefix '{self.sample_prefix}' found.", style="bold yellow")
            else:
                console.log(f"Found {len(self.intensity_cols)} intensity columns: {', '.join(self.intensity_cols)}", style="bold green")
                
            return self.peaks_data
            
        except Exception as e:
            console.log(f"Error loading PEAKS data: {str(e)}", style="bold red")
            raise
    
    def load_protein_sequences(self, fasta_path: str) -> Dict[str, str]:
        """
        Load protein sequences from a FASTA file.
        
        Parameters:
        -----------
        fasta_path : str
            Path to the FASTA file
            
        Returns:
        --------
        Dict[str, str]: Dictionary mapping protein IDs to sequences
        """
        try:
            # Parse the FASTA file
            for record in SeqIO.parse(fasta_path, "fasta"):
                # Extract the protein ID from the FASTA header
                protein_id = record.id
                # Store the sequence
                self.protein_sequences[protein_id] = str(record.seq)
                
                # Also store with description for more flexible matching
                self.protein_sequences[record.description] = str(record.seq)
            
            console.log(f"Loaded {len(self.protein_sequences)} protein sequences from {fasta_path}", style="bold green")
            return self.protein_sequences
            
        except Exception as e:
            console.log(f"Error loading protein sequences: {str(e)}", style="bold red")
            raise
    
    def is_contaminant(self, accession: str) -> bool:
        """
        Check if a protein accession belongs to a contaminant.
        
        Parameters:
        -----------
        accession : str
            Protein accession to check
            
        Returns:
        --------
        bool: True if the accession is a contaminant, False otherwise
        """
        if pd.isna(accession) or accession == "":
            return True
            
        for keyword in self.contaminant_keywords:
            if keyword.lower() in accession.lower():
                return True
        return False
        
    def remove_ptm(self, peptide: str) -> str:
        """
        Remove post-translational modifications (PTMs) from peptide sequences.
        Handles modifications like M(+15.99) and other mass shift notations.
        
        Parameters:
        -----------
        peptide : str
            Peptide sequence with PTM annotations
            
        Returns:
        --------
        str: Clean peptide sequence without PTM annotations
        """
        if peptide is None or pd.isna(peptide):
            return ""
            
        # Regular expression to match PTM patterns like M(+15.99)
        # Matches any character followed by parentheses containing +/- and numbers
        ptm_pattern = r'([A-Z])\([+\-][0-9.]+\)'
        
        # Replace each match with just the amino acid
        clean_peptide = re.sub(ptm_pattern, r'\1', peptide)
        
        return clean_peptide
    
    def extract_protein_ids(self, accession_value: str) -> List[str]:
        """
        Extract protein IDs from an accession value, which may contain multiple IDs.
        
        Parameters:
        -----------
        accession_value : str
            Accession value from the PEAKS output
            
        Returns:
        --------
        List[str]: List of protein IDs
        """
        if pd.isna(accession_value) or accession_value == "":
            return []
            
        # Split by common delimiters
        protein_ids = re.split(r'[,:;|/\s]+', accession_value)
        
        # Remove empty entries and trim whitespace
        protein_ids = [pid.strip() for pid in protein_ids if pid.strip()]
        
        return protein_ids
    
    def find_peptide_position(self, peptide: str, protein_sequence: str) -> Tuple[int, int]:
        """
        Find the start and end positions of a peptide in a protein sequence.
        Automatically removes PTMs before searching.
        
        Parameters:
        -----------
        peptide : str
            Peptide sequence (may contain PTMs)
        protein_sequence : str
            Protein sequence
                
        Returns:
        --------
        Tuple[int, int]: (start, end) positions (1-based indexing)
        """
        # Remove PTMs from the peptide sequence
        clean_peptide = self.remove_ptm(peptide)
        
        # Find the peptide in the protein sequence
        start_pos = protein_sequence.find(clean_peptide)
        
        if start_pos == -1:
            return (-1, -1)
            
        end_pos = start_pos + len(clean_peptide)
        
        # Convert to 1-based indexing
        return (start_pos + 1, end_pos)
    
    def filter_and_format_data(self, 
                               filter_contaminants: bool = True, 
                               intensity_threshold: float = 0.0,
                               min_samples: int = 1) -> pd.DataFrame:
        """
        Filter and format the PEAKS data for ImmunoViz.
        
        Parameters:
        -----------
        filter_contaminants : bool, optional
            Whether to filter out contaminants (default: True)
        intensity_threshold : float, optional
            Minimum intensity threshold (default: 0.0)
        min_samples : int, optional
            Minimum number of samples a peptide must be detected in (default: 1)
            
        Returns:
        --------
        pd.DataFrame: Formatted data for ImmunoViz
        """
        if self.peaks_data is None:
            raise ValueError("PEAKS data not loaded. Call load_peaks_data() first.")
            
        if not self.intensity_cols:
            raise ValueError(f"No intensity columns found with prefix '{self.sample_prefix}'")
            
        # Make a copy to avoid modifying the original data
        data = self.peaks_data.copy()
        
        # Capitalize the first letter of all column names
        #data.columns = [col.capitalize() for col in data.columns]
        
        # Filter out contaminants
        if filter_contaminants:
            initial_count = len(data)
            data = data[~data['Accession'].apply(self.is_contaminant)]
            console.log(f"Removed {initial_count - len(data)} contaminant entries", style="bold green")
        
        # Filter by intensity threshold and minimum samples
        if intensity_threshold > 0 or min_samples > 1:
            # Count how many samples have intensity above threshold for each peptide
            # detection_counts = (data[self.intensity_cols] > intensity_threshold).sum(axis=1)
            # Use apply to count the number of samples above the threshold for each peptide in each sample instead of sum of all samples
            detection_counts = (data[self.intensity_cols] > intensity_threshold).apply(lambda x: sum(x >= intensity_threshold), axis=1)
            initial_count = len(data)
            data = data[detection_counts >= min_samples]
            console.log(f"Removed {initial_count - len(data)} entries below intensity threshold of {intensity_threshold} or minimum sample count of {min_samples}", style="bold green")
        
        # Prepare the formatted data for ImmunoViz
        formatted_rows = []
        
        # Extract sample names from intensity columns
        sample_names = [re.sub(r'^[_\-\*]+', '', col.replace(self.sample_prefix, '')) for col in self.intensity_cols]
        
        # Process each peptide
        for _, row in data.iterrows():
            peptide = row['Peptide']
            # Get clean peptide for length calculation
            clean_peptide = self.remove_ptm(peptide)
            
            # Get all protein IDs for this peptide
            protein_ids = self.extract_protein_ids(row['Accession'])
            
            if not protein_ids:
                continue
                
            # Process each protein ID
            for protein_id in protein_ids:
                # Find the protein sequence
                protein_sequence = self.get_protein_sequence(protein_id)
                
                if protein_sequence is None:
                    # Could not find the sequence, use placeholder positions
                    start, end = 1, len(clean_peptide)
                else:
                    # Find the peptide position in the protein
                    start, end = self.find_peptide_position(peptide, protein_sequence)
                    
                    if start == -1:
                        # Peptide not found in the sequence, use placeholder positions
                        start, end = 1, len(clean_peptide)
                
                # Add an entry for each sample where the peptide was detected
                for i, col in enumerate(self.intensity_cols):
                    intensity = row[col]
                    if intensity > intensity_threshold:
                        formatted_rows.append({
                            'Peptide': peptide,
                            'CleanPeptide': clean_peptide,  # Store the clean peptide too
                            'Protein': protein_id,
                            'Start': start,
                            'End': end,
                            'Intensity': intensity,
                            'Sample': sample_names[i],
                            'Length': len(clean_peptide)  # Use clean peptide length
                        })
        
        # Create the formatted DataFrame
        self.peptide_df = pd.DataFrame(formatted_rows)
        
        console.log(f"Created formatted data with {len(self.peptide_df)} peptide-protein-sample combinations", style="bold green")
        console.log(f"PTMs were removed for position finding. Original peptides preserved in 'Peptide' column, clean versions in 'CleanPeptide' column.", style="bold yellow")
        
        return self.peptide_df
    
    def get_protein_sequence(self, protein_id: str) -> Optional[str]:
        """
        Get the sequence for a protein ID, trying different matching strategies.
        
        Parameters:
        -----------
        protein_id : str
            Protein ID to look up
            
        Returns:
        --------
        Optional[str]: Protein sequence if found, None otherwise
        """
        # Direct match
        if protein_id in self.protein_sequences:
            return self.protein_sequences[protein_id]
            
        # Try to match as a substring of FASTA headers
        for header, sequence in self.protein_sequences.items():
            if protein_id in header:
                return sequence
                
        return None
    
    def create_immunoviz_object(self) -> 'ImmunoViz':
        """
        Create an ImmunoViz object from the processed data.
        
        Returns:
        --------
        ImmunoViz: ImmunoViz object ready for visualization
        """
        if self.peptide_df is None:
            raise ValueError("Data not formatted. Call filter_and_format_data() first.")
            
        # Import ImmunoViz here to avoid circular imports
        try:
            # Assuming ImmunoViz is defined elsewhere or imported
            from ProtPeptigram.viz import ImmunoViz
            # Use a dataframe with just the columns ImmunoViz expects
            immunoviz_df = self.peptide_df[['Peptide', 'Protein', 'Start', 'End', 'Intensity', 'Sample', 'Length']].copy()
            return ImmunoViz(immunoviz_df)
        except ImportError:
            console.log("Warning: ImmunoViz class not found. Make sure it's properly imported.", style="bold yellow")
            return None
    
    def get_unique_proteins(self) -> List[str]:
        """
        Get the list of unique proteins in the processed data.
        
        Returns:
        --------
        List[str]: List of unique protein IDs
        """
        if self.peptide_df is None:
            raise ValueError("Data not formatted. Call filter_and_format_data() first.")
            
        return sorted(self.peptide_df['Protein'].unique())
    
    def get_unique_samples(self) -> List[str]:
        """
        Get the list of unique samples in the processed data.
        
        Returns:
        --------
        List[str]: List of unique sample names
        """
        if self.peptide_df is None:
            raise ValueError("Data not formatted. Call filter_and_format_data() first.")
            
        return sorted(self.peptide_df['Sample'].unique())
    
    def save_formatted_data(self, output_file: str) -> None:
        """
        Save the formatted data to a CSV file.
        
        Parameters:
        -----------
        output_file : str
            Path to the output CSV file
        """
        if self.peptide_df is None:
            raise ValueError("Data not formatted. Call filter_and_format_data() first.")
            
        self.peptide_df.to_csv(output_file, index=False)
        console.log(f"Saved formatted data to {output_file}", style="bold green")


# Example of how to use the updated class
# if __name__ == "__main__":
#     # Test the PTM removal function
#     processor = PeptideDataProcessor()
#     test_peptide = "IVS(+15.99)Y(+15.99)YDDIANSEENPTPG"
#     clean_peptide = processor.remove_ptm(test_peptide)
#     console.print(f"Original peptide: {test_peptide}")
#     print(f"Clean peptide: {clean_peptide}")
    
#     # Full example would need real data files
#     processor = PeptideDataProcessor("../data/JCI146771_Mouse_peptides_peaks_online.csv", "../data/uniprotkb_proteome_UP000000589_AND_revi_2025_03_12.fasta")
#     processor.filter_and_format_data()
#     viz = processor.create_immunoviz_object()
    