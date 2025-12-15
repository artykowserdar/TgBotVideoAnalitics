import uvicorn
import logging.config

from logging.handlers import SMTPHandler
from app import config


# logger = logging.getLogger()
# logger.setLevel(logging.DEBUG)
# mail_handler = SMTPHandler((config.MAIL_SERVER,
#                             config.MAIL_PORT),
#                            config.MAIL_USERNAME,
#                            config.MAIL_RECEIVERS,
#                            '[EZIZ-ULKAM] An ERROR was thrown',
#                            (config.MAIL_USERNAME,
#                             config.MAIL_PASSWORD),
#                            secure=())
# mail_handler.setLevel(logging.ERROR)
# mail_handler.setFormatter(logging.Formatter("""
# Time:               %(asctime)s
# Message type:       %(levelname)s
#
#
# Message:
#
# %(message)s
# """))
# logger.addHandler(mail_handler)

if __name__ == '__main__':
    # logger.info('Starting FastAPI Server')
    uvicorn.run('app.main:app',
                host='0.0.0.0',
                port=5056,
                workers=3,
                reload=True)
