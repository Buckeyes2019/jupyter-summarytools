import pandas as pd
import numpy as np
from pathlib import Path
from IPython.display import HTML
from concurrent.futures import ProcessPoolExecutor
from .summarytools import _summarize_col
from .htmlwidgets import collapsible

def get_stats(df: pd.DataFrame, num_proc: int, max_level: int = 10, tbl_name: str = 'df', show_graph: bool = True, tmp_dir: str = './tmp') -> list:
    tmp_dir = Path(tmp_dir)
    tmp_dir.mkdir(exist_ok=True, parents=True)
    
    data = [(df[col], max_level, tbl_name, i, show_graph, tmp_dir) for i, col in enumerate(df.columns)]
    
    with ProcessPoolExecutor(max_workers=num_proc) as executor:
        results = list(executor.map(_summarize_col, *zip(*data)))
    
    return results

def dfSummary(data: pd.DataFrame, max_level: int = 10, show_graph: bool = True, tmp_dir: str = './tmp', is_collapsible: bool = False, num_proc: int = 1) -> pd.io.formats.style.Styler:
    """
    Generate HTML data summary.

    Args:
        data (pd.DataFrame): Input dataframe
        max_level (int, optional): Max level of categorical variable to be shown. Defaults to 10.
        show_graph (bool, optional): Flag to show Graph column. Defaults to True.
        tmp_dir (str, optional): Directory for temporary images. Defaults to './tmp'.
        is_collapsible (bool, optional): Flag for collapsible page. Defaults to False.
        num_proc (int, optional): Number of processes to use for parallel computation. Defaults to 1.

    Returns:
        pd.io.formats.style.Styler: Styled DataFrame if is_collapsible = False
        HTML: HTML object if is_collapsible = True

    Examples:
    ```
    from summarytools import dfSummary
    import pandas as pd
    data = pd.read_csv('./your-data-path.csv')
    # default summary view
    dfSummary(data)
    # collapsible summary
    dfSummary(data, is_collapsible=True)
    # tabbed summary
    from summarytools import tabset
    tab1 = dfSummary(data).to_html()
    tabset({'tab1': tab1})
    ```
    """
    tbl_name = data.name if hasattr(data, 'name') else 'df'
    tbl_dups = f"Duplicates: {data.duplicated().sum():,}"
    tbl_dims = f"Dimensions: {data.shape[0]:,} x {data.shape[1]:,}"
    tbl_caption = f"<strong>Data Frame Summary</strong><br>{tbl_name}<br>{tbl_dims}<br>{tbl_dups}"

    variable = data.columns.astype(str)
    variable = [f'<strong>{i}</strong><br>[{dtype}]' for i, dtype in zip(variable, data.dtypes.astype(str))]
    out = pd.DataFrame({
        'No': np.arange(1, data.shape[1] + 1),
        'Variable': variable
    })

    stats = get_stats(data, num_proc, max_level, tbl_name, show_graph, tmp_dir)
    out = pd.concat([out, pd.DataFrame(stats)], axis=1)

    missing = data.isna().sum()
    missing_pct = data.isna().mean()
    out['Missing'] = [f'{m:,}<br>({p:.1%})' for m, p in zip(missing, missing_pct)]

    styled_out = (out.style
        .set_properties(**{
            'text-align': 'left',
            'font-size': '12px',
            'vertical-align': 'middle'
        })
        .set_table_styles([{'selector': 'thead>tr>th', 'props': 'text-align: left'}])
        .set_properties(subset=['No'], **{'width': '5%', 'max-width': '50px', 'min-width': '20px'})
        .set_properties(subset=['Variable'], **{'width': '15%', 'max-width': '200px', 'min-width': '100px', 'word-break': 'break-word'})
        .set_properties(subset=['Stats / Values'], **{'width': '30%', 'min-width': '100px'})
        .set_properties(subset=['Freqs / (% of Valid)'], **{'width': '25%', 'min-width': '100px'})
        .set_properties(subset=['Missing'], width='10%')
        .hide(axis='index')
        .set_caption(tbl_caption))

    if show_graph:
        styled_out = styled_out.set_properties(subset=['Graph'], **{'width': '20%', 'min-width': '150px'})

    if is_collapsible:
        html_out = styled_out.to_html()
        html_out = collapsible(html_out, tbl_name)
        return HTML(html_out)

    return styled_out
