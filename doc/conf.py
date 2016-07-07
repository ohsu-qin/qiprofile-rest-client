import os
import sys
import qirest_client

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.intersphinx', 'sphinx.ext.todo']
autoclass_content = "both"
autodoc_default_flags= ['members', 'show-inheritance']
source_suffix = '.rst'
master_doc = 'index'
project = u'qirest-client'
copyright = u'2015, OHSU Knight Cancer Institute. This software is not intended for clinical use'
pygments_style = 'sphinx'
htmlhelp_basename = 'qirestclientdoc'
html_title = "qirest-client"

def skip(app, what, name, obj, skip, options):
    return False if name == "__init__" else skip


def setup(app):
    app.connect("autodoc-skip-member", skip)
