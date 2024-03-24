import discord
import shared.config as config
import random
from discord.ext import commands
from games.mines import mine

intents = discord.Intents.default()
intents.message_content = True
intents.members = True 


bot = commands.Bot(command_prefix=config.prefix, intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} online ✔')


@bot.command()
async def createaposta(ctx):
    print(mine)
    embed = discord.Embed(
        title=config.Table_Geral['Variaveis']['Bot_Name'],
        color=discord.Color.red()
    )

    for v in config.Table_Geral['Menssagens']['msg']:
        embed.add_field(
            name=v['Commands'],
            value=v['Desc'],
            inline=True
        )

    embed.set_image(url='https://cdn.discordapp.com/attachments/1216538872314466304/1216548061128687646/SWQ.png?ex=6600c9ac&is=65ee54ac&hm=6f21d23245159a5f58adbd381413da1260f66349af346d78d22354f2deba7825&')
    view = discord.ui.View()
    button_01 = discord.ui.Button(label='Mines', style=discord.ButtonStyle.red, custom_id='ID >> Button_01')
    button_01.callback = Functionsgames
    button_02 = discord.ui.Button(label='Bicho', style=discord.ButtonStyle.red, custom_id='ID >> Button_02')
    button_02.callback = Functionsgames2
    button_03 = discord.ui.Button(label='Crash', style=discord.ButtonStyle.red, custom_id='ID >> Button_03')
    button_03.callback = Functionsgames3
    view.add_item(button_01)
    view.add_item(button_02)
    view.add_item(button_03)

    await ctx.send(embed=embed, view=view)

async def Functionsgames(interaction: discord.Interaction):
    await mine(interaction)

bot.run(config.Table_Geral['Variaveis']['TOKEN'])