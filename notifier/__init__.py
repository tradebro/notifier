from os import environ
from string import Template
from decimal import Decimal
import aio_pika
import ujson
import telepot


AMQP_CONN_STRING = environ.get('AMQP_CONN_STRING')
AMQP_QUEUE = environ.get('AMQP_QUEUE')
TELEGRAM_TOKEN = environ.get('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = environ.get('TELEGRAM_CHAT_ID')


TEMPLATE_BUY = '''<b>TradeBro</b>

New trade has come, details below.

Action: <b>$action</b>

Pair: $pair
Price: $price

Written with 💚 by contributors
<a href="https://github.com/tradebro">TradeBro</a>'''

TEMPLATE_SELL = '''<b>TradeBro</b>

New trade has come, details below.

Action: <b>$action</b>

Pair: $pair
Price: $price

PnL: $pnl

Written with 💚 by contributors
<a href="https://github.com/tradebro">TradeBro</a>'''


def format_number(number, precision: int = 2) -> str:
    return '{:0.0{}f}'.format(number, precision)


async def send_message(message: str):
    bot = telepot.Bot(token=TELEGRAM_TOKEN)
    bot.sendMessage(chat_id=TELEGRAM_CHAT_ID,
                    text=message,
                    parse_mode='HTML')


async def send_buy_notification(message_body: dict):
    template = Template(TEMPLATE_BUY)
    message_html = template.substitute({
        'action': message_body.get('side'),
        'pair': message_body.get('symbol'),
        'price': message_body.get('fills')[0].get('price')
    })

    return await send_message(message=message_html)


async def send_sell_notification(message_body: dict):
    buy_price = message_body.get('buyPrice')
    sell_price = message_body.get('fills')[0].get('price')

    pnl = Decimal(sell_price) / Decimal(buy_price)
    pnl = Decimal(1) - pnl if pnl < Decimal(1) else pnl - Decimal(1)
    pnl = pnl * Decimal(100)
    pnl = format_number(pnl)

    template = Template(TEMPLATE_BUY)
    message_html = template.substitute({
        'action': message_body.get('side'),
        'pair': message_body.get('symbol'),
        'price': sell_price,
        'pnl': pnl,
    })

    return await send_message(message=message_html)


async def send_notification(message_body: dict):
    side = message_body.get('side')
    funcs = {
        'BUY': send_buy_notification,
        'SELL': send_sell_notification,
    }
    func = funcs.get(side)

    return await func(message_body=message_body)


async def process_message(message: aio_pika.IncomingMessage):
    async with message.process(ignore_processed=True):
        message_body = ujson.loads(message.body)
        await send_notification(message_body=message_body)


async def main(aio_loop) -> aio_pika.Connection:
    conn: aio_pika.Connection = await aio_pika.connect_robust(url=AMQP_CONN_STRING,
                                                              loop=aio_loop)

    channel = await conn.channel()
    queue = await channel.declare_queue(name=AMQP_QUEUE,
                                        auto_delete=True)

    await queue.consume(process_message)

    return conn
