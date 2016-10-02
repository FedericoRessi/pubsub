'''
Created on 2 Oct 2016

@author: fressi
'''

import collections
import os
import logging
import uuid
import weakref

import yaml
import six

from pubsub import publisher, topic, subscriber


LOG = logging.getLogger(__name__)

_DOMAINS = {}


def default_domain(conf_file_path):
    """ It returns a singleton domain for given yaml configuration file path

    """

    conf_file_path = os.path.abspath(conf_file_path)
    domain = _DOMAINS.get(conf_file_path)
    while domain is None:
        new_domain = Domain.from_conf_file(conf_file_path)
        domain = _DOMAINS.setdefault(conf_file_path, new_domain)
        if new_domain is not domain:
            LOG.warning("Concurrent domain creation: %s", conf_file_path)

    return domain


class Domain(object):
    """ It represents a publication-subscription domain

    """

    def __init__(self, config=None):
        self._config = config
        self._elements = weakref.WeakValueDictionary()
        self._topics = collections.OrderedDict()

    @classmethod
    def from_conf_file(cls, file_path):
        """ Creates a new domain for given yaml configuration file path

        """

        with open(file_path, 'rt') as conf_file:
            conf = yaml.load(conf_file.read())
        return cls(conf)

    def create_element(
            self, element_class, element_uuid=None, element_table=None,
            **init_args):
        """ Creates an element of this domain of given class and uuid

        """
        if element_table is None:
            element_table = self._elements

        if element_uuid is None:
            element_uuid = uuid.uuid4()

        new_element = element_class(
            domain=self, element_uuid=element_uuid, **init_args)
        actual_element = element_table.setdefault(element_uuid, new_element)
        if actual_element is not new_element:
            raise RuntimeError(
                "An element with given element_uuid already exists!")
        return actual_element

    def get_element(
            self, element_uuid, create_class=None, element_table=None,
            **init_args):
        """ Creates an element of this domain of given class and uuid

        """
        if element_table is None:
            element_table = self._elements

        element = element_table.get(element_uuid)
        if create_class is not None:
            while element is None:
                try:
                    element = self.create_element(
                        element_uuid=element_uuid,
                        element_class=create_class,
                        element_table=element_table,
                        **init_args)
                except RuntimeError:
                    # this is due to concurrent element creation: try again
                    LOG.debug(
                        "Concurrent creation of domain element: %s, %s",
                        element_uuid, create_class, exc_info=True)
                    element = element_table.get(element_uuid)
            assert isinstance(element, create_class)

        return element

    def create_topic(
            self, topic_key, topic_class=topic.Topic, topic_uuid=None,
            **init_args):
        """ Creates a publisher for this domain

        """

        return self.create_element(
            element_class=topic_class, element_uuid=topic_uuid,
            topic_key=topic_key, element_table=self._topics, **init_args)

    def get_topic(self, topic_uuid, topic_class=None, **init_args):
        """It returns a publisher for given uuid

        """
        topic_element = self.get_element(
            element_uuid=topic_uuid, create_class=topic_class,
            element_table=self._topics, **init_args)
        assert topic_element is None or isinstance(topic_element, topic.Topic)
        return topic_element

    def create_publisher(
            self, publisher_class=publisher.Publisher, publisher_uuid=None,
            **init_args):
        """ Creates a publisher for this domain

        """

        return self.create_element(
            element_class=publisher_class, element_uuid=publisher_uuid,
            **init_args)

    def get_publisher(self, publisher_uuid, publisher_class=None, **init_args):
        """It returns a publisher for given uuid

        """
        publisher_element = self.get_element(
            element_uuid=publisher_uuid, create_class=publisher_class,
            **init_args)
        assert publisher_element is None or\
            isinstance(publisher_element, publisher.Publisher)
        return publisher_element

    def create_subscriber(
            self, subscriber_class=subscriber.Subscriber, subscriber_uuid=None,
            **init_args):
        """ Creates a subscriber for this domain

        """

        return self.create_element(
            element_class=subscriber_class, element_uuid=subscriber_uuid,
            **init_args)

    def get_subscriber(
            self, subscriber_uuid, subscriber_class=None, **init_args):
        """It returns a subscriber for given uuid

        """
        subscriber_element = self.get_element(
            element_uuid=subscriber_uuid, create_class=subscriber_class,
            **init_args)
        assert subscriber_element is None or\
            isinstance(subscriber_element, subscriber.Subscriber)
        return subscriber_element

    def subscribe(self, subscriber_element, topic_key):
        """Creates a new subscription to some existing topics

        """

        assert subscriber_element.uuid in self._elements

        for topic_element in six.itervalues(self._topics):
            if topic_key == topic_element.key:
                topic_element.subscribe(subscriber_element)
