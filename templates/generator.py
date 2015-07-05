#!/usr/bin/env python

"""
generator.py

This module defines a series of functions to create static html pages
from the given templates in this folder.

"""

import sys
from string import Template

template_files = {
    'PAGE': 'content.html',
    'FOOT': 'footer.html',
    'HEAD': 'header.html',
    'NAV' : 'navigation.html',
    'DATE': 'post_date.html',
}

templates = {}

def load_text_file (filename):
    with open (filename, "r") as f:
        return f.read()

for template_type, template_file in template_files.items():
    templates[template_type] = Template(load_text_file(template_file))

def generate_post (page_title, page_subtitle, page_desc, post_date, bg_image, bg_image_source, article):
    """Convert the post metadata and article contents into a static html string"""

    heading    = templates['HEAD'].safe_substitute(title=page_title, description=page_desc, docroot='..')
    posting    = templates['DATE'].safe_substitute(post_date=post_date)
    navigation = templates['NAV'].safe_substitute()
    footer     = templates['FOOT'].safe_substitute(docroot='..')
    
    return templates['PAGE'].safe_substitute(header=heading,
                                             navigation=navigation,
                                             bg_image=bg_image,
                                             bg_image_source=bg_image_source,
                                             page_heading=page_title,
                                             page_subheading=page_subtitle,
                                             post_date=posting,
                                             contents=load_text_file(article),
                                             footer=footer)


if __name__ == "__main__":
    """Create a command-line main() entry point"""

    if len(sys.argv) != 8:
        # Define the usage 
        print sys.argv[0], '[page title]', '[page subtitle]', '[page desc]', '[post date]', '[bg image]', '[bg image source]', '[article filename]'
    else:
        # Do the deed
        print generate_post(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7])
