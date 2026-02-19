import asyncio
from io import BytesIO
from pathlib import Path

from task._models.custom_content import Attachment, CustomContent
from task._utils.constants import API_KEY, DIAL_CHAT_COMPLETIONS_ENDPOINT, DIAL_URL
from task._utils.bucket_client import DialBucketClient
from task._utils.model_client import DialModelClient
from task._models.message import Message
from task._models.role import Role

async def _put_image() -> Attachment:
    file_name = 'dialx-banner.png'
    image_path = Path(__file__).parent.parent.parent / file_name
    mime_type_png = 'image/png'

    async with DialBucketClient(API_KEY, DIAL_URL) as client:
        with open(image_path, 'rb') as f:
            content = BytesIO(f.read())
        result = await client.put_file(name=file_name, mime_type=mime_type_png, content=content)

    file_path = result.get('path') or result.get('url') or result.get('file_path')
    if file_path and file_path.startswith('http'):
        for prefix in (f'{DIAL_URL}/v1/', 'https://', 'http://'):
            if '/v1/' in file_path:
                file_path = file_path.split('/v1/', 1)[-1]
                break
    if not file_path:
        file_path = f"files/appdata/{file_name}"

    return Attachment(title=file_name, url=file_path, type=mime_type_png)


def start() -> None:
    client = DialModelClient(
        DIAL_CHAT_COMPLETIONS_ENDPOINT,
        deployment_name='gpt-4o',
        api_key=API_KEY,
    )
    attachment = asyncio.run(_put_image())
    print('Attachment:', attachment)

    message = Message(
        role=Role.USER,
        content='What do you see on this picture?',
        custom_content=CustomContent(attachments=[attachment]),
    )
    response = client.get_completion(messages=[message])
    print('Response:', response.content)


if __name__ == '__main__':
    start()
