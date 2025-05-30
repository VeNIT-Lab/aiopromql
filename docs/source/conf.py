import os
import sys

sys.path.insert(0, os.path.abspath("../.."))


def linkcode_resolve(domain, info):
    if domain != "py" or not info["module"]:
        return None
    filename = info["module"].replace(".", "/")
    return f"https://github.com/VeNIT-Lab/aiopromql/blob/main/{filename}.py"


project = "aiopromql"
copyright = "2025, VeNIT Lab"
author = "Ozay Tokgozlu"

# The full version, including alpha/beta/rc tags
release = "0.1.1"

# Add any Sphinx extension module names here, as strings
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "sphinx_autodoc_typehints",
    "sphinx.ext.linkcode",
    "myst_parser",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = []

# The theme to use for HTML and HTML Help pages
html_theme = "sphinx_rtd_theme"
html_theme_options = {
    "display_version": True,
    "navigation_depth": 4,
    "prev_next_buttons_location": "bottom",
    "style_external_links": True,
    "logo_only": False,
}

html_context = {
    "display_github": True,
    "github_user": "VeNIT-Lab",
    "github_repo": "aiopromql",
    "github_version": "main",
    "conf_py_path": "/docs/source/",
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]
templates_path = ["_templates"]
# Intersphinx mapping
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "httpx": ("https://www.python-httpx.org/", None),
    "pydantic": ("https://docs.pydantic.dev/latest/", None),
}

# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = True
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = True
napoleon_use_ivar = True
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_type_aliases = None
