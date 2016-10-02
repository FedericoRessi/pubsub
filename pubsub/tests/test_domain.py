'''
Created on 2 Oct 2016

@author: fressi
'''

# pylint: disable=unused-import,redefined-outer-name,invalid-name

import mock
import pytest

from pubsub import domain, element, publisher, subscriber, topic

from pubsub.tests.fixtures import create_temp_yaml  # noqa


def test_default_domain_given_same_file(create_temp_yaml):  # noqa
    """default_domain function returns the same instance given the same file

    """

    conf_file1 = create_temp_yaml({})

    domain1 = domain.default_domain(conf_file1)
    domain2 = domain.default_domain(conf_file1)

    assert domain1 is domain2


def test_default_domain_given_two_files(create_temp_yaml):  # noqa
    """default_domain function doesn't return the same instance given not the
    same files

    """

    conf_file1 = create_temp_yaml({})
    conf_file2 = create_temp_yaml({})

    domain1 = domain.default_domain(conf_file1)
    domain2 = domain.default_domain(conf_file2)

    assert domain1 is not domain2


def test_default_domain_given_cuncurrent_same_file(create_temp_yaml):  # noqa
    """default_domain function returns the same instance given the same file

    """

    conf_file1 = create_temp_yaml({})

    domain1 = domain.default_domain(conf_file1)
    with mock.patch.object(domain, "_DOMAINS") as domains:
        domains.get.return_value = None
        domains.setdefault.return_value = domain1

        domain2 = domain.default_domain(conf_file1)

    assert domain1 is domain2


def test_create_topic():
    """create_topic creates a topic identified by an unique ID

    """

    domain1 = domain.Domain()

    topic1 = domain1.create_topic(topic_key="some_key")

    assert isinstance(topic1, topic.Topic)
    assert topic1.domain is domain1
    assert topic1 is domain1.get_topic(topic1.uuid)
    assert topic1.key == "some_key"


def test_create_topic_given_existing_uuid():
    """create_topic creates a topic with and existing UUID

    """

    domain1 = domain.Domain()
    topic1 = domain1.create_topic(topic_key="some_key")

    with pytest.raises(RuntimeError):
        domain1.create_topic(topic_key="some_key", topic_uuid=topic1.uuid)


def test_get_topic_given_custom_class():
    """create_publisher creates a publisher identified by an unique ID

    """

    class CustomTopic(topic.Topic):
        """Custom topic class"""

    domain1 = domain.Domain()

    topic1 = domain1.get_topic(
        topic_uuid="some_uuid", topic_class=CustomTopic, topic_key="some_key")

    assert isinstance(topic1, CustomTopic)
    assert topic1.domain is domain1
    assert topic1.uuid == "some_uuid"
    assert topic1 is domain1.get_topic("some_uuid")
    assert topic1.key == "some_key"


def test_create_publisher():
    """create_publisher creates a publisher identified by an unique ID

    """

    domain1 = domain.Domain()

    publisher1 = domain1.create_publisher()

    assert isinstance(publisher1, publisher.Publisher)
    assert publisher1.domain is domain1
    assert publisher1 is domain1.get_publisher(publisher1.uuid)


def test_create_publisher_given_existing_uuid():
    """create_publisher creates a publisher with and existing UUID

    """

    domain1 = domain.Domain()
    publisher1 = domain1.create_publisher()

    with pytest.raises(RuntimeError):
        domain1.create_publisher(publisher_uuid=publisher1.uuid)


def test_get_publisher_given_custom_class():
    """create_publisher creates a publisher identified by an unique ID

    """

    class CustomPublisher(publisher.Publisher):
        """Custom publisher class"""

    domain1 = domain.Domain()

    publisher1 = domain1.get_publisher(
        publisher_uuid="some_uuid", publisher_class=CustomPublisher)

    assert isinstance(publisher1, CustomPublisher)
    assert publisher1.domain is domain1
    assert publisher1.uuid == "some_uuid"
    assert publisher1 is domain1.get_publisher("some_uuid")


def test_create_subscriber():
    """create_subscriber creates a subscriber identified by an unique ID

    """

    domain1 = domain.Domain()

    subscriber1 = domain1.create_subscriber()

    assert isinstance(subscriber1, subscriber.Subscriber)
    assert subscriber1.domain is domain1
    assert subscriber1 is domain1.get_subscriber(subscriber1.uuid)


def test_create_subscriber_given_existing_uuid():
    """create_subscriber creates a publisher with and existing UUID

    """

    domain1 = domain.Domain()
    subscriber1 = domain1.create_subscriber()

    with pytest.raises(RuntimeError):
        domain1.create_subscriber(subscriber_uuid=subscriber1.uuid)


def test_get_subscriber_given_custom_class():
    """create_publisher creates a publisher identified by an unique ID

    """

    class CustomSubscriber(subscriber.Subscriber):
        """Custom publisher class"""

    domain1 = domain.Domain()

    subscriber1 = domain1.get_subscriber(
        subscriber_uuid="some_uuid", subscriber_class=CustomSubscriber)

    assert isinstance(subscriber1, CustomSubscriber)
    assert subscriber1.domain is domain1
    assert subscriber1.uuid == "some_uuid"
    assert subscriber1 is domain1.get_subscriber("some_uuid")


def test_get_element_given_create_class_concurrent_same_uuid():
    """create_publisher creates a publisher identified by an UUID

    """

    domain1 = domain.Domain()

    element1 = domain1.get_element(
        element_uuid="same_uuid", create_class=element.Element)

    with mock.patch.object(domain1, "_elements") as elements:
        elements.get.side_effect = [None, element1]
        elements.setdefault.return_value = element1

        element2 = domain1.get_element(
            element_uuid="same_uuid", create_class=element.Element)

    assert element2 is element1


def test_subscribe():
    """publish sends data to subscriber throw topic

    """

    # given
    domain1 = domain.Domain()
    domain1.create_topic(topic_key='key1')
    topic1 = domain1.create_topic(topic_key='key2')
    domain1.create_topic(topic_key='key3')
    domain1.create_topic(topic_key='key4')
    subscriber1 = domain1.create_subscriber()
    subscriber1.on_subscribe = on_subscribe = mock.MagicMock()

    # when
    subscriber1.subscribe('key2')

    # then
    on_subscribe.assert_called_once_with(topic_element=topic1)


def test_subscribe_given_wild_card():
    """publish sends data to subscriber throw topic

    """

    # given
    domain1 = domain.Domain()
    domain1.create_topic(topic_key='non_matching_key1')
    topic1 = domain1.create_topic(topic_key='matching_key1')
    topic2 = domain1.create_topic(topic_key='matching_key2')
    domain1.create_topic(topic_key='non_matching_key2')
    subscriber1 = domain1.create_subscriber()
    subscriber1.on_subscribe = on_subscribe = mock.MagicMock()

    # when
    subscriber1.subscribe('matching_key*', wild_card=True)

    # then
    on_subscribe.assert_has_calls([
        mock.call(topic_element=topic1), mock.call(topic_element=topic2)])


def test_publish():
    """publish sends data to subscriber throw topic

    """

    domain1 = domain.Domain()
    topic1 = domain1.create_topic(topic_key='some_topic_key')
    domain1.create_topic(topic_key='other_topic_key')
    publisher1 = domain1.create_publisher()
    subscriber1 = domain1.create_subscriber()
    subscriber1.on_topic_data = on_topic_data = mock.MagicMock()
    subscriber1.subscribe('some_topic_key')

    # when
    publisher1.publish(topic_element=topic1, topic_data="some_topic_data")

    # then
    on_topic_data.assert_called_once_with(
        publisher_element=publisher1, topic_data='some_topic_data')


def test_publish_after_subscriber_disposal():
    """publish sends data to subscriber throw topic

    """

    # given
    domain1 = domain.Domain()
    topic1 = domain1.create_topic(topic_key='some_topic_key')
    domain1.create_topic(topic_key='other_topic_key')
    publisher1 = domain1.create_publisher()
    subscriber1 = domain1.create_subscriber()
    subscriber1.on_topic_data = on_topic_data = mock.MagicMock()
    subscriber1.subscribe('some_topic_key')
    del subscriber1

    # when
    publisher1.publish(topic_element=topic1, topic_data="some_topic_data")

    # then
    on_topic_data.assert_not_called()
