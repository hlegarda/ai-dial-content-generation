import asyncio
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

from task._models.custom_content import Attachment
from task._utils.constants import API_KEY, DIAL_CHAT_COMPLETIONS_ENDPOINT, DIAL_URL
from task._utils.bucket_client import DialBucketClient
from task._utils.model_client import DialModelClient
from task._models.message import Message
from task._models.role import Role

class Size:
    square: str = '1024x1024'
    height_rectangle: str = '1024x1792'
    width_rectangle: str = '1792x1024'


class Style:
    natural: str = "natural"
    vivid: str = "vivid"


class Quality:
    standard: str = "standard"
    hd: str = "hd"

def _attachment_url_to_path(url: str) -> str:
    """Normalize attachment URL to path for get_file (GET /v1/{path})."""
    if not url:
        return url
    if url.startswith('http'):
        if '/v1/' in url:
            return url.split('/v1/', 1)[-1]
        parsed = urlparse(url)
        return (parsed.path or '').lstrip('/')
    return url


async def _save_images(attachments: list[Attachment]) -> None:
    if not attachments:
        return
    project_root = Path(__file__).parent.parent.parent
    async with DialBucketClient(API_KEY, DIAL_URL) as client:
        for i, attachment in enumerate(attachments):
            if not attachment.url:
                continue
            path = _attachment_url_to_path(attachment.url)
            data = await client.get_file(path)
            base = attachment.title or 'generated'
            if not base.endswith(('.png', '.jpg', '.jpeg', '.webp')):
                base = f'{base}.png'
            stem = Path(base).stem
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'{stem}_{timestamp}_{i}.png'
            out_path = project_root / filename
            out_path.write_bytes(data)
            print(f'Saved: {out_path}')


IMAGE_DEPLOYMENT = 'dall-e-3'


def start() -> None:
    client = DialModelClient(
        DIAL_CHAT_COMPLETIONS_ENDPOINT,
        deployment_name=IMAGE_DEPLOYMENT,
        api_key=API_KEY,
    )
    use_image_options = 'dall-e' in IMAGE_DEPLOYMENT.lower() or 'image' in IMAGE_DEPLOYMENT.lower()
    custom_fields = (
        {'size': Size.square, 'quality': Quality.hd, 'style': Style.natural}
        if use_image_options
        else None
    )
    response = client.get_completion(
        messages=[Message(role=Role.USER, content='Jim Raynor being happy with his family after the war.')],
        custom_fields=custom_fields,
    )
    attachments = []
    if response.custom_content and response.custom_content.attachments:
        attachments = response.custom_content.attachments
    if attachments:
        asyncio.run(_save_images(attachments))

if __name__ == '__main__':
    start()
