"""
Python Wechaty - https://github.com/wechaty/python-wechaty

Authors:    Jingjing WU (吴京京) <https://github.com/wj-Mcat>

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
import os
import math
from typing import AsyncIterable, List, Optional
import tempfile
from uuid import uuid4
from wechaty_grpc.wechaty.puppet import MessageSendFileStreamRequest
from wechaty_puppet import FileBox
from wechaty_grpc.wechaty.puppet import FileBoxChunk

from wechaty_puppet_service.config import CHUNK_SIZE


async def pack_file_box_to_chunk(file_box: FileBox) -> AsyncIterable[FileBoxChunk]:
    """pack file-box instance to async iterator chunks

    Args:
        file_box (FileBox): the source file-box instance

    Returns:
        AsyncIterator[FileBoxChunk]: Async Iterator FileBox Chunk
    """
    # 1. save file-box as temp file, so that we can read stream from it.
    temp_dir = tempfile.TemporaryDirectory()
    file_name = "%s-%s" % (str(uuid4()), file_box.name)
    file_path = os.path.join(temp_dir.name, file_name)
    await file_box.to_file(file_path, overwrite=True)
    
    # 2. read stream from the temp file
    streams: bytes = bytes()
    with open(file_path, 'rb') as f:
        for line in f:
            streams += line
    
    # 3. split it to chunks
    size = len(streams)
    
    for i in range(math.ceil(size / CHUNK_SIZE)):
        stream = streams[i * CHUNK_SIZE: (i + 1) * CHUNK_SIZE]
        yield FileBoxChunk(
            data=stream,
            name=file_box.name
        )


async def gen_file_stream_request(
        conversation_id: str, file_box: FileBox) -> AsyncIterable[MessageSendFileStreamRequest]:
    chunks = pack_file_box_to_chunk(file_box)
    async for chunk in chunks:
        request = MessageSendFileStreamRequest(
            conversation_id=conversation_id,
            file_box_chunk=chunk
        )
        yield request


async def unpack_file_box_chunk(file_box_chunks: List[FileBoxChunk]) -> FileBox:
    """unpack async iterator filebox chunks to file-box instance

    Args:
        file_box_chunks (AsyncIterator[FileBox]):

    Returns:
        FileBox: [description]
    """
    # 1. merge chunks
    buffers: bytes = bytes()
    name: Optional[str] = None
    for chunk in file_box_chunks:
        buffers += chunk.data
        name = chunk.name

    # 2. gen file-box
    file_box: FileBox = FileBox.from_buffer(buffers, name)
    return file_box
