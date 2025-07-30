
# Plot benchmarking results using plottable

def add_metric_row(df):
    """
    Adds a row to a multi-index DataFrame with the first element of each tuple 
    in the multi-index as values in a new 'Metric' row, and keeps only the 
    second element of the multi-index as column headers.
    
    Parameters:
        df (pd.DataFrame): A DataFrame with a multi-index in columns.
        
    Returns:
        pd.DataFrame: Modified DataFrame with a new 'Metric' row.
    """
    import pandas as pd
    df = df.copy()
    # Extract the first and second levels of the multi-index columns
    metric_labels = [col[0] for col in df.columns]
    new_columns = [col[1] for col in df.columns]
    
    # Create a new row with the metric labels
    metric_row = pd.DataFrame([metric_labels], columns=new_columns, index=["Metric"])
    
    # Update the columns of the original DataFrame to only have the second level
    df.columns = new_columns
    
    # Concatenate the metric row at the top of the original DataFrame
    result_df = pd.concat([metric_row, df], axis=0)
    
    return result_df


def plot_benchmark_table(df, pal='PRGn', pal_agg='YlGnBu', cmap_method='norm', cmap_padding=0.05, agg_name='Aggregate score', dpi=300, save_path=None, figsize=None):
    """
    Plots a benchmarking results table using the `plottable` library.

    This function creates a formatted table displaying different benchmarking metrics 
    across various methods. It includes:
    - Circle-marked metric values.
    - Color-encoded values based on a chosen colormap.
    - Aggregate scores visualized as bar charts.

    Args:
        df (pd.DataFrame): 
            The benchmarking results DataFrame. It should have a multi-index in columns 
            where the first level represents metric categories and the second level contains 
            metric names.
        pal (str, optional): 
            Colormap for individual metric values. Defaults to `'PRGn'`.
        pal_agg (str, optional): 
            Colormap for aggregate scores. Defaults to `'YlGnBu'`.
        cmap_method (str, optional): 
            Method for normalizing colormaps. Options:
                - `'norm'`: Normalize based on standard deviation.
                - `'minmax'`: Normalize based on the min-max range.
                - `'minmax_padded'`: Adds padding to the min-max normalization.
                - `'0_to_1'`: Normalize between 0 and 1.
            Defaults to `'norm'`.
        cmap_padding (float, optional): 
            Padding factor for `minmax_padded` colormap normalization. Defaults to `0.05`.
        agg_name (str, optional): 
            The name of the aggregate score column. Defaults to `'Aggregate score'`.
        dpi (int, optional): 
            Resolution of the saved figure. Defaults to `300`.
        save_path (str, optional): 
            If provided, saves the figure to the specified path. Defaults to `None`.
        figsize (tuple, optional): 
            Figure size `(width, height)`. If `None`, it is determined dynamically based on 
            the number of columns and rows. Defaults to `None`.

    Raises:
        ValueError: If `cmap_method` is not one of `'norm'`, `'minmax'`, `'minmax_padded'`, or `'0_to_1'`.

    Returns:
        None
    """
    
    # Plot the geometry results using plotable
    from plottable import ColumnDefinition, Table
    from plottable.plots import bar
    from plottable.cmap import normed_cmap
    import matplotlib.pyplot as plt
    import matplotlib as mpl
    import pandas as pd

    df = df.copy()
    df = add_metric_row(df)
    num_embeds = df.shape[0]
    plot_df = df.drop("Metric", axis=0)
    plot_df['Method'] = plot_df.index

    cmap = mpl.cm.get_cmap(pal)
    cmap_agg = mpl.cm.get_cmap(pal_agg)
    if cmap_method == 'norm':
        cmap_fn = lambda col_data: normed_cmap(col_data, cmap=cmap, num_stds=2.5)
        cmap_agg_fn = lambda col_data: normed_cmap(col_data, cmap=cmap_agg, num_stds=2.5)
    elif cmap_method == 'minmax':
        cmap_fn = lambda col_data: mpl.cm.ScalarMappable(
            norm=mpl.colors.Normalize(vmin=col_data.min(), vmax=col_data.max()),
            cmap=cmap
        ).to_rgba
        cmap_agg_fn = lambda col_data: mpl.cm.ScalarMappable(
            norm=mpl.colors.Normalize(vmin=col_data.min(), vmax=col_data.max()),
            cmap=cmap_agg
        ).to_rgba

    elif cmap_method == 'minmax_padded':
        cmap_fn = lambda col_data: mpl.cm.ScalarMappable(
            norm=mpl.colors.Normalize(vmin=col_data.min()-cmap_padding*(col_data.max()-col_data.min()), vmax=col_data.max()+cmap_padding*(col_data.max()-col_data.min())),
            cmap=cmap
        ).to_rgba
        cmap_agg_fn = lambda col_data: mpl.cm.ScalarMappable(
            norm=mpl.colors.Normalize(vmin=col_data.min()-cmap_padding*(col_data.max()-col_data.min()), vmax=col_data.max()+cmap_padding*(col_data.max()-col_data.min())),
            cmap=cmap_agg
        ).to_rgba
    elif cmap_method == '0_to_1':
        cmap_fn = lambda col_data: mpl.cm.ScalarMappable(
            norm=mpl.colors.Normalize(vmin=0, vmax=1),
            cmap=cmap
        ).to_rgba
        cmap_agg_fn = lambda col_data: mpl.cm.ScalarMappable(
            norm=mpl.colors.Normalize(vmin=0, vmax=1),
            cmap=cmap_agg
        ).to_rgba
    else:
        raise ValueError(f"Invalid cmap_method: {cmap_method}, choose 'norm' or 'minmax'")
    
    column_definitions = [
        ColumnDefinition("Method", width=1.5, textprops={"ha": "left", "weight": "bold"}),
    ]

    aggr_cols = df.columns[df.loc['Metric'] == agg_name]
    stats_cols = df.columns[df.loc['Metric'] != agg_name]

    # Circles for the metric values
    column_definitions += [
        ColumnDefinition(
            col,
            title=col.replace(" ", "\n"),
            width=1,
            textprops={
                "ha": "center",
                "bbox": {"boxstyle": "circle", "pad": 0.1},
            },
            cmap=cmap_fn(plot_df[col]),
            group=df.loc['Metric', col],
            formatter="{:.2f}",
        )
        for i, col in enumerate(stats_cols)
    ]

    column_definitions += [
        ColumnDefinition(
            col,
            width=1,
            title=col.replace(" ", "\n", 1),
            plot_fn=bar,
            plot_kw={
                "cmap": cmap_agg_fn(plot_df[col]),
                "plot_bg_bar": False,
                "annotate": True,
                "height": 0.9,
                "formatter": "{:.2f}",
                # font size
                "textprops": {"fontsize": 12},
            },
            group=df.loc['Metric', col],
            border="left" if i == 0 else None,
        )
        for i, col in enumerate(aggr_cols)
    ]

    # Set figure size dynamically or use provided figsize
    if figsize is None:
        figsize = (len(df.columns) * 1.25, 3 + 0.3 * num_embeds)
    
    with mpl.rc_context({"svg.fonttype": "none"}):
        fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
        tab = Table(
            plot_df,
            cell_kw={
                "linewidth": 0,
                "edgecolor": "k",
            },
            column_definitions=column_definitions,
            ax=ax,
            row_dividers=True,
            footer_divider=True,
            textprops={"fontsize": 11, "ha": "center"},
            row_divider_kw={"linewidth": 1, "linestyle": (0, (0.5, 2))},
            col_label_divider_kw={"linewidth": 1, "linestyle": "-"},
            column_border_kw={"linewidth": 1, "linestyle": "-"},
            index_col="Method"
        ).autoset_fontcolors(colnames=plot_df.columns)

    if save_path:
        plt.savefig(save_path, bbox_inches="tight")
    plt.show()
