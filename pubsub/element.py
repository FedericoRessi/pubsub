'''
Created on 2 Oct 2016

@author: fressi
'''

import weakref


class Element(object):
    """ Base class for all domain elements

    """

    def __init__(self, domain, element_uuid):
        self._domain = weakref.ref(domain)
        self._uuid = element_uuid

    @property
    def domain(self):
        """Parent pub-sub domain

        """
        return self._domain()

    @property
    def uuid(self):
        """Publisher UUID

        """
        return self._uuid
