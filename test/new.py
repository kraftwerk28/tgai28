import os
import sys
import logging as log
from dotenv import load_dotenv

from tgai28.core import *
from tgai28.core.utils import *

load_dotenv()

log.basicConfig(
    format='[%(asctime)s] %(message)s',
    datefmt='%d.%m.%Y %H:%M:%S',
    level=log.INFO
)

API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
SESSION_PATH = os.path.abspath('./sessions/tgai28')

app = TgAI(SESSION_PATH, API_ID, API_HASH)


@app.on_command('help', arglist=['object', 'sample'], direction=MsgDir.OUT)
async def help(ctx: TgAIContext):
    print(ctx.state)
    await ctx.msg.reply(
        'Help: {}, {}'.format(
            ctx.named_args['object'],
            ctx.named_args['sample'],
        )
    )


@app.on_command('tagall', direction=MsgDir.OUT)
async def tagall(ctx: TgAIContext):
    users = await ctx.client.get_participants(ctx.msg.chat_id)
    if len(users) > 50:
        return
    mentions = [utils.mention(u) for u in users if not u.bot and not u.is_self]
    if mentions:
        sent = await ctx.msg.respond(' '.join(mentions))
        ctx.state.autorm[ctx.msg.id] = (sent.chat_id, sent.id)


@app.on_delete()
async def on_delete(ctx: TgAIContext):
    autorm = ctx.state.autorm
    stickerids = [i for i in ctx.event.deleted_ids if i in autorm]
    for _id in stickerids:
        chat_id, msg_id = autorm[_id]
        try:
            await ctx.client.delete_messages(chat_id, msg_id)
        except:
            pass
        del autorm[_id]


if __name__ == '__main__':
    app.start()