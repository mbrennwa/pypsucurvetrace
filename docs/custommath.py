from docutils import nodes
from docutils.parsers.rst import roles

def custommath_role(role, rawtext, text, lineno, inliner, options={}, content=[]):
    # Replace 'CUSTOM_SYMBOL' with your desired LaTeX expression
    latex = r'\(\text{{CUSTOM\_SYMBOL}}\)'  # Use double backslashes for backslashes
    node = nodes.raw(rawtext, latex, format='latex')
    return [node], []

def setup(app):
    app.add_role('custommath', custommath_role)

