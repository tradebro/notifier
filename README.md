# Notifier

Subscribes to a queue and send notifications for buy or sell orders.

## Env Vars

| Name | Description |
| :--- | :--- |
| `TELEGRAM_TOKEN` | Required string |
| `TELEGRAM_CHAT_ID` | Required string |
| `AMQP_CONN_STRING` | Required string |
| `AMQP_QUEUE` | Required string, also known as routing key |
