#!/usr/bin/env python

"""
generator.py

This module defines a series of functions to create static html pages
from the given templates in this folder.

The overall site index and tag summary pages are drive by index.json,
the master "database" of all posts and tags.

"""

import sys
from string import Template
from datetime import datetime
import os.path
import json

def load_text_file (filename):
    with open (filename, "r") as f:
        return f.read()

try:
    SITE_INDEX = json.loads(load_text_file(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                        '../posts/index.json')))
except:
    SITE_INDEX = {}

#
# index.json handling logic

# post keys are strings in "%Y%m%d" format

def post_date_as_datetime (s, fmt="%Y%m%d"):
    """Convert the string in the given format to a datetime object
       defaulting to now in YYYYMMDD format"""
    
    try:
        return datetime.strptime(s, fmt)
    except ValueError:
        # return the current date instead
        return datetime.utcnow()

def post_date_as_link (s, fmt="%Y%m%d", docroot='..'):
    """Convert the string in the given format to a link in /posts"""

    dt = post_date_as_datetime(s, fmt)
    return ''.join([docroot, '/posts/', dt.strftime("%Y.%m.%d"), '.post.html'])

def post_date_as_display_value (s, in_fmt="%Y%m%d", out_fmt="%B %d, %Y"):
    """Convert the string in the given input format 
       to a string in the output (human readable) format"""

    dt = post_date_as_datetime(s, in_fmt)
    return dt.strftime(out_fmt)

# each post json contains all the information to
# produce the index or the tag summary page

def posts_for_tag (tag):
    """Return a dict of all the posts with the given tag"""

    posts = {}
    try:
        for (date, post) in SITE_INDEX['posts'].items():
            if tag in post['tags']:
                posts[date] = post
    except KeyError:
        pass

    return posts

def get_all_posts ():
    """Return a dict of all the posts"""

    posts = {}
    try:
        for (date, post) in SITE_INDEX['posts'].items():
            posts[date] = post
    except KeyError:
        pass

    return posts

def get_tag_link (tag, docroot='..'):
    """Return the html link for this tag"""

    try:
        tag_data = SITE_INDEX['tags'][tag]
        return ''.join([docroot, '/', tag_data['link']])
    except KeyError:
        return ''


#
# Template generation logic

template_files = {
    'PAGE': 'content.html',
    'FOOT': 'footer.html',
    'HEAD': 'header.html',
    'NAV' : 'navigation.html',
    'DATE': 'post_date.html',
    'PREV': 'post_preview.html',
    'TAG' : 'tag.html'
}

templates = {}

for template_type, template_file in template_files.items():
    templates[template_type] = Template(load_text_file(template_file))

def generate_post (post_date, article_filename, docroot='..'):
    """Convert the post metadata from SITE_INDEX and article file contents into a static html string"""

    try:
        post  = SITE_INDEX['posts'][post_date]
        title = post['title']
        desc  = post['subtitle']
        heading_style = ''
        if post.has_key('color'):
            heading_style = 'style="color:'+post['color']+'"'
 
        # set the page header, footer and navigation
        heading    = templates['HEAD'].safe_substitute(title=title, description=desc, docroot=docroot)
        posting    = templates['DATE'].safe_substitute(post_date=post_date_as_display_value(post_date))
        navigation = templates['NAV'].safe_substitute(docroot=docroot)
        footer     = templates['FOOT'].safe_substitute(docroot=docroot)

        # make the list of tag links
        tags = []
        for tag_name in post['tags']:
            tags.append(templates['TAG'].safe_substitute(tag=tag_name,
                                                         tag_link=get_tag_link(tag_name, docroot=docroot)))
        # write the page post
        return templates['PAGE'].safe_substitute(header=heading,
                                                 heading_style=heading_style,
                                                 navigation=navigation,
                                                 bg_image=post['image'],
                                                 bg_image_source=post['image_src'],
                                                 page_heading=title,
                                                 page_subheading=desc,
                                                 post_date=posting,
                                                 contents=load_text_file(article_filename),
                                                 footer=footer)
    except Exception, e:
        print >>sys.stderr, e

def generate_summary (tag, docroot=''):
    """Use the SITE_INDEX to produce a summary page for this tag"""

    try:
        tag_data = SITE_INDEX['tags'][tag]
        tag_desc = tag_data['heading']
        heading_style = ''
        if tag_data.has_key('color'):
            heading_style = 'style="color:'+tag_data['color']+'"'
        
        # get the list of posts for this tag
        post_limit = None
        page_title = tag

        # index is a special case
        if 'Index' == tag:
            post_data  = get_all_posts()
            post_limit = 5
            page_title = 'Denis Papathanasiou'
        else:
            post_data = posts_for_tag (tag)

        # write their summaries in reverse chronological order
        posts = []
        for i, post_date in enumerate(sorted(post_data.iterkeys(), reverse=True)):
            if post_limit is not None and \
               i > post_limit:
                break
            
            # get the data for this post
            post = post_data[post_date]
            
            # make the list of tag links
            tags = []
            for tag_name in post['tags']:
                tags.append(templates['TAG'].safe_substitute(tag=tag_name,
                                                             tag_link=get_tag_link(tag_name, docroot=docroot)))

            posts.append(templates['PREV'].safe_substitute(link=post_date_as_link(post_date, docroot=docroot),
                                                           title=post['title'],
                                                           sub_title=post['subtitle'],
                                                           date=post_date_as_display_value(post_date),
                                                           tags=', '.join(tags)))

        # set the page header, footer and navigation
        heading    = templates['HEAD'].safe_substitute(title=page_title, description=tag_desc, docroot=docroot)
        navigation = templates['NAV'].safe_substitute(docroot=docroot)
        footer     = templates['FOOT'].safe_substitute(docroot=docroot)

        # write the full summary page
        return templates['PAGE'].safe_substitute(header=heading,
                                                 heading_style=heading_style,
                                                 navigation=navigation,
                                                 bg_image=tag_data['image'],
                                                 bg_image_source=tag_data['image_src'],
                                                 page_heading=page_title,
                                                 page_subheading=tag_desc,
                                                 post_date='',
                                                 contents='\n'.join(posts),
                                                 footer=footer)
    except Exception, e:
        print >>sys.stderr, e


if __name__ == "__main__":
    """Create a command-line main() entry point"""

    args = len(sys.argv)
    usage = ' '.join([sys.argv[0], '--tag=[tag] OR --post=[post date]', '[article filename (post only)]'])
    
    if args < 2 or args > 3:
        # Define the usage 
        print usage
    else:
        # Do the deed
        # create a tag summary page
        if sys.argv[1].startswith('--tag='):
            print generate_summary(sys.argv[1].split('=')[1])
        # create a post
        elif sys.argv[1].startswith('--post='):
            print generate_post(sys.argv[1].split('=')[1], sys.argv[2])
        # sorry, charlie
        else:
            print usage
