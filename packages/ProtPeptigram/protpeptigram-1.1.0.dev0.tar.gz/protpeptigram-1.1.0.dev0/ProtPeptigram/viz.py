import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import matplotlib.patheffects as path_effects
from typing import List, Dict, Union, Tuple, Optional
import os


class ImmunoViz:
    """
    A visualization tool for immunopeptide data from mass spectrometry results.
    Enhanced version with sequential colormaps and advanced visualization options.
    """

    def __init__(self, peptide_data: pd.DataFrame):
        """
        Initialize the ImmunoViz object with peptide data.

        Parameters:
        -----------
        peptide_data : pd.DataFrame
            DataFrame containing peptide information with columns:
            - Peptide: sequence of the peptide
            - Protein: protein identifier
            - Start: start position in the protein
            - End: end position in the protein
            - Intensity: intensity value from mass spec
            - Sample: sample identifier
        """
        self.peptide_data = peptide_data.copy()

        # Set default visualization parameters
        self.font_family = "Arial"
        plt.rcParams["font.family"] = self.font_family

        # Nature journal inspired color palette for proteins
        self.protein_colors = [
            "#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8172B3",  # Main colors
            "#937860", "#DA8BC3", "#8C8C8C", "#CCB974", "#64B5CD"   # Secondary colors
        ]

    # Update the plot_peptigram method with these improvements
    def plot_peptigram(
        self,
        protein_ids: Union[str, List[str]],
        groups: List[str] = None,
        group_by: str = 'Sample',
        color_by: str = None,
        figsize: Tuple[int, int] = (12, 10),
        title: Optional[str] = None,
        y_desnity_forntsize: int = 8,
        y_desnity_forntcolour: str = "#333333",
        y_lab_ticksize: int = 8,
        y_sample_fontsize: int = 8,
        y_sample_color: Optional[Union[list, str]] = "#333333",
        max_sample_name_length: int = 15,
        sample_name_wrap: bool = True,
        use_sample_color_bars: bool = False,
        sample_colors: Optional[List[str]] = None,
        sample_bar_width: float = 0.5,
        x_lab_forntsize: int = 12,
        xticks_font: int = 12,
        xticks_color: str = "#333333",
        xticks_rotation: int = 0,
        annotate: bool = True,
        legend_titleFontsize: int = 10,
        legend_fontsize: int = 8,
        min_intensity: Optional[float] = None,
        highlight_regions: Optional[List[Tuple[int, int]]] = None,
        auto_highlight: bool = True,
        auto_highlight_window: int = 10,
        auto_highlight_threshold: float = 0.8,
        highlight: bool = True,
        color_by_protein_and_intensity: bool = False,
        colour_by_text: bool = False,
        intensity_color_scale: float = 0.7,
        intensity_cmaps: Union[str, List[str]] = "viridis",
        protein_cmap: str = "tab10",
        external_legend: bool = True,
        highlight_alpha: float = 0.25,
        highlight_color: str = "#FF8888",
        dpi: int = 300
    ) -> Tuple[plt.Figure, List[plt.Axes]]:
        """
        Create a PeptiGram visualization with protein-based coloring.

        Parameters:
        -----------
        protein_ids : str or List[str]
            Protein identifier(s) to visualize
        groups : List[str], optional
            List of group names to include (if None, all groups are included)
        group_by : str, optional
            Column name to group samples by (default: 'Sample')
        color_by : str, optional
            How to color peptides: 'intensity', 'count', 'length', or 'protein' (default: 'protein')
        figsize : Tuple[int, int], optional
            Figure size (width, height) in inches (default: (12, 10))
        title : str, optional
            Title for the plot (default: "Protein Peptide Coverage")
        x_lab_fontsize : int, optional
            Font size for x-axis labels Amino acid positions(default: 12)
        y_desnity_forntsize : int, optional
            Font size for y-axis labels Density plot(default: 8)
        y_desnity_forntcolour : str, optional   
            Color for y-axis labels Density plot (default: "#333333")
        y_sample_color : str
            Color for y-axis sample names (default: "#333333")
        y_lab_ticksize : int, optional
            Font size for y-axis tick labels (default: 8)
        y_sample_fontsize : int, optional
            Font size for y-axis sample names (default: 8)
        max_sample_name_length : int, optional
            Maximum length for sample names on the y-axis (default: 8)
        sample_name_wrap : bool, optional
            Whether to wrap long sample names (default: True)
        use_sample_color_bars : bool, optional
            Whether to use colored bars for sample names (default: False)
        sample_colors : List[str], optional
            List of colors for sample bars (if None, default colors are used)
        sample_bar_width : float, optional
            Width of sample color bars (default: 0.02)
        x_lab_forntsize : int, optional
            Font size for x-axis labels (default: 12)
        xticks_font : int, optional
            Font size for x-axis tick labels (default: 12)
        xticks_color : str, optional
            Color for x-axis tick labels (default: "#333333")
        x_ticks_rotation : int, optional
            Rotation angle for x-axis tick labels (default: 0)
        annotate : bool, optional
            Whether to annotate proteins (default: True)
        min_intensity : float, optional
            Minimum intensity threshold (default: None)
        highlight_regions : List[Tuple[int, int]], optional
            List of (start, end) regions to highlight in the protein
        auto_highlight : bool, optional
            Whether to automatically highlight high density regions if no regions are provided (default: True)
        auto_highlight_window : int, optional
            Window size for density smoothing when auto-highlighting (default: 10)
        auto_highlight_threshold : float, optional
            Threshold for density to be considered high (as a fraction of max density) (default: 0.8)
        highlight : bool, optional
            Whether to apply highlighting at all (default: True)
        color_by_protein_and_intensity : bool, optional
            Whether to color peptides by both protein and intensity (default: False)
        colour_by_text : bool, optional
            Whether to add text indicating the coloring method (default: False)
        intensity_color_scale : float, optional
            How much the intensity should influence the color (0.0-1.0) (default: 0.7)
        intensity_cmaps : str or List[str], optional
            Colormaps for intensity visualization for each protein (default: "viridis")
            If a string is provided, the same colormap is used for all proteins
            If a list is provided, each protein gets its own colormap from the list
            Options include: "viridis", "plasma", "inferno", "magma", "cividis",
            "Blues", "Greens", "Reds", "Purples", "Oranges", "YlOrBr", "YlGnBu", etc.
        protein_cmap : str, optional
            Colormap for protein visualization (default: "tab10")
            Options: "tab10", "tab20", "Pastel1", "Pastel2", "Set1", "Set2", "Set3"
        external_legend : bool, optional
            Whether to place the legend outside the main plot (default: True)
        highlight_alpha : float, optional
            Alpha value for highlighted regions (default: 0.25)
        highlight_color : str, optional
            Color for highlighted regions (default: "#FF8888")
        dpi : int, optional
            DPI for the figure (default: 100)
        """

        # Convert single protein ID to list
        if isinstance(protein_ids, str):
            protein_ids = [protein_ids]

        # Filter data for the selected proteins
        data = self.peptide_data[self.peptide_data['Protein'].isin(
            protein_ids)].copy()

        if data.empty:
            print(f"No data found for proteins {protein_ids}")
            return

        # Apply intensity threshold if specified
        if min_intensity is not None:
            data = data[data['Intensity'] >= min_intensity]

        # Group peptides by their sequence
        peptide_groups = data.groupby(['Peptide', 'Protein', 'Start', 'End']).agg({
            'Intensity': ['mean', 'std', 'count'],
            group_by: lambda x: list(set(x))
        }).reset_index()

        peptide_groups.columns = ['Peptide', 'Protein', 'Start',
                                  'End', 'Mean_Intensity', 'Std_Intensity', 'Count', 'Groups']

        # Determine groups to plot
        if groups is None:
            all_groups = []
            for g in peptide_groups['Groups']:
                all_groups.extend(g)
            groups = sorted(list(set(all_groups)))

        # Configure styling for publication-quality
        plt.style.use('default')
        plt.rcParams['font.family'] = 'sans-serif'
        plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']
        plt.rcParams['axes.linewidth'] = 0.8
        plt.rcParams['xtick.major.width'] = 0.8
        plt.rcParams['ytick.major.width'] = 0.8
        plt.rcParams['xtick.direction'] = 'out'
        plt.rcParams['ytick.direction'] = 'out'

        # Set colors and style elements
        grid_color = '#e5e5e5'         # Very light gray grid
        separator_color = '#cccccc'    # Light gray separator
        background_color = '#ffffff'   # White background
        text_color = '#333333'         # Dark gray for text

        # Get proper colormaps
        try:
            protein_colormap = plt.cm.get_cmap(protein_cmap)
        except:
            # Default to tab10 if specified cmap doesn't exist
            protein_colormap = plt.cm.get_cmap('tab10')

        # Create map of proteins to colors
        protein_to_color = {}
        for i, protein in enumerate(protein_ids):
            color_idx = i % protein_colormap.N
            protein_to_color[protein] = protein_colormap(color_idx)

        # Set up available sequential colormaps
        sequential_cmaps = [
            "viridis", "plasma", "inferno", "magma", "cividis",
            "Blues", "Greens", "Reds", "Purples", "Oranges",
            "YlOrBr", "YlOrRd", "OrRd", "PuRd", "RdPu",
            "BuPu", "GnBu", "PuBu", "YlGnBu", "PuBuGn",
            "BuGn", "YlGn"
        ]

        # Set up intensity colormaps for each protein
        intensity_cmap_dict = {}

        # Handle the case where intensity_cmaps is a list
        if isinstance(intensity_cmaps, list):
            for i, protein_id in enumerate(protein_ids):
                # Get an intensity colormap for this protein
                cmap_idx = i % len(intensity_cmaps)
                cmap_name = intensity_cmaps[cmap_idx]

                # Ensure the colormap exists
                if cmap_name in sequential_cmaps or cmap_name in plt.colormaps():
                    intensity_cmap_dict[protein_id] = plt.cm.get_cmap(
                        cmap_name)
                else:
                    # Fallback to a default sequential colormap
                    fallback_idx = i % len(sequential_cmaps)
                    intensity_cmap_dict[protein_id] = plt.cm.get_cmap(
                        sequential_cmaps[fallback_idx])
        else:
            # If a single colormap is provided, use it for all proteins
            try:
                # Try to get the specified colormap
                cmap = plt.cm.get_cmap(intensity_cmaps)
                for protein_id in protein_ids:
                    intensity_cmap_dict[protein_id] = cmap
            except:
                # If it doesn't exist, assign a different sequential colormap to each protein
                for i, protein_id in enumerate(protein_ids):
                    cmap_idx = i % len(sequential_cmaps)
                    intensity_cmap_dict[protein_id] = plt.cm.get_cmap(
                        sequential_cmaps[cmap_idx])

        # Set up figure with padding for external legend
        legend_width = 0.2 if external_legend else 0

        # Adjust figure size
        fig_width = figsize[0] + (figsize[0] * legend_width)
        fig_height = figsize[1]

        # Create figure
        n_groups = len(groups)
        fig = plt.figure(figsize=(fig_width, fig_height))

        # Define grid layout with space for legend
        if external_legend:
            gs = fig.add_gridspec(
                n_groups + 1, 2, width_ratios=[0.85, 0.15], height_ratios=[1] + [3] * n_groups)
            main_axes = []
            legend_axes = []

            # Create main plot axes
            for i in range(n_groups + 1):
                main_axes.append(fig.add_subplot(gs[i, 0]))
                if i > 0:  # Don't share x for the first axis (density plot)
                    main_axes[i].sharex(main_axes[0])

            # Create legend axes
            legend_ax = fig.add_subplot(gs[0, 1])
            legend_ax.axis('off')
        else:
            gs = fig.add_gridspec(
                n_groups + 1, 1, height_ratios=[1] + [3] * n_groups)
            main_axes = []

            # Create main plot axes
            for i in range(n_groups + 1):
                main_axes.append(fig.add_subplot(gs[i, 0]))
                if i > 0:  # Don't share x for the first axis (density plot)
                    main_axes[i].sharex(main_axes[0])

        axs = main_axes

        # Calculate limits
        min_start = int(peptide_groups['Start'].min())
        max_end = int(peptide_groups['End'].max())
        xlim = (min_start - 10, max_end + 10)

        # Set up the figure with proper styling
        for ax in axs:
            ax.set_facecolor(background_color)
            ax.grid(False)
            ax.tick_params(colors=text_color)
            for spine in ax.spines.values():
                spine.set_color(grid_color)

        # Initialize density profiles for each protein
        all_proteins_density = np.zeros(max_end - min_start + 1)
        protein_densities = {}

        # Plot protein overview at the top
        for protein_id in protein_ids:
            protein_peptides = peptide_groups[peptide_groups['Protein'] == protein_id]

            if protein_peptides.empty:
                continue

            # Create density profile for this protein
            positions = np.arange(min_start, max_end + 1)
            density = np.zeros(len(positions))

            for _, peptide in protein_peptides.iterrows():
                start, end = int(peptide['Start']), int(peptide['End'])
                if start < min_start:
                    start = min_start
                if end > max_end:
                    end = max_end
                idx_start = start - min_start
                idx_end = end - min_start
                if idx_start < len(density) and idx_end <= len(density):
                    density[idx_start:idx_end] += 1

            # Store density for this protein
            protein_densities[protein_id] = density
            # Add to combined density
            all_proteins_density += density

            # Get color for this protein
            protein_color = protein_to_color[protein_id]

            # Plot density with high quality styling
            axs[0].bar(positions, density, color=protein_color, alpha=0.75, width=1,
                       label=protein_id, edgecolor=None, linewidth=0)

            # Add elegant protein annotation
            if annotate and np.max(density) > 0:
                max_pos = np.argmax(density) + min_start
                axs[0].annotate(protein_id, xy=(max_pos, np.max(density)),
                                xytext=(0, 5), textcoords='offset points',
                                ha='center', va='bottom', fontsize=8,
                                bbox=dict(boxstyle="round,pad=0.2",
                                          fc=background_color, ec='none', alpha=0.8),
                                color=text_color, weight='normal')

        # Auto-detect high density regions if requested
        auto_regions = []
        if highlight and auto_highlight and highlight_regions is None:
            # Apply smoothing to the density
            smoothed_density = self._smooth_density(
                all_proteins_density, window_size=auto_highlight_window)
            threshold = np.max(smoothed_density) * auto_highlight_threshold

            # Find regions above threshold
            high_density_regions = self._find_high_density_regions(
                smoothed_density, threshold, min_start)

            # Apply highlighting for auto-detected regions
            if high_density_regions:
                auto_regions = high_density_regions
                highlight_regions = high_density_regions

        # Styling for the top panel
        axs[0].set_xlim(xlim)
        axs[0].set_ylabel('Density', color=y_desnity_forntcolour,
                          fontweight='normal', fontsize=y_desnity_forntsize)
        axs[0].spines['top'].set_visible(False)
        axs[0].spines['right'].set_visible(False)
        # Remove all ticks
        # axs[0].set_yticks([])

        # Instead of removing all ticks, set them appropriately
        max_density = max(all_proteins_density)
        axs[0].set_yticks([0, max_density/2, max_density])
        axs[0].set_yticklabels(
            [0, f"{max_density/2:.0f}", f"{max_density:.0f}"], fontsize=y_lab_ticksize, color="lightgray")

        # Create legend in the designated area if external
        if external_legend:
            # Create protein legend handles
            legend_handles = []
            for protein_id in protein_ids:
                patch = plt.Line2D(
                    [0], [0], color=protein_to_color[protein_id], lw=4, label=protein_id)
                legend_handles.append(patch)
                # Add legend to the separate legend axis
                protein_legend = legend_ax.legend(
                    handles=legend_handles,
                    loc='upper left',
                    fontsize=legend_fontsize,
                    frameon=True,
                    framealpha=0.7,
                    facecolor=background_color,
                    edgecolor=grid_color,
                    title='Protein',
                    title_fontsize=legend_titleFontsize
                )
                protein_legend.get_title().set_fontweight('bold')
        else:
            # Create protein legend in the main plot
            protein_legend = axs[0].legend(
                loc='upper right',
                fontsize=legend_fontsize,
                framealpha=0.7,
                facecolor=background_color,
                edgecolor='none',
                title='Proteins',
                title_fontsize=legend_titleFontsize,
            )
            # Set the font weight of the legend title to normal for a consistent appearance
            protein_legend.get_title().set_fontweight('normal')

        # Add subtle grid lines
        axs[0].grid(axis='x', linestyle=':', alpha=0.2, color=grid_color)

        # Highlight auto-detected regions in top panel with improved visibility
        if highlight and highlight_regions:
            for start, end in highlight_regions:
                # Make highlight more visible in top density panel
                axs[0].axvspan(start, end, alpha=highlight_alpha, color=highlight_color,
                               edgecolor=None, linewidth=0)

                # Add subtle lines to mark the region boundaries
                axs[0].axvline(start, color=highlight_color,
                               linestyle='-', alpha=0.3, linewidth=0.8)
                axs[0].axvline(end, color=highlight_color,
                               linestyle='-', alpha=0.3, linewidth=0.8)

        # Find global min/max intensity for consistent colormap normalization
        min_intensity_val = min_intensity if min_intensity is not None else peptide_groups['Mean_Intensity'].min(
        )
        max_intensity_val = peptide_groups['Mean_Intensity'].max()

        # Create normalizations per protein to ensure consistent coloring
        protein_intensity_norms = {}
        for protein_id in protein_ids:
            protein_data = peptide_groups[peptide_groups['Protein']
                                          == protein_id]
            if not protein_data.empty:
                protein_min = min_intensity if min_intensity is not None else protein_data['Mean_Intensity'].min(
                )
                protein_max = protein_data['Mean_Intensity'].max()
                protein_intensity_norms[protein_id] = plt.Normalize(
                    protein_min, protein_max)

        # Plot peptides by group
        for i, group in enumerate(groups):
            ax = axs[i + 1]

            # Filter peptides for this group
            group_peptides = peptide_groups[peptide_groups['Groups'].apply(
                lambda x: group in x)]

            if group_peptides.empty:
                ax.set_visible(False)
                continue

            # group_peptides['Length'] = group_peptides['End'] - group_peptides['Start']
            group_peptides.loc[:, 'Length'] = group_peptides['End'] - \
                group_peptides['Start']

            # Calculate maximum height needed
            max_height = self._calculate_plot_height(group_peptides, xlim)

            # Initialize space tracking array
            spaces = np.zeros((max_height, int(xlim[1] - xlim[0] + 1)))

            # Sort peptides by start position and length
            group_peptides = group_peptides.sort_values(
                ['Start', 'End'], ascending=[True, False])

            # Plot each peptide
            for idx, peptide in group_peptides.iterrows():
                start = int(peptide['Start'])
                end = int(peptide['End'])
                protein_id = peptide['Protein']

                # Get base color for this protein
                base_color = protein_to_color[protein_id]
                final_color = base_color

                # Apply coloring based on selection
                if color_by_protein_and_intensity:
                    # Get intensity value and normalize using per-protein normalization
                    intensity_val = peptide['Mean_Intensity']

                    # Get normalization for this protein
                    if protein_id in protein_intensity_norms:
                        norm = protein_intensity_norms[protein_id]
                        intensity_normalized = norm(intensity_val)
                    else:
                        # Fallback to global normalization
                        intensity_normalized = plt.Normalize(
                            min_intensity_val, max_intensity_val)(intensity_val)

                    # Get the appropriate colormap for this protein
                    intensity_cmap = intensity_cmap_dict[protein_id]

                    # Get color from the protein's intensity colormap
                    if intensity_normalized < 0:
                        intensity_normalized = 0
                    elif intensity_normalized > 1:
                        intensity_normalized = 1

                    final_color = intensity_cmap(intensity_normalized)

                elif color_by == 'intensity':
                    intensity_val = peptide['Mean_Intensity']

                    # Use per-protein normalization and colormap
                    if protein_id in protein_intensity_norms:
                        norm = protein_intensity_norms[protein_id]
                        intensity_normalized = norm(intensity_val)
                    else:
                        # Fallback to global normalization
                        intensity_normalized = plt.Normalize(
                            min_intensity_val, max_intensity_val)(intensity_val)

                    # Use the protein's assigned colormap
                    intensity_cmap = intensity_cmap_dict[protein_id]
                    final_color = intensity_cmap(intensity_normalized)

                elif color_by == 'count':
                    count_val = peptide['Count']
                    count_normalized = plt.Normalize(
                        1, group_peptides['Count'].max())(count_val)
                    final_color = plt.cm.Blues(count_normalized)

                elif color_by == 'length':
                    length_val = peptide['End'] - peptide['Start']
                    length_normalized = plt.Normalize(
                        group_peptides['Length'].min(), group_peptides['Length'].max())(length_val)
                    final_color = plt.cm.Greens(length_normalized)

                # Find available space for this peptide
                for height in range(max_height):
                    if start < xlim[0]:
                        start = xlim[0]
                    if end > xlim[1]:
                        end = xlim[1]

                    space_start = max(0, start - xlim[0])
                    space_end = min(end - xlim[0], xlim[1] - xlim[0])

                    if space_start >= spaces.shape[1] or space_end >= spaces.shape[1]:
                        continue

                    space_needed = spaces[height, space_start:space_end+1]
                    if np.sum(space_needed) == 0:  # Space is available
                        spaces[height, space_start:space_end+1] = 1
                        #peptide visualization
                        ax.plot(
                            [start, end],
                            [-height-0.4, -height-0.4],
                            linewidth=2.5,
                            solid_capstyle='round',
                            color=final_color,
                            alpha=0.95,
                            path_effects=[
                                path_effects.withStroke(
                                    linewidth=3.0,
                                    foreground=(0, 0, 0, 0.2),
                                    alpha=0.3
                                )
                            ]
                        )
                        break

            # Set plot limits and labels
            ax.set_ylim(-max_height, 0)
            ax.set_xlim(xlim)
            
            # Add colored vertical bar for each sample if requested
            if use_sample_color_bars:
                if sample_colors is None:
                    # Generate colors automatically
                    sample_cmap = plt.cm.get_cmap('tab10')
                    sample_color = sample_cmap(i % sample_cmap.N)
                else:
                    sample_color = sample_colors[i % len(sample_colors)]
                
                # Add vertical colored bar on the left
                bar_x = xlim[0] #-5 # Position slightly left of the plot
                ax.axvline(bar_x, ymin=0, ymax=1, color=sample_color, 
                        linewidth=sample_bar_width, alpha=0.8, solid_capstyle='butt')
                
                # Remove y-axis label if using color bars
                ax.set_ylabel('')
                
                # Store sample info for legend
                if i == 0:  # Initialize on first iteration
                    sample_legend_handles = []
                
                # Create legend handle
                sample_legend_handles.append(
                    plt.Line2D([0], [0], color=sample_color, lw=4, label=group)
                )
                        # Add styled group label - ensure it's visible and consistent
            elif sample_name_wrap and len(group) > max_sample_name_length:
                # Calculate wrap width based on max_height
                # More height = more space = wider wrap width
                import textwrap
                
                # Base wrap width, adjusted by plot height
                # Higher max_height allows longer lines
                dynamic_wrap_width = max(8, min(max_sample_name_length, max_height // 2))
                
                wrapped_group = '\n'.join(textwrap.wrap(group, width=dynamic_wrap_width))
                ax.set_ylabel(wrapped_group, fontweight='normal',
                            color=y_sample_color, fontsize=y_sample_fontsize)
            
            else:
                ax.set_ylabel(group, fontweight='normal',
                            color=y_sample_color, fontsize=y_sample_fontsize)
                    # Add subtitle for coloring method
            coloring_method = ""
            if color_by_protein_and_intensity:
                coloring_method = "Colored by protein and intensity"
            elif color_by is None:
                coloring_method = None
            elif color_by == 'intensity':
                coloring_method = "Colored by intensity"
            elif color_by == 'protein':
                coloring_method = "Colored by protein"
            elif color_by == 'count':
                coloring_method = "Colored by detection count"
            elif color_by == 'length':
                coloring_method = "Colored by peptide length"
            

            
            # Set Sample color bar legend if using sample color bars
            if use_sample_color_bars and external_legend:
                # Calculate scaling factor based on plot height
                height_scale_factor = len(groups) / 6.0  # Normalize to 6 groups as baseline
                height_scale_factor = max(0.5, min(height_scale_factor, 2.0))  # Clamp between 0.5 and 2.0
                
                # Calculate space needed for protein legend, scaled by plot height
                base_item_height = 1 * height_scale_factor  # Scale item height
                base_title_padding = 0.06 * height_scale_factor  # Scale title/padding
                
                protein_legend_height = len(protein_ids) * base_item_height + base_title_padding
                
                # Position sample legend below protein legend with scaled padding
                padding = 0.3 * height_scale_factor
                sample_legend_y = 1.0 - protein_legend_height - padding
                
                # Ensure sample legend doesn't go below available space
                # sample_legend_y = max(sample_legend_y, 0.1)
                
                # Create sample legend with calculated position
                sample_legend = legend_ax.legend(
                    handles=sample_legend_handles,
                    bbox_to_anchor=(0, sample_legend_y),
                    loc='upper left',
                    fontsize=legend_fontsize,
                    frameon=True,
                    framealpha=0.7,
                    facecolor=background_color,
                    edgecolor=grid_color,
                    title='Samples',
                    title_fontsize=legend_titleFontsize
                )
                sample_legend.get_title().set_fontweight('bold')
                
                # Add the protein legend back (since matplotlib replaces it)
                legend_ax.add_artist(protein_legend)
                
                # Add notes below sample legend
                sample_items = len(groups)
                sample_legend_height = sample_items * base_item_height + base_title_padding
                current_note_y = sample_legend_y - sample_legend_height - 0.03  # Start position for notes
                
                # Prepare notes list
                notes = []
                
                # Add coloring method note if enabled
                if coloring_method and colour_by_text:
                    notes.append(f"Coloring: {coloring_method}")
                
                # Add auto-detected regions note if applicable
                if auto_regions and len(auto_regions) > 0:
                    regions_str = ", ".join([f"{start}-{end}" for start, end in auto_regions])
                    notes.append(f"High density regions: {regions_str}")
                
                # Add all notes
                for i, note in enumerate(notes):
                    note_y_pos = current_note_y - (i * 0.04)  # Space between notes
                    
                    # Ensure note doesn't go below available space
                    # note_y_pos = max(note_y_pos, 0.02)
                    
                    # Determine color for the note
                    note_color = highlight_color if "High density regions" in note else text_color
                    
                    # Add the note text
                    legend_ax.text(0.0, note_y_pos, f"Note: {note}", 
                                transform=legend_ax.transAxes,
                                fontsize=legend_fontsize-1, 
                                fontstyle='italic',
                                color=note_color,
                                ha='left', va='top',
                                wrap=True)
        
            # Set y-ticks and labels    
            ax.set_yticks([])
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_visible(False)

            # Add subtle grid lines
            ax.grid(axis='x', linestyle=':', alpha=0.15, color=grid_color)

            # Add separator line
            ax.axhline(0, color=separator_color, linestyle=':', alpha=0.4,
                       linewidth=0.8, dash_capstyle='round')

            # Highlight regions if specified and highlighting is enabled
            if highlight and highlight_regions:
                for start, end in highlight_regions:
                    # Apply highlighting with improved visibility
                    ax.axvspan(start, end, alpha=highlight_alpha, color=highlight_color,
                               edgecolor=None, linewidth=0)

                    # Add subtle boundary lines
                    ax.axvline(start, color=highlight_color,
                               linestyle='-', alpha=0.3, linewidth=0.8)
                    ax.axvline(end, color=highlight_color,
                               linestyle='-', alpha=0.3, linewidth=0.8)
        # Set title
        if title is None:
            if len(protein_ids) == 1:
                title = f"Peptide Coverage: {protein_ids[0]}"
            else:
                title = f"Protein Peptide Coverage Analysis"

        plt.suptitle(title, fontsize=14, y=0.98,
                     fontweight='bold', color=text_color)

        # Add subtitle if multiple proteins
        if len(protein_ids) > 1:
            protein_str = ", ".join(protein_ids)
            if len(protein_str) > 50:  # Truncate if too long
                protein_str = protein_str[:47] + "..."
            plt.figtext(0.5, 0.94, protein_str, ha='center', color=text_color,
                        fontsize=9, fontstyle='italic')
            
        if use_sample_color_bars == False:
            if coloring_method and colour_by_text:
                y_pos = 0.92 if len(protein_ids) <= 1 else 0.90
                plt.figtext(0.5, y_pos, coloring_method, ha='center', color=text_color,
                            fontsize=9, fontstyle='italic')

            # Add subtitle for auto-detected regions if applicable
            if auto_regions and len(auto_regions) > 0:
                regions_str = ", ".join(
                    [f"{start}-{end}" for start, end in auto_regions])
                y_pos = 0.90 if len(
                    protein_ids) <= 1 and not coloring_method else 0.88
                plt.figtext(0.5, y_pos, f"High density regions: {regions_str}",
                            ha='center', fontsize=9, fontstyle='italic', color=highlight_color)

        # Handle x-tick labels for all axes except the last one
        for i in range(len(axs)):
            # if i == 0:  # Density plot - keep labels
            #     continue
            if i == len(axs) - 1:  # Last plot - keep labels
                axs[i].tick_params(axis='x', labelsize=xticks_font, rotation=xticks_rotation, labelcolor=xticks_color)
            else:  # Middle plots - hide labels
                axs[i].tick_params(axis='x', labelbottom=False)
        
        
        # Set x-label on the bottom axis only
        axs[-1].set_xlabel('Amino Acid Position',
                           fontweight='normal', color=text_color, fontsize=x_lab_forntsize)

        # Add intensity colorbars for each protein if using protein+intensity
        if color_by_protein_and_intensity and external_legend:
            # Calculate how much space each colorbar needs
            colorbar_height = 0.7 / len(protein_ids)
            colorbar_padding = 0.02

            for i, protein_id in enumerate(protein_ids):
                if protein_id not in protein_intensity_norms:
                    continue

                # Calculate position for this colorbar
                bottom_position = 0.75 - \
                    (i * (colorbar_height + colorbar_padding))
                position = [0.88, bottom_position, 0.03, colorbar_height]

                # Create axes for the colorbar
                cax = fig.add_axes(position)

                # Get the appropriate colormap and normalization
                cmap = intensity_cmap_dict[protein_id]
                norm = protein_intensity_norms[protein_id]

                # Create colorbar
                sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
                sm.set_array([])
                cbar = plt.colorbar(sm, cax=cax)

                # Add the protein ID as the label
                cbar.set_label(f'{protein_id}', fontweight='bold', fontsize=8)
                cbar.ax.tick_params(labelsize=7)

        # Add a label for the intensity legend
        if color_by_protein_and_intensity and external_legend:
            legend_label_ypos = 0.85
            legend_ax.text(0.5, legend_label_ypos, 'Intensity Scales',
                           horizontalalignment='center', verticalalignment='center',
                           transform=legend_ax.transAxes, fontsize=10, fontweight='bold')

        # Apply final layout adjustments
        plt.tight_layout()
        plt.subplots_adjust(hspace=0.05, top=0.9)

        # Set DPI for higher quality
        fig.set_dpi(dpi)

        return fig, axs

    def _calculate_plot_height(self, peptide_data: pd.DataFrame, xlim: Tuple[int, int]) -> int:
        """
        Calculate the required height for plotting peptides without overlap.
        """
        # Sort peptides by start position and length
        peptides = peptide_data.sort_values(
            ['Start', 'Length'], ascending=[True, False])

        # Initialize space tracking array
        spaces = np.zeros((100, int(xlim[1] - xlim[0] + 1)))
        max_height = 0

        # Track required height
        for _, peptide in peptides.iterrows():
            start = int(peptide['Start'])
            end = int(peptide['End'])

            # Skip peptides outside plot range
            if end < xlim[0] or start > xlim[1]:
                continue

            # Adjust to plot coordinates
            plot_start = max(0, start - xlim[0])
            plot_end = min(end - xlim[0], xlim[1] - xlim[0])

            # Find available space
            placed = False
            for height in range(spaces.shape[0]):
                if height > max_height:
                    max_height = height

                if plot_start >= spaces.shape[1] or plot_end >= spaces.shape[1]:
                    continue

                space_needed = spaces[height, plot_start:plot_end+1]
                if np.sum(space_needed) == 0:  # Space is available
                    spaces[height, plot_start:plot_end+1] = 1
                    placed = True
                    break

            # If no space found, we need more height
            if not placed:
                max_height = spaces.shape[0]

        return max_height + 1  # Add 1 for padding

    def _adjust_color(self, color, value):
        """
        Adjust color based on intensity value.
        """
        # Convert string colors to RGB
        if isinstance(color, str):
            color = plt.matplotlib.colors.to_rgba(color)

        # For darker values, maintain more of the original color but adjust brightness
        r, g, b, a = color

        # Adjust color based on value while preserving hue
        if value < 0.5:
            # Darken
            factor = 0.5 + value
            r = r * factor
            g = g * factor
            b = b * factor
        else:
            # Lighten
            factor = value - 0.5
            r = r + (1 - r) * factor
            g = g + (1 - g) * factor
            b = b + (1 - b) * factor

        return (r, g, b, a)

    def _adjust_color_by_intensity(self, color, intensity, scale_factor=0.7):
        """
        Adjust color by intensity while preserving the protein's base color.
        Enhanced version for better visibility of intensity differences.

        Parameters:
        -----------
        color : tuple or str
            Base color to adjust
        intensity : float (0-1)
            Normalized intensity value
        scale_factor : float (0-1)
            How much the intensity should influence the color (default: 0.7)
            Higher values make intensity differences more pronounced

        Returns:
        --------
        tuple: (r, g, b, a) color
        """
        # Convert string colors to RGB
        if isinstance(color, str):
            color = plt.matplotlib.colors.to_rgba(color)

        r, g, b, a = color

        # Enhanced color adjustment:
        # For low intensity (0-0.5), darken the color significantly
        # For high intensity (0.5-1.0), brighten and increase saturation

        if intensity < 0.5:
            # Map 0-0.5 to 0.1-0.5 (avoid going completely black)
            mapped_intensity = 0.1 + intensity * 0.8
            # Apply non-linear darkening for better differentiation
            factor = mapped_intensity ** (1.5 * scale_factor)

            # Preserve hue but reduce brightness
            new_r = r * factor
            new_g = g * factor
            new_b = b * factor
        else:
            # Map 0.5-1.0 to 0.5-1.2 (allow some brightening beyond original)
            mapped_intensity = 0.5 + (intensity - 0.5) * 1.4

            # For high intensity: preserve or increase saturation while brightening
            # Find dominant color channel to preserve hue
            max_channel = max(r, g, b)
            if max_channel == 0:
                # If color is black, just use gray scale
                new_r = new_g = new_b = mapped_intensity
            else:
                # Calculate how much to brighten each channel
                factor = mapped_intensity / max_channel

                # Brighten proportionally to preserve hue
                new_r = min(1, r * factor * (1 + scale_factor * 0.5))
                new_g = min(1, g * factor * (1 + scale_factor * 0.5))
                new_b = min(1, b * factor * (1 + scale_factor * 0.5))

        # Ensure values stay in valid range
        new_r = max(0, min(1, new_r))
        new_g = max(0, min(1, new_g))
        new_b = max(0, min(1, new_b))

        return (new_r, new_g, new_b, a)

    def _smooth_density(self, density, window_size=10):
        """
        Apply smoothing to density array for better peak detection.

        Parameters:
        -----------
        density : np.ndarray
            Density array to smooth
        window_size : int, optional
            Size of the smoothing window (default: 10)

        Returns:
        --------
        np.ndarray: Smoothed density
        """
        # Create simple moving average smoothing
        kernel = np.ones(window_size) / window_size
        smoothed = np.convolve(density, kernel, mode='same')

        # Handle edge effects by replacing edges with original values
        half_window = window_size // 2
        smoothed[:half_window] = density[:half_window]
        smoothed[-half_window:] = density[-half_window:]

        return smoothed

    def _find_high_density_regions(self, density, threshold, min_start, min_region_size=5, max_gap=3):
        """
        Find regions with high peptide density.

        Parameters:
        -----------
        density : np.ndarray
            Density array (smoothed)
        threshold : float
            Threshold value for high density
        min_start : int
            Minimum starting position (for coordinate adjustment)
        min_region_size : int, optional
            Minimum size of a region to be considered (default: 5)
        max_gap : int, optional
            Maximum gap between high density points to be considered same region (default: 3)

        Returns:
        --------
        List[Tuple[int, int]]: List of (start, end) high density regions
        """
        # Find positions above threshold
        high_density_positions = np.where(density >= threshold)[0]

        if len(high_density_positions) == 0:
            return []

        # Group positions into contiguous regions
        regions = []
        current_region_start = high_density_positions[0]
        prev_pos = high_density_positions[0]

        for pos in high_density_positions[1:]:
            # If there's a gap larger than max_gap, end the current region
            if pos - prev_pos > max_gap:
                if prev_pos - current_region_start + 1 >= min_region_size:
                    regions.append(
                        (current_region_start + min_start, prev_pos + min_start + 1))
                current_region_start = pos
            prev_pos = pos

        # Add the last region if it meets minimum size
        if prev_pos - current_region_start + 1 >= min_region_size:
            regions.append((current_region_start + min_start,
                           prev_pos + min_start + 1))

        # Merge overlapping regions
        if len(regions) > 1:
            regions.sort()
            merged_regions = [regions[0]]

            for current in regions[1:]:
                previous = merged_regions[-1]
                if current[0] <= previous[1]:
                    # Regions overlap, merge them
                    merged_regions[-1] = (previous[0],
                                          max(previous[1], current[1]))
                else:
                    # No overlap, add as new region
                    merged_regions.append(current)

            regions = merged_regions

        return regions

    def export_peptogram(self, protein_ids: Union[str, List[str]], output_file: str, **kwargs):
        """
        Create and save a PeptiGram visualization to a file.
        """
        fig, _ = self.plot_peptigram(protein_ids, **kwargs)
        fig.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close(fig)
        print(f"PeptiGram saved to {output_file}")
