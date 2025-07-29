from python_simplex_bot.types import BaseContext, BaseHandler

def text_handler(handler: BaseHandler):
    async def wrapper(message: str, context: BaseContext):
        return await handler(message, context)
    return wrapper