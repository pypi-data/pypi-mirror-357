""" Peptigram: mapping peptide to source protein"""

import argparse
import sys
from multiprocessing import Pool
from rich.text import Text
from rich_argparse import RichHelpFormatter
from ProtPeptigram.logger import CONSOLE as console
from ProtPeptigram import __author__, __version__
from ProtPeptigram.runner import run_pipeline


def _welcome():
    """Display application banner."""

    tool_icon = r"""
    ____             __        ____             __  _                          
   / __ \_________  / /_      / __ \___  ____  / /_(_)___ __________ _____ ___ 
  / /_/ / ___/ __ \/ __/_____/ /_/ / _ \/ __ \/ __/ / __ `/ ___/ __ `/ __ `__ \
 / ____/ /  / /_/ / /_/_____/ ____/  __/ /_/ / /_/ / /_/ / /  / /_/ / / / / / /
/_/   /_/   \____/\__/     /_/    \___/ .___/\__/_/\__, /_/   \__,_/_/ /_/ /_/ 
                                     /_/          /____/                                                                                                                                
    """

    console.print(tool_icon, style="blue")
    


def _print_credits(credits=False):
    """Print software credits to terminal."""
    text = Text()
    text.append("\n")
    if credits:
        text.append("Please cite: \n", style="bold")
        text.append(
            "GibbsCluster - 2.0 (Simultaneous alignment and clustering of peptide data)\n",
            style="bold link https://services.healthtech.dtu.dk/services/GibbsCluster-2.0/",
        )
        text.append(
            "Seq2Logo - 2.0 (Visualization of amino acid binding motifs)\n",
            style="bold link https://services.healthtech.dtu.dk/services/Seq2Logo-2.0/",
        )
        text.append(
            "MHC Motif Atlas (MHC motif PSM matrics are genrated using mhcmotifatlas please cite [link])\n\n",
            style="bold link http://mhcmotifatlas.org/home",
        )
    else:
        text.append(
            "Prot-Petigram", style="bold link https://www.monash.edu/research/compomics/"
        )
        text.append(f" (v{__version__})\n", style="bold")
    if credits:
        text.append(
            "HLA motif finder pipeline for identifying peptide motif immunopeptididomic data.\n",
            style="italic",
        )
    text.append("Developed at Li Lab / Purcell Lab, Monash University, Australia.\n")
    text.append("Please cite: ")
    if credits:
        text.append(
            "Sanjay Krishna, Nathon Craft & Chen Li et al. bioRxiv (2024)",
            style="link https://www.monash.edu/research/compomics/",
        )
    else:
        text.append(
            "Sanjay Krishna & Chen Li et al. bioRxiv (2024)",
            style="ttps://www.monash.edu/research/compomics/",
        )
    text.append("\n")
    if credits:
        text.stylize("#006cb5")
    console.print(text)
    

def main():
    """Main function to parse CLI arguments and execute the pipeline."""
    _welcome()
    _print_credits()
    parser = argparse.ArgumentParser(
        description="Prot-Petigram: Mapping peptides to source protein 🧬🧬🧬.",
        formatter_class=lambda prog: RichHelpFormatter(prog, max_help_position=42),
    )

    parser.add_argument(
        "-i",
        "--input",
        type=str,
        help="input path csv file from peaks output"
    )
    
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="output dir path to save the processed data"
    )
    parser.add_argument(
        "-f",
        "--fasta",
        type=str,
        help="fasta file containing protein sequences"
    )
    parser.add_argument(
        "-r",
        "--regex",
        type=str,
        help=r"regex pattern to filter protein names. e.g., '(\W+\d+)\|' to extract protein names from Uniprot IDs"
    )
    
    parser.add_argument(
        "-th",
        "--threshold",
        type=float,
        default=0.0,
        help="intensity threshold for filtering peptides"
    )
    
    parser.add_argument(
        "-ms",
        "--min-samples",
        type=int,
        default=1,
        help="minimum number of samples a peptide must be present in"
    )
    
    parser.add_argument(
        "-pl",
        "--protein_list",
        type=str,
        help="path to a text file containing a list of protein IDs to filter"
    )
    
    parser.add_argument(
        "-tp",
        "--top",
        type=str,
        default=5,
        help="fasta file containing protein sequences"
    )
    
    parser.add_argument(
        "-t",
        "--threads",
        type=int,
        default=1,
        help="Number of threads to use for processing (default: 1)"
    )

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"Prot-Petigram v{__version__}"
    )
    
    parser.add_argument(
        "-c",
        "--credits",
        action="store_true",
        help="Print software credits"
    )
    
    args = parser.parse_args()
    if args.credits:
        _print_credits(credits=True)
        sys.exit(0)
    
    if args.input and args.fasta:
        if args.threads > 1:
            console.log(
                f"Using {args.threads} threads for processing.",
                style="bold green"
            )
            with Pool(processes=args.threads) as pool:
                pool.apply_async(
                    run_pipeline,
                    args=(
                        args.input,
                        args.fasta,
                        args.output,
                        args.top,
                        args.protein_list,
                        args.regex,
                        args.threshold,
                        args.min_samples
                    )
                )
                pool.close()
                pool.join()
        else:
            console.log("Running in single-threaded mode.", style="bold yellow")
            run_pipeline(
                args.input,
                args.fasta,
                args.output,
                args.top,
                args.protein_list,
                args.regex,
                args.threshold,
                args.min_samples
            )
    else:
        parser.error("Both input CSV file (-i/--input) and FASTA file (-f/--fasta) are required.")
    
    


if __name__ == "__main__":
    main()