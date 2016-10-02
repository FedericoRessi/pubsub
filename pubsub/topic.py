'''
Created on 2 Oct 2016

@author: fressi
'''

import collections
import weakref

import six

from pubsub import element


class Topic(element.Element):
    """Base class for all topics.

    """

    def __init__(self, topic_key, domain, element_uuid):
        super(Topic, self).__init__(
            domain=domain, element_uuid=element_uuid)
        self._key = topic_key
        self._subscribers = collections.OrderedDict()

    @property
    def key(self):
        """It returns the key of this topic."""
        return self._key

    def subscribe(self, subscriber_element):
        """Subscribes given subscriber to this topic
        """

        self._subscribers[
            subscriber_element.uuid] = weakref.ref(subscriber_element)
        subscriber_element.on_subscribe(topic_element=self)

    def publish(self, publisher_element, topic_data):
        """Publish some data on this topic

        """

        for subscriber in self._iter_subscribers():
            subscriber.on_topic_data(
                publisher_element=publisher_element, topic_data=topic_data)

    def _iter_subscribers(self):
        subscribers = tuple(six.iteritems(self._subscribers))
        for subscriber_uuid, subscriber_ref in subscribers:
            subscriber = subscriber_ref()
            if subscriber is None:
                del self._subscribers[subscriber_uuid]
            else:
                yield subscriber

    def __repr__(self):
        return "Topic(topic_key={}, element_uuid={})".format(
            self.key, self.uuid)
