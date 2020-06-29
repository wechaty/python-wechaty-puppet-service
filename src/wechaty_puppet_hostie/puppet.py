"""
Python Wechaty - https://github.com/wechaty/python-wechaty

Authors:    Huan LI (李卓桓) <https://github.com/huan>
            Jingjing WU (吴京京) <https://github.com/wj-Mcat>

2020-now @ Copyright Wechaty

Licensed under the Apache License, Version 2.0 (the 'License');
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an 'AS IS' BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
from __future__ import annotations

import json
from typing import Optional, List
import requests

from chatie_grpc.wechaty import (  # type: ignore
    PuppetStub,
)
# pylint: disable=E0401
from grpclib.client import Channel
# pylint: disable=E0401
from pyee import AsyncIOEventEmitter  # type: ignore

from wechaty_puppet import (  # type: ignore
    EventScanPayload,
    ScanStatus,

    EventReadyPayload,

    EventDongPayload,
    EventRoomTopicPayload,
    EventRoomLeavePayload,
    EventRoomJoinPayload,
    EventRoomInvitePayload,

    EventMessagePayload,
    EventLogoutPayload,
    EventLoginPayload,
    EventFriendshipPayload,
    EventHeartbeatPayload,
    EventErrorPayload,
    FileBox, RoomMemberPayload, RoomPayload, RoomInvitationPayload,
    RoomQueryFilter, FriendshipPayload, ContactPayload, MessagePayload,
    MessageQueryFilter,

    ImageType,
    EventType,
    MessageType,
    Puppet,
    PuppetOptions,
    MiniProgramPayload,
    UrlLinkPayload,

    get_logger
)

from .config import (
    WECHATY_PUPPET_HOSTIE_TOKEN,
    WECHATY_PUPPET_HOSTIE_ENDPOINT
)

log = get_logger('HostiePuppet')


def _map_message_type(message_payload: MessagePayload) -> MessagePayload:
    """
    get messageType value which is ts-wechaty-puppet type from hostie server,
        but is MessageType. so we should map it to MessageType from chatie-grpc
    target MessageType Enum:
        MESSAGE_TYPE_UNSPECIFIED  = 0;

       MESSAGE_TYPE_ATTACHMENT   = 1;
       MESSAGE_TYPE_AUDIO        = 2;
       MESSAGE_TYPE_CONTACT      = 3;
       MESSAGE_TYPE_EMOTICON     = 4;
       MESSAGE_TYPE_IMAGE        = 5;
       MESSAGE_TYPE_TEXT         = 6;
       MESSAGE_TYPE_VIDEO        = 7;
       MESSAGE_TYPE_CHAT_HISTORY = 8;
       MESSAGE_TYPE_LOCATION     = 9;
       MESSAGE_TYPE_MINI_PROGRAM = 10;
       MESSAGE_TYPE_TRANSFER     = 11;
       MESSAGE_TYPE_RED_ENVELOPE = 12;
       MESSAGE_TYPE_RECALLED     = 13;
       MESSAGE_TYPE_URL          = 14;

    source MessageType Enum:
        export enum MessageType {
          Unknown = 0,

          Attachment=1,     // Attach(6),
          Audio=2,          // Audio(1), Voice(34)
          Contact=3,        // ShareCard(42)
          ChatHistory=4,    // ChatHistory(19)
          Emoticon=5,       // Sticker: Emoticon(15), Emoticon(47)
          Image=6,          // Img(2), Image(3)
          Text=7,           // Text(1)
          Location=8,       // Location(48)
          MiniProgram=9,    // MiniProgram(33)
          GroupNote=10,      // GroupNote(53)
          Transfer=11,       // Transfers(2000)
          RedEnvelope=12,    // RedEnvelopes(2001)
          Recalled=13,       // Recalled(10002)
          Url=14,            // Url(5)
          Video=15,          // Video(4), Video(43)
        }
    :return:

    #
    """
    if isinstance(message_payload.type, int):
        map_container: List[MessageType] = [
            MessageType.MESSAGE_TYPE_UNSPECIFIED,
            MessageType.MESSAGE_TYPE_ATTACHMENT,
            MessageType.MESSAGE_TYPE_AUDIO,
            MessageType.MESSAGE_TYPE_CONTACT,
            MessageType.MESSAGE_TYPE_CHAT_HISTORY,
            MessageType.MESSAGE_TYPE_EMOTICON,
            MessageType.MESSAGE_TYPE_IMAGE,
            MessageType.MESSAGE_TYPE_TEXT,
            MessageType.MESSAGE_TYPE_LOCATION,
            MessageType.MESSAGE_TYPE_MINI_PROGRAM,
            MessageType.MESSAGE_TYPE_UNSPECIFIED,
            MessageType.MESSAGE_TYPE_TRANSFER,
            MessageType.MESSAGE_TYPE_RED_ENVELOPE,
            MessageType.MESSAGE_TYPE_RECALLED,
            MessageType.MESSAGE_TYPE_URL,
            MessageType.MESSAGE_TYPE_VIDEO]
        message_payload.type = map_container[message_payload.type]
    return message_payload


# pylint: disable=R0904
class HostiePuppet(Puppet):
    """
    grpc wechaty puppet implementation
    """

    def __init__(self, options: PuppetOptions, name: str = 'hostie_puppet'):
        super(HostiePuppet, self).__init__(options, name)

        if options.token is None:
            if WECHATY_PUPPET_HOSTIE_TOKEN is None:
                raise Exception('wechaty-puppet-hostie: token not found.')
            options.token = WECHATY_PUPPET_HOSTIE_TOKEN

        if options.end_point is None \
                and WECHATY_PUPPET_HOSTIE_ENDPOINT is not None:
            options.end_point = WECHATY_PUPPET_HOSTIE_ENDPOINT

        self.channel: Optional[Channel] = None
        self.puppet_stub: Optional[PuppetStub] = None

        self._event_stream: AsyncIOEventEmitter = AsyncIOEventEmitter()

        self.login_user_id: Optional[str] = None

    async def room_list(self) -> List[str]:
        """
        get all room list
        :return:
        """
        if self.puppet_stub is None:
            raise Exception('puppet_stub should not be none')
        response = await self.puppet_stub.room_list()
        if response is None:
            raise ValueError('can"t get room_list response')
        return response.ids

    async def message_image(self, message_id: str, image_type: ImageType
                            ) -> FileBox:
        """
        get message image data
        :param message_id:
        :param image_type:
        :return:
        """
        if self.puppet_stub is None:
            raise Exception('puppet_stub should not be none')
        response = await self.puppet_stub.message_image(
            id=message_id,
            type=image_type)
        if response is None:
            # TODO -> need to refactor the raised error
            raise ValueError('response is invalid')
        json_response = json.loads(response.filebox)
        return FileBox.from_json(obj=json_response)

    def on(self, event_name: str, caller):
        """
        listen event from the wechaty
        :param event_name:
        :param caller:
        :return:
        """
        # TODO -> if the event is listened twice, how to handle this problem
        self._event_stream.on(event_name, caller)

    def listener_count(self, event_name: str) -> int:
        """
        how to get event count
        :param event_name:
        :return:
        """
        listeners = self._event_stream.listeners(event_name)
        return len(listeners)

    async def contact_list(self) -> List[str]:
        """
        get contact list
        :return:
        """
        if self.puppet_stub is None:
            raise Exception('puppet_stub should not be none')
        response = await self.puppet_stub.contact_list()
        if response is None:
            # TODO -> need to refactor the raised error
            raise ValueError('response is invalid')
        return response.ids

    async def tag_contact_delete(self, tag_id: str) -> None:
        """
        delete some tag
        :param tag_id:
        :return:
        """
        if self.puppet_stub is None:
            raise Exception('puppet_stub should not be none')
        await self.puppet_stub.tag_contact_delete(id=tag_id)
        return None

    async def tag_favorite_delete(self, tag_id: str) -> None:
        """
        delete tag favorite
        :param tag_id:
        :return:
        """
        # chatie_grpc has not implement this function
        return None

    async def tag_contact_add(self, tag_id: str, contact_id: str):
        """
        add a tag to contact
        :param tag_id:
        :param contact_id:
        :return:
        """
        if self.puppet_stub is None:
            raise Exception('puppet_stub should not be none')
        await self.puppet_stub.tag_contact_add(
            id=tag_id, contact_id=contact_id)

    async def tag_favorite_add(self, tag_id: str, contact_id: str):
        """
        add a tag to favorite
        :param tag_id:
        :param contact_id:
        :return:
        """
        # chatie_grpc has not implement this function

    async def tag_contact_remove(self, tag_id: str, contact_id: str):
        """
        remove a tag from contact
        :param tag_id:
        :param contact_id:
        :return:
        """
        if self.puppet_stub is None:
            raise Exception('puppet_stub should not be none')
        await self.puppet_stub.tag_contact_remove(
            id=tag_id,
            contact_id=contact_id)

    async def tag_contact_list(self, contact_id: Optional[str] = None
                               ) -> List[str]:
        """
        get tag list from a contact
        :param contact_id:
        :return:
        """
        if self.puppet_stub is None:
            raise Exception('puppet_stub should not be none')
        response = await self.puppet_stub.tag_contact_list(
            contact_id=contact_id)
        return response.ids

    async def message_send_text(self, conversation_id: str, message: str,
                                mention_ids: List[str] = None) -> str:
        """
        send text message
        :param conversation_id:
        :param message:
        :param mention_ids:
        :return:
        """
        if self.puppet_stub is None:
            raise Exception('puppet_stub should not be none')
        response = await self.puppet_stub.message_send_text(
            conversation_id=conversation_id,
            text=message, mentonal_ids=mention_ids)
        return response.id

    async def message_send_contact(self, contact_id: str,
                                   conversation_id: str) -> str:
        """
        send contact message
        :param contact_id:
        :param conversation_id:
        :return:
        """
        if self.puppet_stub is None:
            raise Exception('puppet_stub should not be none')
        response = await self.puppet_stub.message_send_contact(
            conversation_id=conversation_id,
            contact_id=contact_id
        )
        return response.id

    async def message_send_file(self, conversation_id: str,
                                file: FileBox) -> str:
        """
        send file message
        :param conversation_id:
        :param file:
        :return:
        """
        if self.puppet_stub is None:
            raise Exception('puppet_stub should not be none')
        response = await self.puppet_stub.message_send_file(
            conversation_id=conversation_id,
            filebox=file.to_json_str()
        )
        return response.id

    async def message_send_url(self, conversation_id: str, url: str) -> str:
        """
        send url message
        :param conversation_id:
        :param url:
        :return:
        """
        if self.puppet_stub is None:
            raise Exception('puppet_stub should not be none')
        response = await self.puppet_stub.message_send_url(
            conversation_id=conversation_id,
            url_link=url
        )
        return response.id

    async def message_send_mini_program(self, conversation_id: str,
                                        mini_program: MiniProgramPayload
                                        ) -> str:
        """
        send mini_program message
        :param conversation_id:
        :param mini_program:
        :return:
        """
        if self.puppet_stub is None:
            raise Exception('puppet_stub should not be none')
        response = await self.puppet_stub.message_send_mini_program(
            conversation_id=conversation_id,
            # TODO -> check mini_program key
            mini_program=mini_program.thumb_url
        )
        return response.id

    async def message_search(self, query: Optional[MessageQueryFilter] = None
                             ) -> List[str]:
        """
        # TODO -> this function should not be here ?
        :param query:
        :return:
        """
        return []

    async def message_recall(self, message_id: str) -> bool:
        """
        recall the message
        :param message_id:
        :return:
        """
        if self.puppet_stub is None:
            raise Exception('puppet_stub should not be none')
        response = await self.puppet_stub.message_recall(id=message_id)
        return response.success

    async def message_payload(self, message_id: str) -> MessagePayload:
        """
        get message payload
        :param message_id:
        :return:
        """
        if self.puppet_stub is None:
            raise Exception('puppet_stub should not be none')
        response = await self.puppet_stub.message_payload(id=message_id)

        return _map_message_type(response)

    async def message_forward(self, to_id: str, message_id: str):
        """
        forward the message
        :param to_id:
        :param message_id:
        :return:
        """
        # TODO -> we should get the type of the message, and forward the message
        # to different conversation_id
        # await self.puppet_stub.message_send_mini_program()

    async def message_file(self, message_id: str) -> FileBox:
        """
        extract file from message
        :param message_id:
        :return:
        """
        if self.puppet_stub is None:
            raise Exception('puppet_stub should not be none')
        response = await self.puppet_stub.message_file(id=message_id)
        json_response = json.loads(response.filebox)
        if 'base64' not in json_response:
            raise Exception('file response data structure is not correct')
        file_box = FileBox.from_base64(
            json_response['base64'],
            name=json_response['name']
        )
        return file_box

    async def message_contact(self, message_id: str) -> str:
        """
        extract
        :param message_id:
        :return:
        """
        if self.puppet_stub is None:
            raise Exception('puppet_stub should not be none')
        response = await self.puppet_stub.message_contact(id=message_id)
        return response.id

    async def message_url(self, message_id: str) -> UrlLinkPayload:
        """
        extract url
        :param message_id:
        :return:
        """
        if self.puppet_stub is None:
            raise Exception('puppet_stub should not be none')
        response = await self.puppet_stub.message_url(id=message_id)
        return UrlLinkPayload(url=response.url_link)

    async def message_mini_program(self, message_id: str) -> MiniProgramPayload:
        """
        extract mini_program from message
        :param message_id:
        :return:
        """
        # TODO -> need to MiniProgram
        # response = await self.puppet_stub.message_mini_program(id=message_id)
        # return MiniProgramPayload(response.mini_program)
        return MiniProgramPayload()

    async def contact_alias(self, contact_id: str, alias: Optional[str] = None
                            ) -> str:
        """
        get/set contact alias
        :param contact_id:
        :param alias:
        :return:
        """
        if self.puppet_stub is None:
            raise Exception('puppet_stub should not be none')
        response = await self.puppet_stub.contact_alias(
            id=contact_id, alias=alias)
        if response.alias is None and alias is None:
            raise ValueError('can"t get contact<%s> alias' % contact_id)
        return response.alias

    async def contact_payload_dirty(self, contact_id: str):
        """
        # TODO this function has not been implement in chatie_grpc
        :param contact_id:
        :return:
        """

    async def contact_payload(self, contact_id: str) -> ContactPayload:
        """
        get contact payload
        :param contact_id:
        :return:
        """
        if self.puppet_stub is None:
            raise Exception('puppet_stub should not be none')
        response = await self.puppet_stub.contact_payload(id=contact_id)
        return response

    async def contact_avatar(self, contact_id: str,
                             file_box: Optional[FileBox] = None) -> FileBox:
        """
        get/set contact avatar
        :param contact_id:
        :param file_box:
        :return:
        """
        if self.puppet_stub is None:
            raise Exception('puppet_stub should not be none')
        response = await self.puppet_stub.contact_avatar(
            id=contact_id, filebox=file_box)
        return FileBox.from_base64(response.filebox)

    async def contact_tag_ids(self, contact_id: str) -> List[str]:
        """
        get contact tags
        :param contact_id:
        :return:
        """
        if self.puppet_stub is None:
            raise Exception('puppet_stub should not be none')
        response = await self.puppet_stub.tag_contact_list(
            contact_id=contact_id)
        return response.ids

    def self_id(self) -> str:
        """
        # TODO -> how to get self_id, nwo wechaty has save login_user
            contact_id
        :return:
        """
        return ''

    async def friendship_search(self, weixin: Optional[str] = None,
                                phone: Optional[str] = None) -> Optional[str]:
        """
        search friendship by wexin/phone
        :param weixin:
        :param phone:
        :return:
        """
        if self.puppet_stub is None:
            raise Exception('puppet_stub should not be none')

        if weixin is not None:
            weixin_response = await self.puppet_stub.friendship_search_weixin(
                weixin=weixin
            )
            if weixin_response is not None:
                return weixin_response.contact_id
        if phone is not None:
            phone_response = await self.puppet_stub.friendship_search_phone(
                phone=phone
            )
            if phone is not None:
                return phone_response.contact_id
        return None

    async def friendship_add(self, contact_id: str, hello: str):
        """
        try to add friendship
        :param contact_id:
        :param hello:
        :return:
        """
        if self.puppet_stub is None:
            raise Exception('puppet_stub should not be none')
        await self.puppet_stub.friendship_add(
            contact_id=contact_id,
            hello=hello
        )

    async def friendship_payload(self, friendship_id: str,
                                 payload: Optional[FriendshipPayload] = None
                                 ) -> FriendshipPayload:
        """
        get/set friendship payload
        :param friendship_id:
        :param payload:
        :return:
        """
        if self.puppet_stub is None:
            raise Exception('puppet_stub should not be none')
        response = await self.puppet_stub.friendship_payload(
            id=friendship_id, payload=json.dumps(payload)
        )
        return response

    async def friendship_accept(self, friendship_id: str):
        """
        accept friendship
        :param friendship_id:
        :return:
        """
        if self.puppet_stub is None:
            raise Exception('puppet_stub should not be none')
        await self.puppet_stub.friendship_accept(id=friendship_id)

    async def room_create(self, contact_ids: List[str], topic: str = None
                          ) -> str:
        """
        create room
        :param contact_ids:
        :param topic:
        :return: created room_id
        """
        if self.puppet_stub is None:
            raise Exception('puppet_stub should not be none')
        response = await self.puppet_stub.room_create(
            contact_ids=contact_ids,
            topic=topic
        )
        return response.id

    async def room_search(self, query: RoomQueryFilter = None) -> List[str]:
        """
        find the room_ids
        search room
        :param query:
        :return:
        """
        if self.puppet_stub is None:
            raise Exception('puppet_stub should not be none')
        room_list_response = await self.puppet_stub.room_list()
        return room_list_response.ids

    async def room_invitation_payload(self,
                                      room_invitation_id: str,
                                      payload: Optional[RoomInvitationPayload]
                                      = None) -> RoomInvitationPayload:
        """
        get room_invitation_payload
        """
        if self.puppet_stub is None:
            raise Exception('puppet_stub should not be none')
        response = await self.puppet_stub.room_invitation_payload(
            id=room_invitation_id,
            payload=payload
        )
        return RoomInvitationPayload(**response.to_dict())

    async def room_invitation_accept(self, room_invitation_id: str):
        """
        accept the room invitation
        :param room_invitation_id:
        :return:
        """
        if self.puppet_stub is None:
            raise Exception('puppet_stub should not be none')
        await self.puppet_stub.room_invitation_accept(id=room_invitation_id)

    async def contact_self_qr_code(self) -> str:
        """
        :return:
        """
        if self.puppet_stub is None:
            raise Exception('puppet_stub should not be none')

        response = await self.puppet_stub.contact_self_q_r_code()
        return response.qrcode

    async def contact_self_name(self, name: str):
        """
        set the name of the contact
        :param name:
        :return:
        """
        if self.puppet_stub is None:
            raise Exception('puppet_stub should not be none')
        await self.puppet_stub.contact_self_name(name=name)

    async def contact_signature(self, signature: str):
        """

        :param signature:
        :return:
        """

    async def room_validate(self, room_id: str) -> bool:
        """

        :param room_id:
        :return:
        """

    async def room_payload_dirty(self, room_id: str):
        """

        :param room_id:
        :return:
        """

    async def room_member_payload_dirty(self, room_id: str):
        """

        :param room_id:
        :return:
        """

    async def room_payload(self, room_id: str) -> RoomPayload:
        """

        :param room_id:
        :return:
        """
        if self.puppet_stub is None:
            raise Exception('puppet_stub should not be none')
        response = await self.puppet_stub.room_payload(id=room_id)
        return response

    async def room_members(self, room_id: str) -> List[str]:
        """

        :param room_id:
        :return:
        """
        if self.puppet_stub is None:
            raise Exception('puppet_stub should not be none')
        response = await self.puppet_stub.room_member_list(id=room_id)
        return response.member_ids

    async def room_add(self, room_id: str, contact_id: str):
        """
        add contact to room
        :param room_id:
        :param contact_id:
        :return:
        """
        if self.puppet_stub is None:
            raise Exception('puppet_stub should not be none')
        await self.puppet_stub.room_add(id=room_id, contact_id=contact_id)

    async def room_delete(self, room_id: str, contact_id: str):
        """
        delete contact from room
        :param room_id:
        :param contact_id:
        :return:
        """
        if self.puppet_stub is None:
            raise Exception('puppet_stub should not be none')
        await self.puppet_stub.room_del(id=room_id, contact_id=contact_id)

    async def room_quit(self, room_id: str):
        """
        quit from room
        :param room_id:
        :return:
        """
        if self.puppet_stub is None:
            raise Exception('puppet_stub should not be none')
        await self.puppet_stub.room_quit(id=room_id)

    async def room_topic(self, room_id: str, new_topic: str):
        """
        set/set topic of the room
        :param room_id:
        :param new_topic:
        :return:
        """
        if self.puppet_stub is None:
            raise Exception('puppet_stub should not be none')
        await self.puppet_stub.room_topic(id=room_id, topic=new_topic)

    async def room_announce(self, room_id: str,
                            announcement: str = None) -> str:
        """
        get/set announce
        :param room_id:
        :param announcement:
        :return:
        """
        if self.puppet_stub is None:
            raise Exception('puppet_stub should not be none')
        room_announce_response = await self.puppet_stub.room_announce(
            id=room_id, text=announcement)
        if announcement is None and room_announce_response.text is not None:
            # get the announcement
            return room_announce_response.text
        if announcement is not None and room_announce_response.text is None:
            return announcement
        return ''

    async def room_qr_code(self, room_id: str) -> str:
        """
        get room qr_code
        :param room_id:
        :return:
        """
        if self.puppet_stub is None:
            raise Exception('puppet_stub should not be none')

        room_qr_code_response = await \
            self.puppet_stub.room_q_r_code(id=room_id)
        return room_qr_code_response.qrcode

    async def room_member_payload(self, room_id: str,
                                  contact_id: str) -> RoomMemberPayload:
        """
        get room member payload
        :param room_id:
        :param contact_id:
        :return:
        """
        if self.puppet_stub is None:
            raise Exception('puppet_stub should not be none')

        member_payload = await self.puppet_stub.room_member_payload(
            id=room_id, member_id=contact_id)
        return member_payload

    async def room_avatar(self, room_id: str) -> FileBox:
        """
        get room avatar
        :param room_id:
        :return:
        """
        if self.puppet_stub is None:
            raise Exception('puppet_stub should not be none')
        room_avatar_response = await self.puppet_stub.room_avatar(id=room_id)

        file_box_data = json.loads(room_avatar_response.filebox)

        if 'remoteUrl' not in file_box_data:
            raise Exception('invalid room avatar response')

        file_box = FileBox.from_url(
            url=file_box_data['remoteUrl'],
            name=f'avatar-{room_id}.jpeg'
        )
        return file_box

    def _init_puppet(self):
        """
        start puppet channel contact_self_qr_code
        """
        log.info('init puppet')
        port = 8788
        if self.options.end_point is None:
            response = requests.get(
                f'https://api.chatie.io/v0/hosties/{self.options.token}'
            )

            if response.status_code != 200:
                raise Exception('hostie server is invalid ... ')

            data = response.json()
            if 'ip' not in data or data['ip'] == '0.0.0.0':
                raise Exception("can't find hostie server address")
            if 'port' in data:
                port = data['port']
            log.debug('get puppet ip address : <%s>', data)
            self.options.end_point = data['ip']
        log.info('init puppet hostie')

        self.channel = Channel(host=self.options.end_point, port=port)
        self.puppet_stub = PuppetStub(self.channel)

    async def start(self) -> None:
        """
        start puppet_stub
        :return:
        """
        self._init_puppet()

        if self.puppet_stub is None:
            raise Exception('puppet_stub should not be none')

        log.info('starting the puppet ...')
        await self.puppet_stub.start()
        log.info('puppet has started ...')
        await self._listen_for_event()
        return None

    async def stop(self):
        """
        stop the grpc channel connection
        """
        log.info('stop()')
        self._event_stream.remove_all_listeners()
        await self.puppet_stub.stop()
        await self.channel.close()

        self.puppet_stub = None
        self.channel = None

    async def logout(self):
        """
        logout the account
        :return:
        """
        log.info('logout()')
        if self.login_user_id is None:
            raise Exception('logout before login?')

        try:
            await self.puppet_stub.logout()
        # pylint: disable=W0703
        except Exception as exception:
            log.error('logout() rejection %s', exception)
        finally:
            payload = EventLogoutPayload(contact_id=self.login_user_id)
            self._event_stream.emit('logout', payload)
            self.login_user_id = None

    async def login(self):
        """
        login the account
        :return:
        """

    async def ding(self, data: Optional[str] = ''):
        """
        set the ding event
        :param data:
        :return:
        """
        log.debug('send ding info to hostie ...')

        if self.puppet_stub is None:
            raise Exception('puppet_stub should not be none')
        await self.puppet_stub.ding(data=data)

    # pylint: disable=R0912,R0915
    async def _listen_for_event(self):
        """
        listen event from hostie with heartbeat
        """
        # listen event from grpclib
        log.info('listening the event from the puppet ...')
        if self.puppet_stub is None:
            raise Exception('puppet_stub should not be none')

        async for response in self.puppet_stub.event():
            if response is not None:
                payload_data: dict = json.loads(response.payload)
                if response.type == int(EventType.EVENT_TYPE_SCAN):
                    log.debug('receive scan info <%s>', payload_data)
                    # create qr_code
                    payload = EventScanPayload(
                        status=ScanStatus(payload_data['status']),
                        qrcode=payload_data.get('qrcode', None),
                        data=payload_data.get('data', None)
                    )
                    self._event_stream.emit('scan', payload)

                elif response.type == int(EventType.EVENT_TYPE_DONG):
                    log.debug('receive dong info <%s>', payload_data)
                    payload = EventDongPayload(**payload_data)
                    self._event_stream.emit('dong', payload)

                elif response.type == int(EventType.EVENT_TYPE_MESSAGE):
                    # payload = get_message_payload_from_response(response)
                    log.debug('receive message info <%s>', payload_data)
                    event_message_payload = EventMessagePayload(
                        message_id=payload_data['messageId'])
                    self._event_stream.emit('message', event_message_payload)

                elif response.type == int(EventType.EVENT_TYPE_HEARTBEAT):
                    log.debug('receive heartbeat info <%s>', payload_data)
                    # Huan(202005) FIXME:
                    #   https://github.com/wechaty/python-wechaty-puppet/issues/6
                    #   Workaround for unexpected server json payload key: timeout
                    # if 'timeout' in payload_data:
                    #     del payload_data['timeout']
                    payload_data = {'data': payload_data['data']}
                    payload = EventHeartbeatPayload(**payload_data)
                    self._event_stream.emit('heartbeat', payload)

                elif response.type == int(EventType.EVENT_TYPE_ERROR):
                    log.info('receive error info <%s>', payload_data)
                    payload = EventErrorPayload(**payload_data)
                    self._event_stream.emit('error', payload)

                elif response.type == int(EventType.EVENT_TYPE_FRIENDSHIP):
                    log.debug('receive friendship info <%s>', payload_data)
                    payload = EventFriendshipPayload(
                        friendship_id=payload_data.get('friendshipId')
                    )
                    self._event_stream.emit('friendship', payload)

                elif response.type == int(EventType.EVENT_TYPE_ROOM_JOIN):
                    log.debug('receive room-join info <%s>', payload_data)
                    payload = EventRoomJoinPayload(
                        invited_ids=payload_data.get('inviteeIdList', []),
                        inviter_id=payload_data.get('inviterId'),
                        room_id=payload_data.get('roomId'),
                        time_stamp=payload_data.get('timestamp')
                    )
                    self._event_stream.emit('room-join', payload)

                elif response.type == int(EventType.EVENT_TYPE_ROOM_INVITE):
                    log.debug('receive room-invite info <%s>', payload_data)
                    payload = EventRoomInvitePayload(
                        room_invitation_id=payload_data.get(
                            'roomInvitationId', None)
                    )
                    self._event_stream.emit('room-invite', payload)

                elif response.type == int(EventType.EVENT_TYPE_ROOM_LEAVE):
                    log.debug('receive room-leave info <%s>', payload_data)
                    payload = EventRoomLeavePayload(
                        removed_ids=payload_data.get('removeeIdList', []),
                        remover_id=payload_data.get('removerId'),
                        room_id=payload_data.get('removerId'),
                        time_stamp=payload_data.get('timestamp')
                    )
                    self._event_stream.emit('room-leave', payload)

                elif response.type == int(EventType.EVENT_TYPE_ROOM_TOPIC):
                    log.debug('receive room-topic info <%s>', payload_data)
                    payload = EventRoomTopicPayload(
                        changer_id=payload_data.get('changerId'),
                        new_topic=payload_data.get('newTopic'),
                        old_topic=payload_data.get('oldTopic'),
                        room_id=payload_data.get('roomId'),
                        time_stamp=payload_data.get('timestamp')
                    )
                    self._event_stream.emit('room-topic', payload)

                elif response.type == int(EventType.EVENT_TYPE_READY):
                    log.debug('receive ready info <%s>', payload_data)
                    payload = EventReadyPayload(**payload_data)
                    self._event_stream.emit('ready', payload)

                elif response.type == int(EventType.EVENT_TYPE_LOGIN):
                    log.debug('receive login info <%s>', payload_data)
                    event_login_payload = EventLoginPayload(
                        contact_id=payload_data['contactId'])
                    self.login_user_id = payload_data.get('contactId', None)
                    self._event_stream.emit('login', event_login_payload)

                elif response.type == int(EventType.EVENT_TYPE_LOGOUT):
                    log.debug('receive logout info <%s>', payload_data)
                    payload = EventLogoutPayload(
                        contact_id=payload_data['contactId'],
                        data=payload_data.get('data', None)
                    )
                    self.login_user_id = None
                    self._event_stream.emit('logout', payload)

                elif response.type == int(EventType.EVENT_TYPE_UNSPECIFIED):
                    pass
