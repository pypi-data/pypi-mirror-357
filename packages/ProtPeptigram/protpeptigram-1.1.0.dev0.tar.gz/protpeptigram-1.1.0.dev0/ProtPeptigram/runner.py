from ProtPeptigram.DataProcessor import PeptideDataProcessor
from ProtPeptigram.viz import ImmunoViz
from ProtPeptigram.logger import CONSOLE as console
import os
import matplotlib.pyplot as plt
from pathlib import Path
from typing import List, Optional, Union


def select_abundant_proteins(processor, top_n=5, min_peptides=3):
    """
    Select proteins with the highest number of peptides for visualization.
    
    Parameters:
    -----------
    processor : PeptideDataProcessor
        Initialized processor with formatted data
    top_n : int
        Number of top proteins to select
    min_peptides : int
        Minimum number of peptides required for a protein to be considered
        
    Returns:
    --------
    List[str]: List of protein IDs sorted by abundance
    """
    if processor.peptide_df is None:
        raise ValueError("Data not formatted. Call filter_and_format_data() first.")
    
    # Count peptides per protein
    protein_counts = processor.peptide_df.groupby('Protein')['Peptide'].nunique().reset_index()
    protein_counts.columns = ['Protein', 'PeptideCount']
    
    # Sort by peptide count (descending)
    protein_counts = protein_counts.sort_values('PeptideCount', ascending=False)
    
    # Filter by minimum peptide count
    abundant_proteins = protein_counts[protein_counts['PeptideCount'] >= min_peptides]
    
    # Get the top N proteins
    selected_proteins = abundant_proteins.head(top_n)['Protein'].tolist()
    
    # print(f"Selected {len(selected_proteins)} proteins with highest peptide counts:")
    console.log(f"Selected {len(selected_proteins)} proteins with highest peptide counts:", style="bold")
    for protein, count in zip(selected_proteins, 
                            abundant_proteins.head(top_n)['PeptideCount']):
        console.log(f"  {protein}: {count} peptides", style="bold")
        
    
    return selected_proteins


def read_protein_list(file_path: str) -> List[str]:
    """
    Read a list of protein IDs from a file.
    
    Parameters:
    -----------
    file_path : str
        Path to the file containing protein IDs (one per line)
    
    Returns:
    --------
    List[str]: List of protein IDs
    """
    proteins = []
    try:
        with open(file_path, 'r') as f:
            for line in f:
                protein = line.strip()
                if protein:  # Skip empty lines
                    proteins.append(protein)
        return proteins
    except FileNotFoundError:
        raise FileNotFoundError(f"Protein list file not found: {file_path}")


def run_pipeline(
    csv_path: str,
    fasta_path: str,
    output_dir: Optional[str] = None,
    top: Optional[Union[int, str]] = 5,
    protein_list: Optional[str] = None,
    regex_pattern: Optional[str] = None,
    intensity_threshold: float = 0.0,
    min_samples: int = 1,
):
    """
    Run the complete peptide analysis pipeline
    
    Parameters:
    -----------
    csv_path : str
        Path to the PEAKS CSV file with peptide data
    fasta_path : str
        Path to the FASTA file with protein sequences
    output_dir : str, optional
        Directory to save output files (defaults to same directory as csv_path)
    top : int or str, optional
        Number of top proteins to visualize (default: 5)
    protein_list : str, optional
        Path to a file containing specific protein IDs to visualize
    regex_pattern : str, optional
        Regex pattern to filter protein names
    intensity_threshold : float, optional
        Intensity threshold for filtering peptides (default: 0.0)
    min_samples : int, optional
        Minimum number of samples a peptide must be present in (default: 1)
    Returns:
    --------
    tuple: (PeptideDataProcessor, ImmunoViz) - The processor and visualization objects
    """
    # Validate input arguments
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    
    if not os.path.exists(fasta_path):
        raise FileNotFoundError(f"FASTA file not found: {fasta_path}")
    
    # Convert top to int if it's a string
    if isinstance(top, str):
        try:
            top = int(top)
        except ValueError:
            raise ValueError(f"Invalid value for 'top': {top}. Must be an integer.")
    
    # Setup output directory
    if output_dir is None:
        output_dir = os.path.dirname(csv_path)
    os.makedirs(output_dir, exist_ok=True)
    
    # Read specific protein list if provided
    specific_proteins = None
    if protein_list and os.path.exists(protein_list):
        specific_proteins = read_protein_list(protein_list)
        console.print(f"Using {len(specific_proteins)} proteins from provided list.", style="bold")
    
    # 1. Initialize the data processor
    processor = PeptideDataProcessor()
    
    # 2. Load PEAKS data
    processor.load_peaks_data(csv_path)
    
    # 3. Load protein sequences from FASTA file
    processor.load_protein_sequences(fasta_path) #regex_pattern=regex_pattern)
    
    # 4. Process and format the data
    immunoviz_df = processor.filter_and_format_data(
        filter_contaminants=True,
        intensity_threshold=intensity_threshold,
        min_samples=min_samples
    )
    
    # 5. Get unique proteins and samples
    unique_proteins = processor.get_unique_proteins()
    unique_samples = processor.get_unique_samples()
    
    console.log(f"Number of unique proteins: {len(unique_proteins)}", style="bold green")
    console.log(f"Unique samples: {unique_samples}", style="bold")
    # print(f"Unique samples: {unique_samples}")
    
    # 6. Create ImmunoViz object
    viz = ImmunoViz(immunoviz_df)
    
    # 7. Determine proteins to visualize
    if specific_proteins:
        # Filter to ensure proteins exist in the data
        proteins_to_visualize = [p for p in specific_proteins if p in unique_proteins]
        if len(proteins_to_visualize) == 0:
            console.print("Warning: None of the specified proteins were found in the data.")
            # Fall back to top proteins if specified proteins not found
            proteins_to_visualize = select_abundant_proteins(processor, top_n=top, min_peptides=3)
    else:
        # Use top proteins by peptide count
        proteins_to_visualize = select_abundant_proteins(processor, top_n=top, min_peptides=3)
    
    # 8. Create visualizations for each protein
    output_files = []
    for prot in proteins_to_visualize:
        try:
            fig, _ = viz.plot_peptigram(
                [prot],
                group_by='Sample',
                color_by='protein',
                figsize=(14, 12),
                title=f"Peptide-Protein alignment visualisation - {prot}",
                color_by_protein_and_intensity=False,
                intensity_cmaps=["Blues", "Reds", "Greens", "Purples"],
                protein_cmap="Set1", 
                external_legend=True,
                highlight=True,
                auto_highlight=True,
                highlight_alpha=0.3,
                use_sample_color_bars=True,
                sample_bar_width=6,
                dpi=120
            )
            
            # Save the figure
            output_file = os.path.join(output_dir, f"prot-peptigram_{prot}.png")
            fig.savefig(output_file, dpi=300, bbox_inches='tight')
            plt.close(fig)
            output_files.append(output_file)
            console.log(f"PeptiGram for {prot} saved to {output_file}", style="bold")
        except Exception as e:
            print(f"Error generating visualization for protein {prot}: {str(e)}")
    
    # Also save a CSV with the processed data
    output_csv = os.path.join(output_dir, "processed_peptides_prot-peptigram.csv")
    immunoviz_df.to_csv(output_csv, index=False)
    console.log(f"Processed peptide data saved to {output_csv}", style="bold")
    
    return processor, viz, output_files