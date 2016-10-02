'''
Created on 2 Oct 2016

@author: fressi
'''

from pubsub import element


class Publisher(element.Element):
    """Base class for all publishers.

    """

    def publish(self, topic_element, topic_data):
        """It publishes some data on given topic.

        """
        return topic_element.publish(
            publisher_element=self, topic_data=topic_data)
