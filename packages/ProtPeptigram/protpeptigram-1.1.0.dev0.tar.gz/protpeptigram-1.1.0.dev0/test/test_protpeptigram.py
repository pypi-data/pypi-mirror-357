import unittest
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import tempfile
import shutil

from ProtPeptigram.DataProcessor import PeptideDataProcessor
from ProtPeptigram.viz import ImmunoViz
from ProtPeptigram.runner import run_pipeline, select_abundant_proteins

class TestPeptideDataProcessor(unittest.TestCase):
    """Test cases for the PeptideDataProcessor class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.processor = PeptideDataProcessor()
        
        # Create path to test data files
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.peaks_file = os.path.join(current_dir, "data", "JCI146771_Mouse_peptides_peaks_online.csv")
        self.fasta_file = os.path.join(current_dir, "data", "uniprotkb_proteome_UP000000589_AND_revi_2025_03_12.fasta")
        
        # Create temp directory for outputs
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up after tests"""
        # Remove temp directory
        shutil.rmtree(self.temp_dir)
    
    def test_load_peaks_data(self):
        """Test loading data from PEAKS output file"""
        # Test data loading
        self.processor.load_peaks_data(self.peaks_file)
        self.assertIsNotNone(self.processor.peaks_data)
        self.assertGreater(len(self.processor.peaks_data), 0)
    
    def test_load_protein_sequences(self):
        """Test loading protein sequences from FASTA file"""
        self.processor.load_protein_sequences(self.fasta_file)
        self.assertIsNotNone(self.processor.protein_sequences)
        self.assertGreater(len(self.processor.protein_sequences), 0)
    
    def test_filter_and_format_data(self):
        """Test filtering and formatting peptide data"""
        # Load data first
        self.processor.load_peaks_data(self.peaks_file)
        self.processor.load_protein_sequences(self.fasta_file)
        
        # Test formatting
        formatted_df = self.processor.filter_and_format_data(
            filter_contaminants=True,
            intensity_threshold=0.0,
            min_samples=1
        )
        
        self.assertIsNotNone(formatted_df)
        self.assertGreater(len(formatted_df), 0)
        
        # Check if required columns are present
        required_columns = ['Peptide', 'Protein', 'Start', 'End', 'Sample', 'Intensity']
        for col in required_columns:
            self.assertIn(col, formatted_df.columns)
    
    def test_get_unique_proteins(self):
        """Test retrieving unique proteins from processed data"""
        # Prepare data
        self.processor.load_peaks_data(self.peaks_file)
        self.processor.load_protein_sequences(self.fasta_file)
        self.processor.filter_and_format_data()
        
        # Test unique protein retrieval
        proteins = self.processor.get_unique_proteins()
        self.assertIsNotNone(proteins)
        self.assertIsInstance(proteins, list)
        self.assertGreater(len(proteins), 0)
    
    def test_get_unique_samples(self):
        """Test retrieving unique samples from processed data"""
        # Prepare data
        self.processor.load_peaks_data(self.peaks_file)
        self.processor.load_protein_sequences(self.fasta_file)
        self.processor.filter_and_format_data()
        
        # Test unique sample retrieval
        samples = self.processor.get_unique_samples()
        self.assertIsNotNone(samples)
        self.assertIsInstance(samples, list)
        self.assertGreater(len(samples), 0)


class TestImmunoViz(unittest.TestCase):
    """Test cases for the ImmunoViz class"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create sample data for testing
        self.test_data = pd.DataFrame({
            'Peptide': ['AAAPEPTIDE', 'BBPEPTIDE', 'CCPEPTIDE'],
            'Protein': ['P12345', 'P12345', 'P67890'],
            'Start': [10, 30, 50],
            'End': [20, 40, 60],
            'Sample': ['Sample1', 'Sample2', 'Sample1'],
            'Intensity': [1000, 2000, 3000]
        })
        
        # Create ImmunoViz instance
        self.viz = ImmunoViz(self.test_data)
        
        # Create temp directory for outputs
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up after tests"""
        # Remove temp directory
        shutil.rmtree(self.temp_dir)
        plt.close('all')
    
    def test_init(self):
        """Test initialization of ImmunoViz object"""
        self.assertIsNotNone(self.viz)
        self.assertIsNotNone(self.viz.peptide_data)
        self.assertEqual(len(self.viz.peptide_data), len(self.test_data))
    
    def test_plot_peptigram_single_protein(self):
        """Test plotting peptide visualization for a single protein"""
        # Test visualization with a single protein
        fig, axs = self.viz.plot_peptigram('P12345')
        
        self.assertIsNotNone(fig)
        self.assertIsNotNone(axs)
        
        # Check created figure properties
        self.assertEqual(len(axs), 3)  # Density plot + 2 sample plots
    
    def test_plot_peptigram_multiple_proteins(self):
        """Test plotting peptide visualization for multiple proteins"""
        # Test visualization with multiple proteins
        fig, axs = self.viz.plot_peptigram(['P12345', 'P67890'])
        
        self.assertIsNotNone(fig)
        self.assertIsNotNone(axs)
    
    def test_export_peptogram(self):
        """Test exporting peptide visualization to a file"""
        # Test exporting to a file
        output_file = os.path.join(self.temp_dir, "test_peptogram.png")
        self.viz.export_peptogram('P12345', output_file)
        
        # Check if file was created
        self.assertTrue(os.path.exists(output_file))
        self.assertTrue(os.path.getsize(output_file) > 0)


class TestRunner(unittest.TestCase):
    """Test cases for the runner module functions"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create path to test data files
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.peaks_file = os.path.join(current_dir, "data", "JCI146771_Mouse_peptides_peaks_online.csv")
        self.fasta_file = os.path.join(current_dir, "data", "uniprotkb_proteome_UP000000589_AND_revi_2025_03_12.fasta")
        
        # Create a processor for testing select_abundant_proteins
        self.processor = PeptideDataProcessor()
        self.processor.load_peaks_data(self.peaks_file)
        self.processor.load_protein_sequences(self.fasta_file)
        self.processor.filter_and_format_data()
        
        # Create temp directory for outputs
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up after tests"""
        # Remove temp directory
        shutil.rmtree(self.temp_dir)
    
    def test_select_abundant_proteins(self):
        """Test selection of proteins with highest peptide counts"""
        # Test protein selection
        proteins = select_abundant_proteins(self.processor, top_n=3, min_peptides=2)
        
        self.assertIsNotNone(proteins)
        self.assertIsInstance(proteins, list)
        self.assertEqual(len(proteins), 3)
        
        # Make sure we got the proteins with highest peptide counts
        protein_counts = self.processor.peptide_df.groupby('Protein')['Peptide'].nunique()
        top_proteins = protein_counts.sort_values(ascending=False).head(3).index.tolist()
        self.assertEqual(set(proteins), set(top_proteins))
    
    def test_run_pipeline(self):
        """Test the complete analysis pipeline"""
        # Test running the pipeline
        output_dir = os.path.join(self.temp_dir, "pipeline_output")
        
        processor, viz, output_files = run_pipeline(
            csv_path=self.peaks_file,
            fasta_path=self.fasta_file,
            output_dir=output_dir,
            top=2
        )
        
        # Check if pipeline ran successfully
        self.assertIsNotNone(processor)
        self.assertIsNotNone(viz)
        self.assertIsNotNone(output_files)
        
        # Check if output files were created
        self.assertEqual(len(output_files), 2)  # Should have 2 protein visualizations
        for file in output_files:
            self.assertTrue(os.path.exists(file))
            self.assertTrue(os.path.getsize(file) > 0)
        
        # Check if CSV output was created
        csv_file = os.path.join(output_dir, "processed_peptides_prot-peptigram.csv")
        self.assertTrue(os.path.exists(csv_file))
        self.assertTrue(os.path.getsize(csv_file) > 0)


if __name__ == '__main__':
    unittest.main()