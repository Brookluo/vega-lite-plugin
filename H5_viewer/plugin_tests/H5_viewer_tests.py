from tests import base
import os
import time


def serUpModule():
    base.enabledPlugins.append('H5_viewer')
    base.startServer)


def tearDownModule():
    base.stopServer()


class H5_viewerTest(base.TestCase):

    def setUp(self):
        base.TestCase.setUp(self)
        self.users = [self.model('user').createUser(
            'usr%s' % num, 'passwd', 'tst', 'usr', 'u%s@u.com' % num)
            for num in [0, 1]]

    
