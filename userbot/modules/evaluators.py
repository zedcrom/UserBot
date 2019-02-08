import asyncio
import subprocess

from telethon import events

from userbot import *
from userbot import bot
from userbot import SUBPROCESS_ANIM

@bot.on(events.NewMessage(outgoing=True, pattern="^.eval"))
@bot.on(events.MessageEdited(outgoing=True, pattern="^.eval"))
async def evaluate(e):
    if not e.text[0].isalpha() and e.text[0] not in ("/", "#", "@", "!"):
        if e.is_channel and not e.is_group:
            await e.edit("`Eval isn't permitted on channels`")
            return
        evaluation = eval(e.text[6:])
        if evaluation:
            if isinstance(evaluation) == "str":
                if len(evaluation) > 4096:
                    f = open("output.txt", "w+")
                    f.write(evaluation)
                    f.close()
                await bot.send_file(
                    e.chat_id,
                    "output.txt",
                    reply_to=e.id,
                    caption="`Output too large, sending as file`",
                )
                subprocess.run(["rm", "sender.txt"], stdout=subprocess.PIPE)
        await e.edit(
            "**Query: **\n`"
            + e.text[6:]
            + "`\n**Result: **\n`"
            + str(evaluation)
            + "`"
        )
    else:
        await e.edit(
            "**Query: **\n`"
            + e.text[6:]
            + "`\n**Result: **\n`No Result Returned/False`"
        )
    if LOGGER:
        await bot.send_message(
            LOGGER_GROUP, "Eval query " + e.text[6:] + " was executed successfully"
        )


@bot.on(events.NewMessage(outgoing=True, pattern=r"^.exec (.*)"))
@bot.on(events.MessageEdited(outgoing=True, pattern=r"^.exec (.*)"))
async def run(e):
    if not e.text[0].isalpha() and e.text[0] not in ("/", "#", "@", "!"):
        if e.is_channel and not e.is_group:
            await e.edit("`Exec isn't permitted on channels`")
            return
        code = e.raw_text[5:]
        exec(f"async def __ex(e): " + ""
             .join(f"\n {l}" for l in code.split("\n")))
        result = await locals()["__ex"](e)
        if result:
            if len(result) > 4096:
                f = open("output.txt", "w+")
                f.write(result)
                f.close()
                await bot.send_file(
                    e.chat_id,
                    "output.txt",
                    reply_to=e.id,
                    caption="`Output too large, sending as file`",
                )
                subprocess.run(["rm", "output.txt"], stdout=subprocess.PIPE)

            await e.edit(
                "**Query: **\n`"
                + e.text[5:]
                + "`\n**Result: **\n`"
                + str(result) + "`"
            )
        else:
            await e.edit(
                "**Query: **\n`"
                + e.text[5:]
                + "`\n**Result: **\n`"
                + "No Result Returned/False"
                + "`"
            )

        if LOGGER:
            await bot.send_message(
                LOGGER_GROUP,
                "Exec query " + e.text[5:] + " was executed successfully"
            )



@bot.on(events.NewMessage(outgoing=True, pattern=r"^\.term (.+)"))
@bot.on(events.MessageEdited(outgoing=True, pattern=r"^\.term (.+)"))
async def terminal(e):
    if not e.text[0].isalpha() and e.text[0] not in ("/", "#", "@", "!"):
        if e.is_channel and not e.is_group:
            await e.edit("`Term Commands aren't permitted on channels`")
            return
    cmd = e.pattern_match.group(1)

    await e.edit("`Connecting..`")

    start_time = time.time() + 10
    process = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )

    OUTPUT = f"**QUERY:**\n__Command:__\n`{cmd}` \n__PID:__\n`{process.pid}`\n\n**Output:**\n"

    if not SUBPROCESS_ANIM:
        stdout, stderr = await process.communicate()

        if len(stdout) > 4096:
            await e.reply(f"{OUTPUT}\n__Process killed:__ `Messasge too long`")
            return

        await e.edit(f"{OUTPUT}`{stdout.decode()}`")
        return


    while process:
        if time.time() > start_time:
            await e.edit(f"{OUTPUT}\n__Process killed__: `Time limit reached`")
            break

        stdout = await process.stdout.readline()

        if not stdout:
            _, stderr = await process.communicate()
            if stderr.decode():
                OUTPUT += f"`{stderr.decode()}`"
                await e.edit(OUTPUT)
                break

        if stdout:
            OUTPUT += f"`{stdout.decode()}`"

        if len(OUTPUT) > 4096:
            await e.reply(f"{OUTPUT}\n__Process killed:__ `Messasge too long`")
            break
        try:
            await e.edit(OUTPUT)
        except Exception:
            break
