#   Programmer: limodou
#   E-mail:     limodou@gmail.com
#
#   Copyleft 2006 limodou
#
#   Distributed under the terms of the GPL (GNU Public License)
#
#   NewEdit is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#   $Id$

from sqlalchemy import *
import datetime

load_flag = False

class BaseTable(object):
    def get(cls, id):
        r = cls.mapper.select(cls.c.id == id)
        if r:
            return r[0]
        else:
            return None
    get = classmethod(get)

    def save(self):
        self.commit()

class Category(BaseTable):
    def __init__(self, title=None):
        self.title = title

    def __repr__(self):
        return "title=%s" % self.title

    def delete_id(cate_id):
        engine.begin()
        feeds = Feed.mapper.select_by_category_id(cate_id)
        for feed in feeds:
            Feed.delete_id(feed.id)
        RssCategory.delete(RssCategory.c.id == cate_id).execute()
        engine.commit()
    delete_id = staticmethod(delete_id)


class Feed(BaseTable):
    def __init__(self, category_id=None, title='', link='', homelink='', imagelink='', description=''):
        self.category_id = category_id
        self.title = title
        self.link = link
        self.homelink = homelink
        self.imagelink = imagelink
        self.description = description

    def delete_id(feed_id):
        engine.begin()
        RssData.delete(RssData.c.feed_id == feed_id).execute()
        RssFeed.delete(RssFeed.c.id == feed_id).execute()
        engine.commit()
    delete_id = staticmethod(delete_id)

    def __repr__(self):
        return "title=%s, link=%s, description=%s" % (self.title, self.link, self.description)

class Data(BaseTable):
    def __init__(self, feed_id=None, guid='', link='', pubDate=None, title='', comments='', description='', read=False):
        self.feed_id = feed_id
        self.guid = guid
        self.link = link
        if not pubDate:
            self.pubDate = datetime.datetime.now()
        else:
            self.pubDate = pubDate
        self.title = title
        self.comments = comments
        self.description = description
        self.read = read

    def __repr__(self):
        return "guid=%s, link=%s, pubDate=%s, title=%s, comments=%s, description=%s, read=%r" % (self.guid, self.link, self.pubDate.strftime("%Y-%m-%d %H:%M:%S"), self.title, self.comments, self.description, self.read)

    def un_read_count(cls, feed_id):
        r = select([func.count(cls.c.id)], and_(cls.c.feed_id==feed_id, cls.c.read==False)).execute()
        return r.fetchone()[0]
    un_read_count = classmethod(un_read_count)

    def set_read(cls, feed_id, *ids):
        if ids:
            RssData.update(and_(cls.c.feed_id == feed_id, cls.c.id.in_(ids))).execute(read=True)
        else:
            RssData.update(cls.c.feed_id == feed_id).execute(read=True)
    set_read = classmethod(set_read)

    def delete_posts(feed_id):
        RssData.delete(RssData.c.feed_id == feed_id).execute()
    delete_posts = staticmethod(delete_posts)

    def get_posts(cls, feed_id):
        return cls.mapper.select(cls.c.feed_id == feed_id, order_by=[desc(cls.c.pubDate)])
    get_posts = classmethod(get_posts)

def init(dbfile, create=False):
    global RssCategory, RssFeed, RssData, load_flag, engine

    if load_flag and not create:
        return

    engine = create_engine('sqlite://filename=%s' % dbfile, echo=False)

    if is_create('rss_category'):
        f = True
    else:
        f = False

    RssCategory = Table('rss_category', engine,
        Column('id', Integer, primary_key = True),
        Column('title', String, nullable = False),
        redefine = True
    )

    RssFeed = Table('rss_feed', engine,
        Column('id', Integer, primary_key = True),
        Column('category_id', Integer, ForeignKey("rss_category.id")),
        Column('title', String, nullable = False),
        Column('link', String, nullable = False),
        Column('homelink', String),
        Column('imagelink', String),
        Column('description', String),
        redefine = True
    )

    RssData = Table('rss_data', engine,
        Column('id', Integer, primary_key = True),
        Column('feed_id', Integer, ForeignKey("rss_feed.id")),
        Column('guid', String, nullable = False),
        Column('link', String, nullable = False),
        Column('pubDate', DateTime),
        Column('title', String),
        Column('comments', String),
        Column('description', String),
        Column('read', Boolean, nullable = False),
        redefine = True
    )

    if create and f:
        RssCategory.drop()
        RssFeed.drop()
        RssData.drop()
    if not f or create:
        RssCategory.create()
        RssFeed.create()
        RssData.create()

#    assign_mapper(Data, RssData, properties = {
#                    'description':deferred(RssData.c.description)
#                }
#            )
    assign_mapper(Data, RssData)
    assign_mapper(Feed, RssFeed, properties = {
                    'posts' : relation(Data.mapper, private=True)
                }
            )
    assign_mapper(Category, RssCategory, properties = {
                    'feeds' : relation(Feed.mapper, private=True)
                }
            )

    load_flag = True

def is_create(tablename):
    table = Table(tablename, engine, autoload=True)
    return len(table.columns.keys()) > 0

if __name__ == '__main__':
    init('d:/test.db')

    categories = Category.mapper.select()
    for i in categories:
        for f in i.feeds:
            number = len(Data.mapper.select(and_(Data.c.feed_id==f.id, Data.c.read==False)))
            print number

    c = Category.get(1)
    print c
