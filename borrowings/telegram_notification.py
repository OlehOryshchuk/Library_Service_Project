import urllib.parse
import httpx


async def send_telegram_notification(bot_token: str, chat_id: str, text: str):
    """
    Send notification on telegram chat_id using bot_token
    """
    async with httpx.AsyncClient() as client:
        try:
            # URL encode the text parameter
            # because could be symbols that are not supported
            encoded_text = urllib.parse.quote(text, safe='')

            # make asynchronous https request
            response = await client.get(
                f"https://api.telegram.org/bot{bot_token}/"
                f"sendMessage?chat_id={chat_id}&text={encoded_text}"
            )
            return response.json()

        except httpx.HTTPError as e:
            print(
                f"Error handling Borrowing creation"
                f" telegram notification: {e}"
            )
            return None
