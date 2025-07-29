import logging

logging.basicConfig(level=logging.INFO,
                    datefmt='%Y-%m-%d %H:%M:%S',
                    format='%(asctime)s - %(name)s - $(levelname)s - %(lineno)s - %(module)s - %(message)s')
logging.getLogger('requests').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)
