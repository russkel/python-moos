#! /usr/bin/env python
"""
unittests for pymoos
"""

import unittest
import subprocess
import time
import logging
logging.basicConfig(level=logging.DEBUG,
        format='%(asctime)s | %(levelname)s:'
        ' %(name)s.%(funcName)s = %(message)s',
        )
logger = logging.getLogger('tests')
logger.level = logging.DEBUG

try:
    import pymoos
except ImportError as e:
    logger.error('Could not find pymoos package. Is it installed?')
    raise e

class pyMOOSTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            logger.info('starting MOOSDB ...')
            cls.moosdb_process = subprocess.Popen(['MOOSDB',
                            '--moos_community=pymoos_test_db'])
            logger.info('starting MOOSDB done')
        except OSError as ose:
            logger.error("Error while launching MOOSDB !"
                        "Is core-moos installed?\n")
            raise ose

    @classmethod
    def tearDownClass(cls):
        logger.info('killing MOOSDB ...')
        cls.moosdb_process.kill()
        logger.info('killing MOOSDB done')

    def test_00_run_close(self):
        c = pymoos.comms()

        self.assertFalse(c.is_connected())
        self.assertFalse(c.is_running())

        c.run('localhost', 9000, 'test_run_close')

        self.assertTrue(c.is_running())

        # sleep for a little to make sure we have time to connect
        c.wait_until_connected(2000)

        self.assertTrue(c.is_connected())
        self.assertTrue(c.is_asynchronous())

        c.close(True)

        self.assertFalse(c.is_connected())
        self.assertFalse(c.is_running())

    def test_01_name(self):
        c = pymoos.comms()
        c.run('localhost', 9000, 'test_name')
        c.wait_until_connected(2000)

        self.assertEqual(c.get_moos_name(), 'test_name')
        self.assertEqual(c.get_community_name(), 'pymoos_test_db')

        c.close(True)

    def test_10_notify_msg(self):
        c = pymoos.comms()
        c.set_on_connect_callback(
                lambda : self.assertTrue(c.register('TEST_NOTIFY_MSG')))
        c.run('localhost', 9000, 'test_notify_msg')
        c.wait_until_connected(5000)
        time.sleep(1)

        self.assertTrue(c.is_registered_for('TEST_NOTIFY_MSG'))

        t = pymoos.time()

        self.assertTrue(c.notify('TEST_NOTIFY_MSG', 1., t))

        time.sleep(1)

        msgs = c.fetch()
        self.assertNotEqual(len(msgs), 0)
        for msg in msgs:
            self.assertEqual(msg.key(), 'TEST_NOTIFY_MSG')
            self.assertEqual(msg.name(), 'TEST_NOTIFY_MSG')
            self.assertTrue(msg.is_name('TEST_NOTIFY_MSG'))
            self.assertEqual(msg.double(), 1)
            self.assertTrue(msg.is_double())
            self.assertEqual(msg.source(), 'test_notify_msg')
            self.assertFalse(msg.is_string())
            self.assertFalse(msg.is_binary())
            self.assertEqual(msg.time(), t)

        c.close(True)

    def test_11_register(self):
        # self.assertFalse(True)
        c = pymoos.comms()
        c.run('localhost', 9000, 'test_register')
        c.wait_until_connected(2000)

        self.assertFalse(c.is_registered_for('MOOS_TIME'))
        self.assertFalse(c.is_registered_for('MOOS_UPTIME'))

        c.register('MOOS_UPTIME',0.)

        self.assertFalse(c.is_registered_for('MOOS_TIME'))
        self.assertTrue(c.is_registered_for('MOOS_UPTIME'))

        c.close(True)

    def test_12_get_registered(self):
        c = pymoos.comms()
        c.run('localhost', 9000, 'test_get_registered')
        c.wait_until_connected(2000)

        c.register('MOOS_UPTIME',0.)
        c.register('MOOS_UPTIME2',0.)

        self.assertSetEqual(c.get_registered(),
                {'MOOS_UPTIME', 'MOOS_UPTIME2'})

        c.close(True)

    def test_13_is_registered_for(self):
        c = pymoos.comms()
        c.run('localhost', 9000, 'test_is_registered_for')
        c.wait_until_connected(2000)

        self.assertFalse(c.is_registered_for('MOOS_UPTIME'))

        c.register('MOOS_UPTIME', 0.)

        self.assertTrue(c.is_registered_for('MOOS_UPTIME'))
        self.assertFalse(c.is_registered_for('MOOS_UPTIME2'))

        c.close(True)

    @unittest.skip("TODO - Fix test")
    def test_20_zmsg_types(self):
        x = bytearray( [0, 3, 0x15, 2, 6, 0xAA] )
        s = 'hello'
        d = 384.653
        c = pymoos.comms()

        def on_connect():
            self.assertTrue(c.register('TEST_STRING_VAR', 0))
            self.assertTrue(c.register('TEST_DOUBLE_VAR', 0))
            self.assertTrue(c.register('TEST_BINARY_VAR', 0))
            return True

        c.set_on_connect_callback(on_connect)

        c.run('localhost', 9000, 'test_zmsg_types')
        c.wait_until_connected(2000)

        self.assertTrue(c.is_registered_for('TEST_STRING_VAR'))
        self.assertTrue(c.is_registered_for('TEST_DOUBLE_VAR'))
        self.assertTrue(c.is_registered_for('TEST_BINARY_VAR'))
        t = pymoos.time()

        self.assertTrue(c.notify('TEST_STRING_VAR', s, t))
        self.assertTrue(c.notify('TEST_DOUBLE_VAR', d, t))
        self.assertTrue(c.notify_binary('TEST_BINARY_VAR', str(x), t))

        time.sleep(1)

        idx = 0
        logger.debug('idx hit')
        msgs = c.fetch()
        logger.debug('fetch hit')
        self.assertNotEqual(len(msgs), 0)
        self.assertEqual(len(msgs), 3)
        for msg in msgs:
            logger.debug('iter hit')
            self.assertEqual(msg.time(), t)
            logger.debug('time hit')
            if msg.key() == 'TEST_STRING_VAR':
                logger.debug('string hit')
                self.assertTrue(msg.is_string())
                self.assertEqual(msg.string(), s)
                self.assertFalse(msg.is_double())
                self.assertFalse(msg.is_binary())
            elif msg.key() == 'TEST_DOUBLE_VAR':
                logger.debug('double hit')
                self.assertTrue(msg.is_double())
                self.assertEqual(msg.double(), d)
                self.assertFalse(msg.is_string())
                self.assertFalse(msg.is_binary())
            elif msg.key() == 'TEST_BINARY_VAR':
                logger.debug('binary hit')
                self.assertTrue(msg.is_binary())
                self.assertEqual(str(msg.binary_data()), str(x))
                self.assertTrue(msg.is_string())
                self.assertFalse(msg.is_double())

            idx += 1
            logger.debug('idx++ hit')

        self.assertEqual(idx, 3)

        c.close(True)

    def test_30_on_connect_callback_inline(self):
        c = pymoos.comms()
        c.set_on_connect_callback(
                lambda : self.assertTrue(c.register('TEST_ON_CALLBACK_I')))
        c.run('localhost', 9000, 'test_on_connect_callback_inline')
        c.wait_until_connected(2000)

        time.sleep(1)

        self.assertTrue(c.is_registered_for('TEST_ON_CALLBACK_I'))

        c.close(True)

    def test_31_on_connect_callback(self):
        logger.debug(' on ')
        c = pymoos.comms()

        def on_connect():
            logger.debug(' on ')
            self.assertTrue(c.register('TEST_ON_CALLBACK', 0))
            return True

        c.set_on_connect_callback(on_connect)
        c.run('localhost', 9000, 'test_on_connect_callback')
        c.wait_until_connected(2000)
        time.sleep(.1)

        self.assertTrue(c.is_registered_for('TEST_ON_CALLBACK'))

        c.close(True)

    def test_32_on_mail_callback(self):
        logger.debug(' on ')
        c = pymoos.comms()
        self.received_mail = False

        def on_connect():
            logger.debug(' on ')
            self.assertTrue(c.register('TEST_CALLBACK_ONMAIL_VAR', 0))
            return True

        def on_new_mail():
            logger.debug(' on ')
            for msg in c.fetch():
                logger.debug(' one new mail ')
                self.assertTrue(msg.is_name('TEST_CALLBACK_ONMAIL_VAR'))
                self.assertEqual(msg.double(), 1)
                self.received_mail = True
                logger.debug(' mail processed ')
            return True

        c.set_on_connect_callback(on_connect)
        c.set_on_mail_callback(on_new_mail)
        c.run('localhost', 9000, 'test_on_mail_callback')
        c.wait_until_connected(2000)

        time.sleep(1)

        self.assertTrue(c.is_registered_for('TEST_CALLBACK_ONMAIL_VAR'))
        self.assertFalse(self.received_mail)
        self.assertTrue(c.notify('TEST_CALLBACK_ONMAIL_VAR', 1, -1))

        time.sleep(1)

        self.assertTrue(self.received_mail)

        c.close(True)

    @unittest.skip("TODO - Fix test")
    def test_33_on_mail_active_queues(self):
        logger.debug(' on ')
        c = pymoos.comms()
        self.received_mail = False
        self.received_mail_q_v1 = False
        self.received_mail_q_v2 = False
        self.received_mail_q2_v = False

        def on_connect():
            logger.debug(' on ')
            self.assertTrue(c.register('TEST_ONMAIL_ACTIVE_Q', 0))
            self.assertTrue(c.register('TEST_ONQUEUE_VAR1', 0))
            self.assertTrue(c.register('TEST_ONQUEUE_VAR2', 0))
            self.assertTrue(c.register('TEST_ONQUEUE2_VAR', 0))
            return True

        def on_new_mail_aq():
            logger.debug(' on ')
            for msg in c.fetch():
                logger.debug(' one new mail = ' + msg.key())
                # self.assertTrue(msg.is_name('TEST_ONMAIL_ACTIVE_Q'))
                # self.assertEqual(msg.double(), 1)
                self.received_mail = True
                logger.debug(' mail processed')
            return True

        def queue1(msg):
            logger.debug(' on ')
            if msg.is_name('TEST_ONQUEUE_VAR1'):
                self.assertEqual(msg.double(), 2)
                self.received_mail_q_v1 = True
            elif msg.is_name('TEST_ONQUEUE_VAR2'):
                self.assertEqual(msg.double(), 3)
                self.received_mail_q_v2 = True
            return True

        def queue2(msg):
            logger.debug(' on ')
            if msg.is_name('TEST_ONQUEUE2_VAR'):
                self.assertEqual(msg.double(), 4)
                self.received_mail_q2_v = True
            return True



        c.set_on_connect_callback(on_connect)
        c.set_on_mail_callback(on_new_mail_aq)
        c.add_active_queue('queue1', queue1)
        c.add_message_route_to_active_queue('queue1', 'TEST_ONQUEUE_VAR1')
        c.add_message_route_to_active_queue('queue1', 'TEST_ONQUEUE_VAR2')
        c.add_active_queue('queue2', queue2)
        c.add_message_route_to_active_queue('queue2', 'TEST_ONQUEUE2_VAR')
        c.run('localhost', 9000, 'test_on_mail_active_queues')
        c.wait_until_connected(5000)

        time.sleep(1)

        self.assertTrue(c.is_registered_for('TEST_ONMAIL_ACTIVE_Q'))
        self.assertTrue(c.is_registered_for('TEST_ONQUEUE_VAR1'))
        self.assertTrue(c.is_registered_for('TEST_ONQUEUE_VAR2'))
        self.assertTrue(c.is_registered_for('TEST_ONQUEUE2_VAR'))
        self.assertFalse(self.received_mail)
        self.assertFalse(self.received_mail_q_v1)
        self.assertFalse(self.received_mail_q_v2)
        self.assertFalse(self.received_mail_q2_v)
        self.assertTrue(c.notify('TEST_ONMAIL_ACTIVE_Q', 1))
        self.assertTrue(c.notify('TEST_ONQUEUE_VAR1', 2))
        self.assertTrue(c.notify('TEST_ONQUEUE_VAR2', 3))
        self.assertTrue(c.notify('TEST_ONQUEUE2_VAR', 4))

        time.sleep(1)

        self.assertTrue(self.received_mail)
        self.assertTrue(self.received_mail_q_v1)
        self.assertTrue(self.received_mail_q_v2)
        self.assertTrue(self.received_mail_q2_v)

        c.close(True)


if __name__ == '__main__':
    unittest.main()
