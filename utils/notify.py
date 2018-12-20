import requests

from pixiu.settings import MAIL_RECIPIENTS, MAIL_API_KEY, SERVERCHAN_KEY, MAIL_SENDER, MAIL_DOMAIN
from utils.log import Logger

logger = Logger(__name__).get_logger()


def send_wechat(title, content=''):
    sc_url = f'https://sc.ftqq.com/{SERVERCHAN_KEY}.send'
    data = {
        'text': title,
        'desp': content
    }
    try:
        sc_req = requests.post(url=sc_url, data=data)
        if sc_req.json().get('errno') == 0:
            return True
        else:
            logger.error(f'Send wechat error: {sc_req.json()}')
            return False
    except Exception as e:
        logger.error(f'ServerChan push failed: {e}', exc_info=1)
        return False


def send_mail(content, sub='DNSLog发来贺电', recipients=MAIL_RECIPIENTS):
    url = f"https://api.mailgun.net/v3/{MAIL_DOMAIN}/messages"

    # 您需要登录Mailgun创建API_USER，使用API_USER和API_KEY才可以进行邮件的发送。
    data = {
        'from': f'Pixiu {MAIL_SENDER}',
        'to': recipients,
        'subject': sub,
        'html': content,
    }
    auth = ('api', MAIL_API_KEY)

    try:
        mail_req = requests.post(url=url, auth=auth, data=data)
        if mail_req.json().get('message') == 'Queued. Thank you.':
            return True
        else:
            logger.error(f'Send mail error: {mail_req.json()}')
            return False
    except Exception as e:
        logger.error(f'Mailgun push failed: {e}', exc_info=1)
        return False


if __name__ == '__main__':
    send_wechat(title='aaabbcc', content='bbbcccddd')
    send_mail('Senddsdsavsafvewavdsavdsaer!')
