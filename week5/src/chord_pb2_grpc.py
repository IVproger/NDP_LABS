# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import chord_pb2 as chord__pb2


class ChordStub(object):
    """The Chord service definition
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.SaveData = channel.unary_unary(
                '/Chord/SaveData',
                request_serializer=chord__pb2.SaveDataMessage.SerializeToString,
                response_deserializer=chord__pb2.DataResponse.FromString,
                )
        self.RemoveData = channel.unary_unary(
                '/Chord/RemoveData',
                request_serializer=chord__pb2.RemoveDataMessage.SerializeToString,
                response_deserializer=chord__pb2.DataResponse.FromString,
                )
        self.FindData = channel.unary_unary(
                '/Chord/FindData',
                request_serializer=chord__pb2.FindDataMessage.SerializeToString,
                response_deserializer=chord__pb2.FindDataResponse.FromString,
                )
        self.GetFingerTable = channel.unary_unary(
                '/Chord/GetFingerTable',
                request_serializer=chord__pb2.GetFingerTableMessage.SerializeToString,
                response_deserializer=chord__pb2.FingerTableResponse.FromString,
                )


class ChordServicer(object):
    """The Chord service definition
    """

    def SaveData(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def RemoveData(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def FindData(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetFingerTable(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_ChordServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'SaveData': grpc.unary_unary_rpc_method_handler(
                    servicer.SaveData,
                    request_deserializer=chord__pb2.SaveDataMessage.FromString,
                    response_serializer=chord__pb2.DataResponse.SerializeToString,
            ),
            'RemoveData': grpc.unary_unary_rpc_method_handler(
                    servicer.RemoveData,
                    request_deserializer=chord__pb2.RemoveDataMessage.FromString,
                    response_serializer=chord__pb2.DataResponse.SerializeToString,
            ),
            'FindData': grpc.unary_unary_rpc_method_handler(
                    servicer.FindData,
                    request_deserializer=chord__pb2.FindDataMessage.FromString,
                    response_serializer=chord__pb2.FindDataResponse.SerializeToString,
            ),
            'GetFingerTable': grpc.unary_unary_rpc_method_handler(
                    servicer.GetFingerTable,
                    request_deserializer=chord__pb2.GetFingerTableMessage.FromString,
                    response_serializer=chord__pb2.FingerTableResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'Chord', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class Chord(object):
    """The Chord service definition
    """

    @staticmethod
    def SaveData(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/Chord/SaveData',
            chord__pb2.SaveDataMessage.SerializeToString,
            chord__pb2.DataResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def RemoveData(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/Chord/RemoveData',
            chord__pb2.RemoveDataMessage.SerializeToString,
            chord__pb2.DataResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def FindData(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/Chord/FindData',
            chord__pb2.FindDataMessage.SerializeToString,
            chord__pb2.FindDataResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetFingerTable(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/Chord/GetFingerTable',
            chord__pb2.GetFingerTableMessage.SerializeToString,
            chord__pb2.FingerTableResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
