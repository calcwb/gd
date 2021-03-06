#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011  Governo do Estado do Rio Grande do Sul
#
#   Author: Lincoln de Sousa <lincoln@gg.rs.gov.br>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Module to carry about all interaction between wordpress XMLRPC
interface and our system.
"""

import re
from datetime import datetime
from urllib import urlopen
from xmlrpclib import Server
from json import loads

from flask import url_for

from gd import conf
from gd import utils
from gd.model import User

class Namespace(object):
    """Abstracts an XMLRPC namespace available in wordpress"""
    def __init__(self, name, conf):
        self.name = name
        self.conf = conf
        self.server = Server(conf['address'],allow_none=True)

    def wrap(self, attr, method):
        """Wrapper that decorates XMLRPC methods that needs the user,
        password and blog id to be passed before anything"""
        def wrapper(*args, **kwargs):
            # Yes, I'm aware that `kwargs' is not being expanded when
            # called in the next line. The params are being sent packed
            # to the XMLRPC server and there they'll be expanded.  Maybe
            # it will change in the future, if I find any function that
            # doesn't fit this strategy
            # print "CALLING XMLRPC", kwargs, args
            ret = method(
                0, self.conf['user'], self.conf['password'],
                kwargs, *args)
            converter = 'convert_%s' % attr
            if converter in globals():
                return globals()[converter](ret)
            return ret
        return wrapper

    def __getattribute__(self, attr):
        try:
            return super(Namespace, self).__getattribute__(attr)
        except AttributeError:
            return self.wrap(
                attr, getattr(self.server, '%s.%s' % (self.name, attr)))


class Wordpress(object):
    """Represents the Wordpress from which we consume
    mostly via XML-RPC"""
    def __init__(self, address, blogid, user, password):
        self.default_namespace = 'exapi'
        self.known_namespaces = 'exapi', 'wpgd', 'wp', 'pairwise', 'ngg', 'nggv', \
            'wpgp', 'govr', 'govp', 'gove', 'wpgove', 'wpgovp', 'gabdig', 'monitoramento'
        self.conf = {
            'address': address,
            'user': user,
            'password': password
        }

    def getRSS(self):
        return wp_links_to_flask(urlopen(conf.WORDPRESS_RSS).read())

    def __getattribute__(self, attr):
        try:
            return super(Wordpress, self).__getattribute__(attr)
        except AttributeError:
            pass

        if attr in self.known_namespaces:
            return Namespace(attr, self.conf)

        # Falling back to our default namespace
        return getattr(Namespace(self.default_namespace, self.conf), attr)


def convert_getComments(comments):
    """Converts the comments coming from wordpress API"""
    for comment in comments:
        link = url_for('post', pid=comment['post_id'])
        comment['link'] = '%s#coment-%s' % (link, comment['comment_id'])
        comment['user'] = User.get(comment['user_id'])
    return comments


def convert_getPageByPath(post):
    """Converts a json that represents a wordpress page into a Post
    instance.

    If the requested page does not exist in the wordpress database,
    this function will return None"""
    return post and Post(post) or None


def convert_getRecentPosts(posts):
    """Convert JSON dictionaries in Post instances"""
    return [Post(i) for i in posts]


def convert_getPostsByCategory(data):
    return posts_and_pagination(data)

def convert_getArchivePosts(data):
    return posts_and_pagination(data)

def convert_getPostsByTag(data):
    return posts_and_pagination(data)


def convert_getPosts(data):
    return posts_and_pagination(data)


def convert_search(data):
    return posts_and_pagination(data)


def convert_getPost(post):
    return Post(post)


def convert_getSidebar(sidebar):
    """Converts all links found in the html of the sidebar to flask
    links"""
    return wp_links_to_flask(sidebar)


def posts_and_pagination(data):
    """Convert JSON dictionaries in Post instances"""
    pagination = data['pagination']
    posts = [Post(i) for i in data['posts']]
    return pagination, posts


def wp_links_to_flask(text):
    """Convert links generated by wordpress to our own style

    This is really just used for the sidebar links. Other wp links
    might not be appropriately converted!
    """
    subs = {}
    wp_url = utils.nts(conf.WORDPRESS_ADDRESS)
    site_url = utils.nts(conf.BASE_URL)
    for href in re.findall('[\'">]('+wp_url+'.*?)["\'<]', text):
        subs[href] = wp_link_style_to_flask(href)
    for original, translated in subs.items():
        text = text.replace(original, translated)
    text = text.replace(wp_url, site_url)

    # Hammer to avoid breaking static content published by users
    # directly in wordpress admin
    return text.replace(
        site_url + '/wp-content',
        wp_url + '/wp-content')


def wp_link_style_to_flask(href):
    """Converts wordpress url style to flask urlws"""
    base = conf.BASE_URL[:-1]
    if href.find("m=") != -1:
        m = re.search('m=(\d+)', href).group(1)
        return base+url_for('archive', m=m)
    if href.find("cat=") != -1:
        cat = re.search('cat=(\d+)', href).group(1)
        return base+url_for('category', cid=cat)
    elif href.find("tag=") != -1:
        tag = re.search('tag=(\w+)', href).group(1)
        return base+url_for('tag', slug=tag)
    elif href.find("p=") != -1:
        p = re.search('p=(\d+)', href).group(1)
        return base+url_for('post', pid=p)
    elif href.find("feed=rss2") != -1:
        return base+url_for('feed')
    else:
        return href


class Post(object):
    """Wordpress post wrapper class

    This class that makes it more natural and easy to work with posts
    received from the wordpress source in a dictionary format."""
    def __init__(self, data):
        self.data = data
        self.datetime = datetime.strptime(
            data['date']['date'].value, "%Y%m%dT%H:%M:%S")

    def __getattribute__(self, attr):
        try:
            return super(Post, self).__getattribute__(attr)
        except AttributeError:
            try:
                return self.data[attr]
            except:
                raise AttributeError

    @property
    def permalink(self):
        """Returns the permanent link for this post"""
        return url_for('post', pid=self.id)

    @property
    def the_date(self):
        return self.datetime

    def has_category(self, slug):
        """Returns true if the post has a given category"""
        return bool([i for i in self.data['categories'] if i['slug'] == slug])

    def has_field(self, key):
        """Returns true if the post has a given custom field"""
        return bool([i for i in self.data['custom_fields'] if i['key'] == key])

    def get_field(self, key, default=None):
        """Returns the value of a custom field"""
        for i in self.data['custom_fields']:
            if i['key'] == key:
                return i['value']
        return default


wordpress = Wordpress(
    conf.WORDPRESS_XMLRPC, conf.WORDPRESS_BLOGID,
    conf.WORDPRESS_USER, conf.WORDPRESS_PASSWORD
)


class Gallery(object):
    def __init__(self):
        pass

    def _api_call(self, method, value, limit=0):
        param = {
            'search': 'term',
            'tag': 'term',
            'gallery': 'id',
            'image': 'id',
            'album': 'id',
        }[method]
        url = ('%(base)s/index.php?callback=json&api_key=true&'
               'format=json&method=%(method)s&%(param)s=%(value)s&'
               'limit=%(limit)s') % {
            'base': conf.WORDPRESS_ADDRESS,
            'method': method,
            'param': param,
            'value': value,
            'limit': limit,
        }
        return loads(urlopen(url).read())

    def search(self, tag, limit=0):
        imgs = self._api_call('search', tag, limit)['images']
        return limit > 0 and imgs[:limit] or imgs

    def get_album(self, aid):
        return self._api_call('album', aid)


gallery = Gallery()
