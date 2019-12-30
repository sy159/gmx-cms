from __future__ import unicode_literals

import functools
import time

import pika


# 同步消息推送类
class RabbitPublisher(object):
    def __init__(self, host, port, vhost, user, password):
        self.host = host  # mq地址
        self.port = port  # 端口
        self.vhost = vhost  # 虚拟环境
        self.user = user  # 用户名
        self.password = password  # 密码
        credentials = pika.PlainCredentials(self.user, self.password)
        self.parameters = pika.ConnectionParameters(host=self.host, port=self.port, virtual_host=self.vhost, credentials=credentials)
        self._connection = None
        self._channel = None

    def _connect(self):
        self._connection = pika.BlockingConnection(self.parameters)
        self._channel = self._connection.channel()

    # 队列绑定exchange
    def on_queue_declare(self, queue, exchange, routing_key=None, arguments=None, callback=None):
        if self._channel is None:
            self._connect()
        try:
            self._channel.queue_bind(queue, exchange, routing_key)
        except Exception as e:
            print(e)
            self._connect()
            self.setup_exchange(exchange)
            self._channel.queue_bind(queue, exchange, routing_key)

    # 设置交换机配置
    def setup_exchange(self, exchange="amq.direct", exchange_type="direct", ack=True):
        if self._channel is None:
            self._connect()
        self._channel.exchange_declare(exchange=exchange,  # 交换机名称
                                       exchange_type=exchange_type,  # 交换机类型
                                       durable=True)  # 交换机是否持久化; 该方法用于声明交换机, 声明多次仅会创建一次
        if ack:
            self._channel.confirm_delivery()  # 在该信道中开启消息手动确认机制

    # 发送消息在队列中
    def send(self, queue_name: str, body: str, exchange="", routing_key=""):
        if self._channel is None:
            self._connect()
        self._channel.queue_declare(queue=queue_name, durable=True)  # 声明一个持久化队列
        if not routing_key:
            routing_key = queue_name
        if exchange:
            self.on_queue_declare(queue_name, exchange, routing_key)
        self._channel.basic_publish(exchange=exchange,
                                    routing_key=routing_key,  # 队列名字
                                    body=body,  # 消息内容
                                    properties=pika.BasicProperties(
                                        delivery_mode=2,  # 消息持久化
                                    ))

    # 清除指定队列的所有的消息
    def purge(self, queue_name):
        self._channel.queue_purge(queue_name)

    # 删除指定队列
    def delete(self, queue_name, if_unused=False, if_empty=False):
        self._channel.queue_delete(queue_name, if_unused=if_unused, if_empty=if_empty)

    # 断开连接
    def stop(self):
        if self._channel is not None:
            self._channel.close()
        if self._connection is not None:
            self._connection.close()


# 异步消息消费类
class RabbitConsumer(object):
    # 消费异常默认的exchange设置（跟消费队列进行绑定配置）
    EXCHANGE = 'amq.direct'
    EXCHANGE_TYPE = 'direct'

    def __init__(self, host, port, vhost, user, password, queue_name, callback_worker, prefetch_count):
        self.host = host
        self.port = port
        self.vhost = vhost
        self.user = user
        self.password = password
        self.QUEUE = queue_name
        self.callback_worker = callback_worker
        self._prefetch_count = prefetch_count
        self.should_reconnect = False
        self.was_consuming = False
        self._connection = None
        self._channel = None
        self._closing = False
        self._consumer_tag = None
        self._consuming = False
        self.ROUTING_KEY = queue_name

    def connect(self):
        credentials = pika.PlainCredentials(self.user, self.password)
        parameters = pika.ConnectionParameters(host=self.host, port=self.port, virtual_host=self.vhost, credentials=credentials)
        return pika.SelectConnection(
            parameters=parameters,
            on_open_callback=self.on_connection_open,
            on_open_error_callback=self.on_connection_open_error,
            on_close_callback=self.on_connection_closed)

    def close_connection(self):
        self._consuming = False
        if self._connection.is_closing or self._connection.is_closed:
            pass
        else:
            self._connection.close()

    def on_connection_open(self, _unused_connection):
        """This method is called by pika once the connection to RabbitMQ has
        been established. It passes the handle to the connection object in
        case we need it, but in this case, we'll just mark it unused.
        :param pika.SelectConnection _unused_connection: The connection
        """
        self.open_channel()

    def on_connection_open_error(self, _unused_connection, err):
        """This method is called by pika if the connection to RabbitMQ
        can't be established.
        :param pika.SelectConnection _unused_connection: The connection
        :param Exception err: The error
        """
        self.reconnect()

    def on_connection_closed(self, _unused_connection, reason):
        """This method is invoked by pika when the connection to RabbitMQ is
        closed unexpectedly. Since it is unexpected, we will reconnect to
        RabbitMQ if it disconnects.
        :param pika.connection.Connection connection: The closed connection obj
        :param Exception reason: exception representing reason for loss of
            connection.
        """
        self._channel = None
        if self._closing:
            self._connection.ioloop.stop()
        else:
            self.reconnect()

    def reconnect(self):
        """Will be invoked if the connection can't be opened or is
        closed. Indicates that a reconnect is necessary then stops the
        ioloop.
        """
        self.should_reconnect = True
        self.stop()

    def open_channel(self):
        """Open a new channel with RabbitMQ by issuing the Channel.Open RPC
        command. When RabbitMQ responds that the channel is open, the
        on_channel_open callback will be invoked by pika.
        """
        self._connection.channel(on_open_callback=self.on_channel_open)

    def on_channel_open(self, channel):
        """This method is invoked by pika when the channel has been opened.
        The channel object is passed in so we can make use of it.
        Since the channel is now open, we'll declare the exchange to use.
        :param pika.channel.Channel channel: The channel object
        """
        self._channel = channel
        self.add_on_channel_close_callback()
        self.setup_exchange(self.EXCHANGE)

    def add_on_channel_close_callback(self):
        """This method tells pika to call the on_channel_closed method if
        RabbitMQ unexpectedly closes the channel.
        """
        self._channel.add_on_close_callback(self.on_channel_closed)

    def on_channel_closed(self, channel, reason):
        """Invoked by pika when RabbitMQ unexpectedly closes the channel.
        Channels are usually closed if you attempt to do something that
        violates the protocol, such as re-declare an exchange or queue with
        different parameters. In this case, we'll close the connection
        to shutdown the object.
        :param pika.channel.Channel: The closed channel
        :param Exception reason: why the channel was closed
        """
        self.close_connection()

    def setup_exchange(self, exchange_name):
        """Setup the exchange on RabbitMQ by invoking the Exchange.Declare RPC
        command. When it is complete, the on_exchange_declareok method will
        be invoked by pika.
        :param str|unicode exchange_name: The name of the exchange to declare
        """
        # Note: using functools.partial is not required, it is demonstrating
        # how arbitrary data can be passed to the callback when it is called
        cb = functools.partial(
            self.on_exchange_declareok, userdata=exchange_name)
        self._channel.exchange_declare(
            exchange=exchange_name,
            exchange_type=self.EXCHANGE_TYPE,
            durable=True,
            callback=cb)

    def on_exchange_declareok(self, _unused_frame, userdata):
        """Invoked by pika when RabbitMQ has finished the Exchange.Declare RPC
        command.
        :param pika.Frame.Method unused_frame: Exchange.DeclareOk response frame
        :param str|unicode userdata: Extra user data (exchange name)
        """
        self.setup_queue(self.QUEUE)

    def setup_queue(self, queue_name):
        """Setup the queue on RabbitMQ by invoking the Queue.Declare RPC
        command. When it is complete, the on_queue_declareok method will
        be invoked by pika.
        :param str|unicode queue_name: The name of the queue to declare.
        """
        cb = functools.partial(self.on_queue_declareok, userdata=queue_name)
        self._channel.queue_declare(queue=queue_name, durable=True, callback=cb)

    def on_queue_declareok(self, _unused_frame, userdata):
        """Method invoked by pika when the Queue.Declare RPC call made in
        setup_queue has completed. In this method we will bind the queue
        and exchange together with the routing key by issuing the Queue.Bind
        RPC command. When this command is complete, the on_bindok method will
        be invoked by pika.
        :param pika.frame.Method _unused_frame: The Queue.DeclareOk frame
        :param str|unicode userdata: Extra user data (queue name)
        """
        queue_name = userdata
        cb = functools.partial(self.on_bindok, userdata=queue_name)
        self._channel.queue_bind(
            queue_name,
            self.EXCHANGE,
            routing_key=self.ROUTING_KEY,
            callback=cb)

    def on_bindok(self, _unused_frame, userdata):
        """Invoked by pika when the Queue.Bind method has completed. At this
        point we will set the prefetch count for the channel.
        :param pika.frame.Method _unused_frame: The Queue.BindOk response frame
        :param str|unicode userdata: Extra user data (queue name)
        """
        self.set_qos()

    def set_qos(self):
        """This method sets up the consumer prefetch to only be delivered
        one message at a time. The consumer must acknowledge this message
        before RabbitMQ will deliver another one. You should experiment
        with different prefetch values to achieve desired performance.
        """
        self._channel.basic_qos(
            prefetch_count=self._prefetch_count, callback=self.on_basic_qos_ok)

    def on_basic_qos_ok(self, _unused_frame):
        """Invoked by pika when the Basic.QoS method has completed. At this
        point we will start consuming messages by calling start_consuming
        which will invoke the needed RPC commands to start the process.
        :param pika.frame.Method _unused_frame: The Basic.QosOk response frame
        """
        self.start_consuming()

    def start_consuming(self):
        """This method sets up the consumer by first calling
        add_on_cancel_callback so that the object is notified if RabbitMQ
        cancels the consumer. It then issues the Basic.Consume RPC command
        which returns the consumer tag that is used to uniquely identify the
        consumer with RabbitMQ. We keep the value to use it when we want to
        cancel consuming. The on_message method is passed in as a callback pika
        will invoke when a message is fully received.
        """
        self.add_on_cancel_callback()
        self._consumer_tag = self._channel.basic_consume(
            self.QUEUE, self.on_message)
        self.was_consuming = True
        self._consuming = True

    def add_on_cancel_callback(self):
        """Add a callback that will be invoked if RabbitMQ cancels the consumer
        for some reason. If RabbitMQ does cancel the consumer,
        on_consumer_cancelled will be invoked by pika.
        """
        self._channel.add_on_cancel_callback(self.on_consumer_cancelled)

    def on_consumer_cancelled(self, method_frame):
        """Invoked by pika when RabbitMQ sends a Basic.Cancel for a consumer
        receiving messages.
        :param pika.frame.Method method_frame: The Basic.Cancel frame
        """
        if self._channel:
            self._channel.close()

    def on_message(self, _unused_channel, basic_deliver, properties, body):
        """Invoked by pika when a message is delivered from RabbitMQ. The
        channel is passed for your convenience. The basic_deliver object that
        is passed in carries the exchange, routing key, delivery tag and
        a redelivered flag for the message. The properties passed in is an
        instance of BasicProperties with the message properties and the body
        is the message that was sent.
        :param pika.channel.Channel _unused_channel: The channel object
        :param pika.Spec.Basic.Deliver: basic_deliver method
        :param pika.Spec.BasicProperties: properties
        :param bytes body: The message body
        """
        self.callback_worker(_unused_channel, basic_deliver, properties, body)  # 执行消费回调函数
        self.acknowledge_message(basic_deliver.delivery_tag)  # ack确认消费

    def acknowledge_message(self, delivery_tag):
        """Acknowledge the message delivery from RabbitMQ by sending a
        Basic.Ack RPC method for the delivery tag.
        :param int delivery_tag: The delivery tag from the Basic.Deliver frame
        """
        self._channel.basic_ack(delivery_tag)

    def stop_consuming(self):
        """Tell RabbitMQ that you would like to stop consuming by sending the
        Basic.Cancel RPC command.
        """
        if self._channel:
            cb = functools.partial(
                self.on_cancelok, userdata=self._consumer_tag)
            self._channel.basic_cancel(self._consumer_tag, cb)

    def on_cancelok(self, _unused_frame, userdata):
        """This method is invoked by pika when RabbitMQ acknowledges the
        cancellation of a consumer. At this point we will close the channel.
        This will invoke the on_channel_closed method once the channel has been
        closed, which will in-turn close the connection.
        :param pika.frame.Method _unused_frame: The Basic.CancelOk frame
        :param str|unicode userdata: Extra user data (consumer tag)
        """
        self._consuming = False
        self.close_channel()

    def close_channel(self):
        """Call to close the channel with RabbitMQ cleanly by issuing the
        Channel.Close RPC command.
        """
        self._channel.close()

    def run(self):
        """Run the example consumer by connecting to RabbitMQ and then
        starting the IOLoop to block and allow the SelectConnection to operate.
        """
        self._connection = self.connect()
        self._connection.ioloop.start()

    def stop(self):
        """Cleanly shutdown the connection to RabbitMQ by stopping the consumer
        with RabbitMQ. When RabbitMQ confirms the cancellation, on_cancelok
        will be invoked by pika, which will then closing the channel and
        connection. The IOLoop is started again because this method is invoked
        when CTRL-C is pressed raising a KeyboardInterrupt exception. This
        exception stops the IOLoop which needs to be running for pika to
        communicate with RabbitMQ. All of the commands issued prior to starting
        the IOLoop will be buffered but not processed.
        """
        if not self._closing:
            self._closing = True
            if self._consuming:
                self.stop_consuming()
                self._connection.ioloop.start()
            else:
                self._connection.ioloop.stop()


# 消费启动重连（消费启动类）
class ReconnectingConsumer(object):
    def __init__(self, host, port, vhost, user, password, queue_name="test", callback_worker=None, prefetch_count=1):
        self.host = host
        self.port = port
        self.vhost = vhost
        self.user = user
        self.password = password
        self.queue_name = queue_name
        self.callback_worker = callback_worker
        self.prefetch_count = prefetch_count
        self._reconnect_delay = 0
        self._consumer = RabbitConsumer(self.host, self.port, self.vhost, self.user, self.password, self.queue_name, self.callback_worker, self.prefetch_count)

    def run(self):
        while True:
            try:
                self._consumer.run()
            except KeyboardInterrupt:
                self._consumer.stop()
                break
            self._maybe_reconnect()

    def _maybe_reconnect(self):
        if self._consumer.should_reconnect:
            self._consumer.stop()
            reconnect_delay = self._get_reconnect_delay()
            time.sleep(reconnect_delay)
            self._consumer = RabbitConsumer(self.host, self.port, self.vhost, self.user, self.password, self.queue_name, self.callback_worker, self.prefetch_count)

    def _get_reconnect_delay(self):
        if self._consumer.was_consuming:
            self._reconnect_delay = 0
        else:
            self._reconnect_delay += 1
        if self._reconnect_delay > 30:
            self._reconnect_delay = 30
        return self._reconnect_delay


# 消费推送使用示例
'''
from mainsys.settings import mq_conf

publisher = RabbitPublisher(mq_conf.get("host"), mq_conf.get("port"), mq_conf.get("vhost"), mq_conf.get("user"), mq_conf.get("pwd"))
publisher.send("test", json.dumps({"data": "test"}))
publisher.stop()
'''

# 消费使用示例
'''
from mainsys.settings import mq_conf

# 消费回调函数(参数跟on_message函数传入的相关，可自行设置)
def test(ch, method, properties, body):
    print(json.loads(body))

consumer = ReconnectingConsumer(mq_conf.get("host"), mq_conf.get("port"), mq_conf.get("vhost"), mq_conf.get("user"), mq_conf.get("pwd"), "test",callback_worker=test)
consumer.run()
'''
