import logging

from thingsboard.common.core.threaded import Threaded


class ThreadMonitor(object):
    """Monitors registered threads.

    It is a passive class. To check if threads are still alive, call method check_threads() regularly.
    """
    log = logging.getLogger(__name__)
    threadList = []

    # References single instance of this class.
    _instance = None            # type: ThreadMonitor or None

    def __init__(self, log_name_prefix:str=''):
        super(ThreadMonitor, self).__init__()
        if self._instance:
            assert False, 'Only one instance of this class is allowed'
        else:
            self._set_instance(self)
            if log_name_prefix:
                type(self).log = logging.getLogger(log_name_prefix + '.' + __name__)

    @classmethod
    def instance(cls):
        """Returns the single instance of this class.
        """
        assert cls._instance, 'Create an instance of this class first'
        return cls._instance

    @classmethod
    def _set_instance(cls, instance):
        assert cls._instance is None, 'Only one instance of this class allowed'
        cls._instance = instance

    @classmethod
    def register(cls, thread: Threaded):
        cls.threadList.append(thread)
        return True

    @classmethod
    def deregister(cls, thread: Threaded):
        if thread in cls.threadList:
            cls.threadList.remove(thread)
        return True

    @classmethod
    def check_threads(cls):
        for thread in cls.threadList:
            if not thread.is_alive():
                cls.log.error(f'Thread \'{thread.name}\' no more alive!')
                return False
        return True
