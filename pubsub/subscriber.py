'''
Created on 2 Oct 2016

@author: fressi
'''

import fnmatch
import re

from pubsub import element


class Subscriber(element.Element):
    """Base class for all subscribers.

    """

    def subscribe(self, topic_key, wild_card=False):
        """It subscribes to topics identified from given key
        """

        if wild_card:
            topic_key = WildCard(topic_key)

        self.domain.subscribe(subscriber_element=self, topic_key=topic_key)

    def on_subscribe(self, topic_element):
        """This event handler is called when subscribed to a new topic

        """

    def on_topic_data(self, publisher_element, topic_data):
        """This event handler is called when some topic data is published

        """


class WildCard(object):  # pylint: disable=too-few-public-methods
    """Helper class for wild card topic key matching

    """

    def __init__(self, obj):
        self._text = text = str(obj)
        self._match = re.compile(fnmatch.translate(text)).match

    def __eq__(self, obj):
        return self._match(str(obj))

    def __repr__(self):
        return "WildCard({})".format(repr(self._text))
