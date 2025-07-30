# SPDX-License-Identifier: MIT
# Copyright (C) 2024 Avnet
# Authors: Nikola Markovic <nikola.markovic@avnet.com> et al.
import json
import traceback
from dataclasses import dataclass, asdict
from datetime import datetime
from json import JSONDecodeError
from typing import Union, Optional

from avnet.iotconnect.sdk.sdklib.error import C2DDecodeError
from avnet.iotconnect.sdk.sdklib.protocol.c2d import ProtocolC2dMessageJson, ProtocolCommandMessageJson, ProtocolOtaUrlJson, ProtocolOtaMessageJson
from avnet.iotconnect.sdk.sdklib.protocol.d2c import ProtocolTelemetryMessageJson, ProtocolTelemetryEntryJson, ProtocolAckMessageJson, ProtocolAckDJson
from avnet.iotconnect.sdk.sdklib.util import dataclass_factory_filter_empty, to_iotconnect_time_str, deserialize_dataclass

# This file contains definitions related to (inbound or outbound) C2D Messages

# When type "object" is defined in IoTConnect, it cannot have nested objects inside of it.
TelemetryValueObjectType = dict[str, Union[None, str, int, float, bool, tuple[float, float]]]
TelemetryValueType = Union[None, str, int, float, bool, tuple[float, float], TelemetryValueObjectType]
TelemetryValues = dict[str, TelemetryValueType]


@dataclass
class TelemetryRecord:
    values: TelemetryValues
    timestamp: datetime = None
    unique_id: str = None
    tag: str = None


class C2dAck:
    """
    OTA Download statuses
    Best practices for OTA status:
    While the final success of the OTA action should be OTA_DOWNLOAD_DONE, it should be generally sent
    only if we are certain that we downloaded the OTA and the new firmware is up and running successfully.
    The user can store the original ACK ID and only report success only after successfully running with the new firmware.
    While the new firmware is downloading over the network or (if available/applicable) writing to the filesystem, unpacking,
    self-testing etc. the intermediate fine-grained statuses along with an appropriate message can be reported
    with the OTA_DOWNLOAD_FAILED status until DONE or FAILED status is reported.
    The exact steps can be left to the interpretation of the user, given the device's capabilities and limitations.
    """

    CMD_FAILED = 1

    CMD_SUCCESS_WITH_ACK = 2

    # OTA download was not attempted or was rejected.
    OTA_FAILED = 1

    # An intermediate step during the firmware update is pending.
    OTA_DOWNLOADING = 2

    # OTA download is fully completed. New firmware is up and running.
    OTA_DOWNLOAD_DONE = 3

    # The download itself, self-test, writing the files, or unpacking or running the downloaded firmware has failed.
    OTA_DOWNLOAD_FAILED = 4

    @classmethod
    def is_valid_cmd_status(cls, status: int) -> bool:
        return status in (C2dAck.CMD_FAILED, C2dAck.CMD_SUCCESS_WITH_ACK)

    @classmethod
    def is_valid_ota_status(cls, status: int) -> bool:
        return status in (C2dAck.OTA_FAILED, C2dAck.OTA_DOWNLOADING, C2dAck.OTA_DOWNLOAD_DONE, C2dAck.OTA_DOWNLOAD_FAILED)


class C2dMessage:
    COMMAND = 0
    OTA = 1
    MODULE_COMMAND = 2
    REFRESH_ATTRIBUTE = 101
    REFRESH_SETTING = 102
    REFRESH_EDGE_RULE = 103
    REFRESH_CHILD_DEVICE = 104
    DATA_FREQUENCY_CHANGE = 105
    DEVICE_DELETED = 106
    DEVICE_DISABLED = 107
    DEVICE_RELEASED = 108
    STOP_OPERATION = 109
    START_HEARTBEAT = 100
    STOP_HEARTBEAT = 111
    UNKNOWN = 9999

    TYPES: dict[int, str, str] = {
        COMMAND: "Command",
        OTA: "OTA Update",
        REFRESH_ATTRIBUTE: "Refresh Attribute",
        REFRESH_SETTING: "Refresh Setting (Twin/Shadow))",
        REFRESH_EDGE_RULE: "Refresh Edge Rule",
        REFRESH_CHILD_DEVICE: "Refresh Child Device",
        DATA_FREQUENCY_CHANGE: "Data Frequency Changed",
        DEVICE_DELETED: "Device Deleted",
        DEVICE_DISABLED: "Device Disabled",
        DEVICE_RELEASED: "Device Released",
        STOP_OPERATION: "Stop Operation",
        START_HEARTBEAT: "Start Heartbeat",
        STOP_HEARTBEAT: "Stop Heartbeat",
        UNKNOWN: "<Unknown Command Received>"
    }

    def __init__(self, packet: ProtocolC2dMessageJson):
        cls = C2dMessage  # shorthand
        self.ct = packet.ct
        self.type_description = cls.TYPES.get(packet.ct)
        if self.type_description is None:
            self.type_description = cls.TYPES[cls.UNKNOWN]
            self.type = cls.UNKNOWN
        else:
            self.type = packet.ct  # this can be None
        self.is_fatal = self.type in (cls.DEVICE_DELETED, cls.DEVICE_DISABLED, cls.DEVICE_RELEASED, cls.STOP_OPERATION)
        self.needs_refresh = self.type in (cls.DATA_FREQUENCY_CHANGE, cls.REFRESH_ATTRIBUTE, cls.REFRESH_SETTING, cls.REFRESH_EDGE_RULE, cls.REFRESH_CHILD_DEVICE)
        self.heartbeat_operation = None
        if self.type == cls.START_HEARTBEAT:
            self.heartbeat_operation = True
        elif self.type == cls.STOP_HEARTBEAT:
            self.heartbeat_operation = False
        self.frequency = packet.f or packet.df  # pick up frequency with respect to DATA_FREQUENCY_CHANGE or Heartbeat

    def validate(self) -> bool:
        return self.type is not None


class C2dCommand:
    def __init__(self, packet: ProtocolCommandMessageJson):
        self.type = C2dMessage.COMMAND  # Used for error checking when sending ACKs
        self.ack_id = packet.ack
        if packet.cmd is not None and len(packet.cmd) > 0:
            cmd_split = packet.cmd.split()
            self.command_name = cmd_split[0]
            self.command_args = cmd_split[1:]
            self.command_raw = packet.cmd
        else:
            self.command_name = None
            self.command_args = []
            self.command_raw = ""

    def validate(self) -> bool:
        return self.command_name is not None


class C2dOta:
    class Url:
        def __init__(self, entry: ProtocolOtaUrlJson):
            self.url = entry.url
            self.file_name = entry.fileName

    def __init__(self, packet: ProtocolOtaMessageJson):
        self.type = C2dMessage.OTA  # Used for error checking when sending ACKs
        self.ack_id = packet.ack
        self.version = packet.sw  # along with OTA superset
        self.hardware_version = packet.hw
        if packet.urls is not None and len(packet.urls) > 0:
            self.urls: list[C2dOta.Url] = [C2dOta.Url(x) for x in packet.urls]
        else:
            # we will let the client handle this case
            self.urls: list[C2dOta.Url] = []

    def validate(self) -> bool:
        if len(self.urls) == 0: return False
        if self.ack_id is None or len(self.ack_id) == 0: return False  # OTA must have ack ID
        for u in self.urls:
            if u is None: return False
            if u.file_name is None or len(u.file_name) == 0: return False
            if u.url is None or len(u.url) == 0: return False
        return True


class C2DDecodeResult:
    """ see decode_c2d_message() for more details """
    def __init__(
            self,
            generic_message: C2dMessage,
            raw_message: dict
    ):
        self.generic_message = generic_message
        self.raw_message = raw_message

        # These will be set later once the generic message is processed:
        self.command: Optional[C2dCommand] = None
        self.ota: Optional[C2dOta] = None



def encode_telemetry_records(records: list[TelemetryRecord], recordset_timestamp: datetime = None) -> str:
    """ Encoded a telemetry packet for a set of telemetry records that should be sent to the back end
    on "RPT" topic.

    See https://docs.iotconnect.io/iotconnect/sdk/message-protocol/device-message-2-1/d2c-messages/#Device for more information.

    :param TelemetryRecord records:
        A set of ordered name-value telemetry pairs (TelemetryValueType)
        with optional individual record timestamps to send. Each TelemetryValueType value can be
            - a primitive value: Maps directly to a JSON string, number or boolean
            - None: Maps to JSON null,
            - Tuple[float, float]: Used to send a lat/long geographic coordinate as decimal degrees as an
                array of two (positive or negative) floats.
                For example, [44.787197, 20.457273] is the geo coordinate Belgrade in Serbia,
                where latitude 44.787197 is a positive number indicating degrees north,
                and longitude a positive number as well, indicating degrees east.
                Maps to JSON array of two elements.
            - Another hash with possible values above when sending an object. Maps to JSON object.
        in case when an object needs to be sent.
    :param datetime recordset_timestamp: (Optional) The timestamp when this set of records was created.
        If not provided, this will save bandwidth, as no timestamp will not be sent over MQTT.
        The server receipt timestamp will be applied to the telemetry values in this telemetry record.
        Supply this value using to_to_iotconnect_time_str() if you need more control over timestamps.
    """
    packet = ProtocolTelemetryMessageJson()
    for r in records:
        packet_entry = ProtocolTelemetryEntryJson(
            d=r.values,
            dt=None if r.timestamp is None else to_iotconnect_time_str(r.timestamp),
            id=r.unique_id,
            tg=r.tag
        )
        packet.d.append(asdict(packet_entry, dict_factory=dataclass_factory_filter_empty))
    if recordset_timestamp is not None:
        packet.dt = to_iotconnect_time_str(recordset_timestamp)
    return json.dumps(asdict(packet, dict_factory=dataclass_factory_filter_empty), separators=(',', ':'))


def encode_single_telemetry_record(values: dict[str, TelemetryValueType], timestamp: datetime = None) -> str:
    """
    Creates a telemetry packet single telemetry dataset that should be sent to the back end
    If you need gateway/child functionality or need to send multiple data sets in one packet,
    use the send_telemetry_records() function.

    See https://docs.iotconnect.io/iotconnect/sdk/message-protocol/device-message-2-1/d2c-messages/#Device for more information.

    :param TelemetryValues values:
        The name-value telemetry pairs to send. Each value can be
            - a primitive value: Maps directly to a JSON string, number or boolean
            - None: Maps to JSON null,
            - Tuple[float, float]: Used to send a lat/long geographic coordinate as decimal degrees as an
                array of two (positive or negative) floats.
                For example, [44.787197, 20.457273] is the geo coordinate Belgrade in Serbia,
                where latitude 44.787197 is a positive number indicating degrees north,
                and longitude a positive number as well, indicating degrees east.
                Maps to JSON array of two elements.
            - Another hash with possible values above when sending an object. Maps to JSON object.
        in case when an object needs to be sent.
    :param datetime timestamp: (Optional) The timestamp when this record was created.
        If not provided, this will save bandwidth, as no timestamp will not be sent over MQTT.
        The server receipt timestamp will be applied to the telemetry values in this telemetry record.
        Supply this value using to_to_iotconnect_time_str() if you need more control over timestamps.

    """

    return encode_telemetry_records([TelemetryRecord(
        values=values,
        timestamp=timestamp
    )])


def encode_c2d_ack(ack_id: str, message_type: int, status: int, message_str: str = None) -> str:
    """
    Send Command acknowledgement for a message received with an ACK ID.

    In order to support any additional future ack status types or message type acknowledgements,
    this function will NOT validate the message type or status type and then
    check whether an inappropriate status was sent for the specified message type.
    For example, sending OTA_DOWNLOAD_FAILED (3) as status of a command will not generate an exception.

    :param ack_id: The ACK ID of the original message that was received.
    :param message_type: The message type ("ct") of the original message that was received.
    :param status: C2dAck.CMD_FAILED or C2dAck.CMD_SUCCESS_WITH_ACK.
    :param message_str: (Optional) For example: 'LED color now "blue"', or 'LED color "red" not supported'.
"""
    packet = ProtocolAckMessageJson(
        d=ProtocolAckDJson(
            ack=ack_id,
            type=message_type,
            st=status,
            msg=message_str
        )
    )
    return json.dumps(asdict(packet, dict_factory=dataclass_factory_filter_empty), separators=(',', ':'))


def decode_c2d_message(payload: str) -> C2DDecodeResult:
    """
    Deserializes a C2D message that arrived to the "CMD" topic.

    The result will contain the "generic" message with properties that any message can have
    and either the "command" or the "OTA" specific message that will be parsed and checked for errror.
    """
    try:
        # use the simplest form of ProtocolC2dMessageJson when deserializing first and
        # convert message to appropriate one later
        raw_message = json.loads(payload)
        message_packet = deserialize_dataclass(ProtocolC2dMessageJson, raw_message)
        message = C2dMessage(message_packet)

        if not message.validate():
            raise C2DDecodeError("C2D Message is invalid: %s" % payload)

        ret = C2DDecodeResult(message, raw_message)

        if message.type == C2dMessage.COMMAND:
            command = C2dCommand(deserialize_dataclass(ProtocolCommandMessageJson, raw_message))
            if not command.validate():
                raise C2DDecodeError("C2D Command is invalid: %s" % payload)
            ret.command = command
        elif message.type == C2dMessage.OTA:
            ota = C2dOta(deserialize_dataclass(ProtocolOtaMessageJson, raw_message))
            if not ota.validate():
                raise C2DDecodeError("C2D OTA message is invalid: %s" % payload)
            if len(ota.urls) == 0:
                raise C2DDecodeError("C2D OTA message has no URLs: %s" % payload)
            ret.ota = ota

        return ret
    except JSONDecodeError as ex:
        raise C2DDecodeError(ex.msg)
