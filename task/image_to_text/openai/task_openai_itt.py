import base64
from pathlib import Path

from task._utils.constants import API_KEY, DIAL_CHAT_COMPLETIONS_ENDPOINT
from task._utils.model_client import DialModelClient
from task._models.role import Role
from task.image_to_text.openai.message import ContentedMessage, TxtContent, ImgContent, ImgUrl


def start() -> None:
    project_root = Path(__file__).parent.parent.parent.parent
    image_path = project_root / "dialx-banner.png"

    with open(image_path, "rb") as image_file:
        image_bytes = image_file.read()
    base64_image = base64.b64encode(image_bytes).decode('utf-8')

    client = DialModelClient(
        DIAL_CHAT_COMPLETIONS_ENDPOINT,
        deployment_name='gpt-4o',
        api_key=API_KEY,
    )

    data_url = f'data:image/png;base64,{base64_image}'
    msg_base64 = ContentedMessage(
        role=Role.USER,
        content=[
            TxtContent('What do you see in this picture?'),
            ImgContent(ImgUrl(url=data_url)),
        ],
    )
    print('--- Base64 image analysis ---')
    response_base64 = client.get_completion(messages=[msg_base64])
    print('Response:', response_base64.content)

    image_url = 'https://i.ytimg.com/vi/uMTo-ge8AHQ/maxresdefault.jpg'
    msg_url = ContentedMessage(
        role=Role.USER,
        content=[
            TxtContent('What do you see in this picture?'),
            ImgContent(ImgUrl(url=image_url)),
        ],
    )
    print('--- URL image analysis ---')
    response_url = client.get_completion(messages=[msg_url])
    print('Response:', response_url.content)


if __name__ == '__main__':
    start()