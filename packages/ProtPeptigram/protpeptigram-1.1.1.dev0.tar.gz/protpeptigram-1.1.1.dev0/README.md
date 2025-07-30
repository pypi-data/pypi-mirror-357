# ProtPeptigram

[![CI/CD](https://github.com/Sanpme66/ProtPeptigram/actions/workflows/python-package.yml/badge.svg)](https://github.com/Sanpme66/ProtPeptigram/actions/workflows/python-package.yml)
[![Cross-Platform](https://github.com/Sanpme66/ProtPeptigram/actions/workflows/cross-platform-metrics.yml/badge.svg)](https://github.com/Sanpme66/ProtPeptigram/actions/workflows/cross-platform-metrics.yml)
[![PyPI version](https://badge.fury.io/py/protpeptigram.svg)](https://pypi.org/project/protpeptigram/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
<!-- [![Downloads](https://static.pepy.tech/badge/protpeptigram)](https://pepy.tech/project/protpeptigram) -->

## Visualization of Immunopeptides Mapped to Source Proteins Across Multiple Samples

ProtPeptigram provides a comprehensive visualization platform for mapping immunopeptides to their source proteins across different biological samples. This tool can enables to identify peptide coverage patterns, analyze density distributions, and compare peptide presentations between experimental conditions.

<p align="center">
  <img src="https://github.com/Sanpme66/ProtPeptigram/blob/main/example/prot-peptigram_P60710.png" alt="ProtPeptigram Visualization Example" width="700"/>
</p>

## Features

- **Intuitive Peptide Visualization**: Map peptides to their source proteins with detailed positional information
- **Multi-Sample Support**: Compare peptide presentation across different experimental conditions
- **Intensity-Based Coloring**: Visualize peptide abundance with customizable color schemes
- **Automatic Highlighting**: Identify regions of interest with dense peptide coverage
- **Publication-Quality Outputs**: Generate high-resolution figures suitable for scientific publications
- **Customizable Visualizations**: Adjust color schemes, highlighting, and display options to suit your needs

## Installation

### From PyPI (Recommended)

```bash
pip install protpeptigram
```

### From TestPyPI

```bash
pip install -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ protpeptigram
```

### From Source

```bash
git clone https://github.com/Sanpme66/ProtPeptigram.git
cd ProtPeptigram
pip install -e .
```

## Requirements

- Python ≥ 3.8
- pandas
- matplotlib
- numpy
- Biopython
- rich

## Quick Start

### Command Line Usage

```bash
# Basic usage with minimal options
protpeptigram -i data/peptides.csv -f data/proteome.fasta -o output_directory

# Specify top 10 proteins by peptide count
protpeptigram -i data/peptides.csv -f data/proteome.fasta -o output_dir -tp 10

# Visualize specific proteins
protpeptigram -i data/peptides.csv -f data/proteome.fasta -o output_dir -pl protein_list.txt

# Apply intensity threshold
protpeptigram -i data/peptides.csv -f data/proteome.fasta -o output_dir -th 1000
```

### Python API Usage

```python
from ProtPeptigram.DataProcessor import PeptideDataProcessor
from ProtPeptigram.viz import ImmunoViz

# Initialize data processor
processor = PeptideDataProcessor()

# Load data
processor.load_peaks_data("data/peptides.csv")
processor.load_protein_sequences("data/proteome.fasta")

# Process data
formatted_data = processor.filter_and_format_data(
    filter_contaminants=True,
    intensity_threshold=1000,
    min_samples=2
)

# Create visualizations
viz = ImmunoViz(formatted_data)
fig, _ = viz.plot_peptigram(
    protein_ids=["P20152", "P32261"],
    group_by="Sample",
    color_by="protein",
    title="HLA Peptide Visualization"
)

# Save visualization
fig.savefig("protein_visualization.png", dpi=300, bbox_inches="tight")
```

## Running on Google Colab

You can quickly try out ProtPeptigram on Google Colab without installing anything locally. Click the link below to open the example notebook:

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Sanpme66/ProtPeptigram/blob/main/example/example.ipynb)


## Documentation

For detailed documentation including API reference, tutorials, and examples:

- [API Documentation](https://github.com/Sanpme66/ProtPeptigram/tree/main/docs)
- [Tutorial](https://github.com/Sanpme66/ProtPeptigram/tree/main/docs/tutorial.md)
- [Example Gallery](https://github.com/Sanpme66/ProtPeptigram/tree/main/docs/examples)

## Input Data Format

ProtPeptigram accepts peptide data in CSV format from PEAKS software with the following columns:
- Peptide sequence
- Protein accession
- Intensity values for each sample

For protein sequences, standard FASTA format files are supported.

## Citation

If you use ProtPeptigram in your research, please cite:

```
Krishna S, Li C, et al. (2024). ProtPeptigram: Visualization tool for mapping peptides to source proteins.
bioRxiv. https://www.monash.edu/research/compomics/
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Developed at Li Lab/Purcell Lab, Monash University, Australia
- Inspired by the need for better visualization tools in immunopeptidomics research

## Contact

Sanjay Krishna - [GitHub](https://github.com/Sanpme66)

Project Link: [https://github.com/Sanpme66/ProtPeptigram](https://github.com/Sanpme66/ProtPeptigram)