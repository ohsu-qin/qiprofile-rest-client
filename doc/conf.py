import os
import sys
import qiprofile_rest_client

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.intersphinx', 'sphinx.ext.todo']
autoclass_content = "both"
autodoc_default_flags= ['members', 'show-inheritance']
source_suffix = '.rst'
master_doc = 'index'
project = u'qiprofile-rest-client'
copyright = u'2015, OHSU Knight Cancer Institute'
pygments_style = 'sphinx'
htmlhelp_basename = 'qiprofilerestclientdoc'
html_title = "qiprofile-rest-client"

def skip(app, what, name, obj, skip, options):
    return False if name == "__init__" else skip


def setup(app):
    app.connect("autodoc-skip-member", skip)
