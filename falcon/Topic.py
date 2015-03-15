# -*- coding: utf-8 -*-

from Entry import Entry

class Topic(Entry):
    """ Tool class for getting topic info """

    def __init__(self, session, url):
        Entry.__init__(self, session, url)

    def get_num_followers(self):
        """ Return number of followers int. """
        num = self.soup.find('div', class_ = 'zm-topic-side-followers-info').a\
                        .get_text(strip = True).encode('utf-8')
        return int(num)

    def get_description(self):
        """ Return description text. """
        description = self.soup.find('div', id = 'zh-topic-desc')\
                                .find('div', class_ = 'zm-editable-content')\
                                .get_text(strip = True).encode('utf-8')
        return self.encode2Character(description)
        