from pathlib import Path
import matplotlib.pyplot as plt
from pandas.api.types import is_datetime64_any_dtype, is_numeric_dtype
import numpy as np
import pandas as pd
from IPython.display import HTML
import base64
from typing import Dict, Any

def _is_categorical(x: pd.Series, num_unique: int, max_level: int) -> bool:
    return (x.dtype == 'category' or
            x.dtype == 'object' or
            (x.dtype in ['int', 'float'] and num_unique <= max_level))

def encode_img_base64(img: Path) -> str:
    with open(img, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    return f"data:image/png;base64, {encoded_string}"

def _graph_cat_col(stats: pd.Series, filename: Path, figsize: tuple) -> str:
    fig, ax = plt.subplots(figsize=figsize)
    pct = stats / stats.sum()
    ax.barh(pct.index, pct, color='gray', alpha=0.3, edgecolor='black')
    ax.invert_yaxis()
    ax.set_xlim(0, 1)
    ax.axis('off')
    fig.savefig(filename, bbox_inches='tight', pad_inches=0, transparent=True)
    plt.close(fig)
    return f'<img src="{encode_img_base64(filename)}"></img>'

def _graph_num_col(x: pd.Series, filename: Path, figsize: tuple) -> str:
    fig, ax = plt.subplots(figsize=figsize)
    ax.hist(x.dropna(), bins=10, color='gray', edgecolor='black', alpha=0.3)
    ax.axis('off')
    fig.savefig(filename, bbox_inches='tight', pad_inches=0, transparent=True)
    plt.close(fig)
    return f'<img src="{encode_img_base64(filename)}"></img>'

def _graph_date_col(x: pd.Series, filename: Path, figsize: tuple) -> str:
    freqs = (x - x.min()).dt.days
    fig, ax = plt.subplots(figsize=figsize)
    ax.hist(freqs, bins=10, color='gray', alpha=0.3, ec='black')
    ax.axis('off')
    fig.savefig(filename, bbox_inches='tight', pad_inches=0, transparent=True)
    plt.close(fig)
    return f'<img src="{encode_img_base64(filename)}"></img>'

def _stats_date_col(x: pd.Series, show_graph: bool, filename: Path) -> Dict[str, Any]:
    stats = f"Min: {x.min().strftime('%Y-%m-%d')}<br>"
    stats += f"Max: {x.max().strftime('%Y-%m-%d')}<br>"
    stats += f"Duration: {(x.max() - x.min()).days:,} days"
    freqs = f"{x.nunique()} distinct values"
    out = {'Stats / Values': stats, 'Freqs / (% of Valid)': freqs}
    if show_graph:
        out['Graph'] = _graph_date_col(x, filename, figsize=(2, 1))
    return out

def _stats_cat_col(x: pd.Series, max_level: int, show_graph: bool, filename: Path, max_str_len: int = 30) -> Dict[str, Any]:
    stats = x.astype(str).value_counts()
    total = stats.sum()
    values = [f'{i+1}. {v[:max_str_len]}' for i, v in enumerate(stats.index[:max_level])]
    freqs = stats[:max_level].map(lambda i: f"{i:,} ({i/total:.1%})")
    
    if len(stats) > max_level:
        values.append(f'{max_level + 1}. other')
        other_sum = stats[max_level:].sum()
        freqs = freqs.tolist() + [f"{other_sum:,} ({other_sum/total:.1%})"]
        stats = pd.concat([stats.head(max_level), pd.Series({'other': other_sum})])
    
    out = {
        'Stats / Values': '<br>'.join(values),
        'Freqs / (% of Valid)': '<br>'.join(freqs)
    }
    if show_graph:
        out['Graph'] = _graph_cat_col(stats, filename, figsize=(2, 0.3 * len(stats)))
    return out

def _stats_num_col(x: pd.Series, show_graph: bool, filename: Path) -> Dict[str, Any]:
    stats = f"Mean (sd) : {x.mean():.1f} ({x.std():.1f})"
    stats += f"<br>min < med < max:"
    stats += f"<br>{x.min():.1f} < {x.median():.1f} < {x.max():.1f}"
    stats += f"<br>IQR (CV) : {x.quantile(0.75) - x.quantile(0.25):.1f} ({x.std() / x.mean():.1f})"
    values = f"{x.nunique():,} distinct values"
    out = {'Stats / Values': stats, 'Freqs / (% of Valid)': values}
    if show_graph:
        out['Graph'] = _graph_num_col(x, filename, figsize=(2, 1))
    return out

def _summarize_col(series: pd.Series, max_level: int = 10, tbl_name: str = 'df', i: int = 0,
                   show_graph: bool = True, tmp_dir: Path = Path('./tmp')) -> Dict[str, Any]:
    filename = tmp_dir / f'{tbl_name}_{i:03d}.png'
    num_uniq = series.nunique()
    
    if _is_categorical(series, num_uniq, max_level):
        return _stats_cat_col(series, max_level, show_graph, filename)
    elif is_datetime64_any_dtype(series):
        return _stats_date_col(series, show_graph, filename)
    elif series.dtype == bool:
        return _stats_cat_col(series, max_level, show_graph, filename)
    elif is_numeric_dtype(series):
        return _stats_num_col(series, show_graph, filename)
    else:
        return {'Stats / Values': f'Unsupported dtype {series.dtype}'}

def _get_stats(data: pd.DataFrame, max_level: int, tbl_name: str, show_graph: bool, tmp_dir: Path) -> list:
    return [_summarize_col(data[v], max_level, tbl_name, i, show_graph, tmp_dir) 
            for i, v in enumerate(data.columns)]
