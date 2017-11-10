from qpython import qconnection


def q_no_credentials():
    return {}


def open_q_connection(host, port, credential=q_no_credentials):
    c = credential() if callable(credential) else credential
    q = qconnection.QConnection(host, port, **c)
    q.open()
    return q


def close_q_connection(q):
    q.close()

    # print(q)
    # print('IPC version: %s. Is connected: %s' % (q.protocol_version, q.is_connected()))
    #
    # # simple query execution via: QConnection.__call__
    # data = q('{`int$ til x}', 10)
    # print('type: %s, numpy.dtype: %s, meta.qtype: %s, data: %s ' % (type(data), data.dtype, data.meta.qtype, data))
    #
    # # simple query execution via: QConnection.sync
    # data = q.sync('{`long$ til x}', 10)
    # print('type: %s, numpy.dtype: %s, meta.qtype: %s, data: %s ' % (type(data), data.dtype, data.meta.qtype, data))
    #
    # # low-level query and read
    # q.query(qconnection.MessageType.SYNC, '{`short$ til x}', 10)  # sends a SYNC query
    # msg = q.receive(data_only=False, raw=False)  # retrieve entire message
    # print('type: %s, message type: %s, data size: %s, is_compressed: %s ' % (
    #     type(msg), msg.type, msg.size, msg.is_compressed))
    # data = msg.data
    # print('type: %s, numpy.dtype: %s, meta.qtype: %s, data: %s ' % (type(data), data.dtype, data.meta.qtype, data))
    # # close connection
    # q.close()
