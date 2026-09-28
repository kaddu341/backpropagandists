"""myst-nb notebook reader that renders images pasted into markdown cells.

Jupyter stores a pasted image as a cell attachment (`![x](attachment:x.png)`),
which myst-nb cannot resolve. This reader swaps each one for a data: URI.
"""

import nbformat


def read_ipynb(text):
    nb = nbformat.reads(text, as_version=4)
    for cell in nb.cells:
        for name, bundle in cell.pop("attachments", {}).items():
            mime, data = next(iter(bundle.items()))  # Jupyter stores one mime type per paste
            cell.source = cell.source.replace(f"attachment:{name}", f"data:{mime};base64,{data}")
    return nb
