import discord 
import shared.config as config
import asyncio
import random
import re
from discord.ext import commands

num_diamantes_encontrados = 0 
multiplicador_base = 1.2
max_multiplicador = 5.30
valormultiplicardiamante = 0.2
valormultiplicarbomba = 0.2

bomb_buttons = [ ]
num_slots = 25
ganho_diamante = 0 

saldo = 100

emojis = {
    'bomba': '💣',
    'diamante': '💎',
    'oculto': 'ㅤ',
    'verde': discord.ButtonStyle.green,
    'vermelho': discord.ButtonStyle.red,
    'cinza': discord.ButtonStyle.gray
}


class Apostar(discord.ui.Modal):
    def __init__(self):
        super().__init__(title=f'Mines - Seu saldo: R$ {saldo}')

    valorinputaposta = discord.ui.TextInput(label='Valor', placeholder='Min: R$ 5 e Max: R$ 100', max_length=7, required=True)
    valorbomba = discord.ui.TextInput(label='Bombas', placeholder='Min: 2 e Max: 24', max_length=3, required=True)
    async def on_submit(self, interaction: discord.Interaction):
        global saldo

        valor_aposta_str = self.valorinputaposta.value
        valor_bombas_str = self.valorbomba.value
        padrao = re.compile(r'[^\w\s]')
        caracteres_especiais_aposta = padrao.findall(valor_aposta_str)
        caracteres_especiais_bombas = padrao.findall(valor_bombas_str)

        if caracteres_especiais_aposta and caracteres_especiais_bombas:
            await interaction.response.send_message('Por favor, insira apenas números não utilize caractres especiais.', ephemeral=True)
            return
        
        if not valor_aposta_str.isdigit():
            await interaction.response.send_message('Por favor, insira apenas números para o valor da aposta.', ephemeral=True)
            return
            
        if not valor_bombas_str.isdigit():
            await interaction.response.send_message('Por favor, insira apenas números para o valor das bombas.', ephemeral=True)
            return

        valor_aposta = int(valor_aposta_str) #float mudei para int
        valor_bombas = int(valor_bombas_str)

        if valor_aposta < 5 or valor_aposta > 100:
            await interaction.response.send_message('O minimo para apostar é R$ 5 reais e o máximo é R$ 100.', ephemeral=True)
            return
        
        if saldo < valor_aposta:
            await interaction.response.send_message('Você não tem saldo suficiente para fazer esta aposta.', ephemeral=True)
            return
        
        if valor_bombas < 2 or valor_bombas > 24:
            await interaction.response.send_message('O minimo de bombas é 2 e o máximo é 24.', ephemeral=True)
            return
            
        #saldo -= valor_aposta

        await interaction.response.send_message(f'Você depositou: R$ {valor_aposta} e escolheu {valor_bombas}x bombas.', ephemeral=True)


def calcular_multiplicador(quantidadeBombas):
    valor_diamante = valormultiplicardiamante * num_diamantes_encontrados
    multiplicador = multiplicador_base + (quantidadeBombas * valormultiplicarbomba)
    multiplicador_total = multiplicador + valor_diamante
    
    return min(multiplicador_total, max_multiplicador)
 

async def mine(interaction: discord.Interaction):
    global num_diamantes_encontrados, saldo

    guild = interaction.guild
    author = interaction.user
    author_name = interaction.user.name
    canal_nome = f'💣mines-{author_name}'
        
    
    existing_channels = [
        channel for channel in interaction.guild.channels if str(channel.name).startswith('💣mines-')
    ]

    if existing_channels:
        await interaction.response.send_message(f'{author.mention} você já tem um canal criado.', ephemeral=True)
        return
    
    modal = Apostar()

    await interaction.response.send_modal(modal)
    await modal.wait() 

    valor_aposta = modal.valorinputaposta.value
    valor_bombas = modal.valorbomba.value
    padrao = re.compile(r'[^\w\s]')
    caracteres_especiais_aposta = padrao.findall(valor_aposta)
    caracteres_especiais_bombas = padrao.findall(valor_bombas)
    
    if caracteres_especiais_aposta and caracteres_especiais_bombas:
        return
    
    if not valor_bombas.isdigit() and not valor_aposta.isdigit():
        return

    apostasNumero = int(valor_aposta)

    if apostasNumero < 5 or apostasNumero > 100:
        return
    
    if saldo < apostasNumero:
        return
    
    quantidadeBombas = int(valor_bombas)
    num_diamantes = num_slots - quantidadeBombas
    num_diamantes_encontrados = 0
    viewbutton = discord.ui.View()
    bomb_buttons.clear()

    if quantidadeBombas < 2 or quantidadeBombas > 24:
        return
    
    bomb_positions = random.sample(range(num_slots), quantidadeBombas)

    diamante_positions = [
        pos for pos in range(num_slots) if pos not in bomb_positions
    ] #PARA TESTE, APAGAR DEPOIS.
    
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        author: discord.PermissionOverwrite(read_messages=True, send_messages=False)
    }
    
    saldo -= apostasNumero

    print("Posição das Bombas:", bomb_positions)
    print("Posição dos Diamantes:", diamante_positions)

    for i in range(num_slots):
        if i in bomb_positions:
            bomb_buttons.append(i+1)

        button = discord.ui.Button(label=emojis['oculto'], style=emojis['cinza'], custom_id=f'ID >> Button_{i+1}')
        button.callback = lambda interact: respostabotao(interact, viewbutton, valor_aposta, valor_bombas, num_diamantes)
        viewbutton.add_item(button)

    viewbutton_desistir = discord.ui.View()
    button_desistir = discord.ui.Button(label='Desistir', style=discord.ButtonStyle.red, custom_id=f'ID >> Button_Desistir')
    viewbutton_desistir.add_item(button_desistir)

    #button_sacar.callback

    embed2 = discord.Embed(
        title='Campo Minado',
        color=discord.Color.red()
    )

    embed2.add_field(
        name='Clique nos botões cinzas para revelar o conteúdo!',
        value=f'ㅤ\n• 💎Diamantes total: {num_diamantes}\n• 💥Bombas: {valor_bombas}\n• ⛏Multiplicador 0x\nㅤ\n• 💰Apostou: R$ {int(valor_aposta)}\n• 💰Saldo: R$ {int(saldo)}\n• 💰Total ganho: R$ {ganho_diamante}',
        inline=True
    )


    global button_desistir_G, canal

    canal = await guild.create_text_channel(name=canal_nome, overwrites=overwrites)

    await canal.send(embed=embed2, view=viewbutton)

    button_desistir_G = await canal.send(view=viewbutton_desistir)
    

button_sacar_G = None
async def respostabotao(interact: discord.Interaction, viewbutton, valor_aposta, valor_bombas, num_diamantes):
    global num_diamantes_encontrados, saldo, ganho_diamante, button_sacar_G

    if interact.response.is_done():
        return
    
    custom_id = interact.data['custom_id']
    button_number = int(custom_id.split('_')[-1])
    button = viewbutton.children[button_number - 1]
    quantidadeBombas = int(valor_bombas)
    multiplicador = calcular_multiplicador(quantidadeBombas)
    valor_aposta_num = int(valor_aposta) #float mudei para int

    if button_number in bomb_buttons:

        button.label = emojis['bomba']
        button.style = emojis['vermelho']
        ganho_diamante = 0 

        #await button_sacar_G.delete()

        for i in range(num_slots):

            if i + 1 in bomb_buttons:
                
                viewbutton.children[i].label = emojis['bomba']
                viewbutton.children[i].style = emojis['vermelho']

            else:

                viewbutton.children[i].label = emojis['diamante']
                viewbutton.children[i].style = emojis['verde']
    
    
        for child in viewbutton.children:
            child.disabled = True


        embed3 = discord.Embed(
            title='Você perdeu o Campo Minado!',
            color=discord.Color.red()
        )

        embed3.add_field(
            name='Deseja jogar novamente?',
            value=f'ㅤ\n• 💰Saldo: R$ {saldo}\n• 💰Ganho: R$ 0,00',
            inline=True
        )
        viewrecomecar = discord.ui.View()
        button_recomecar = discord.ui.Button(label='SIM', style=discord.ButtonStyle.green, custom_id='ID >> Button_recomecar')
        button_sair = discord.ui.Button(label='NÃO.', style=discord.ButtonStyle.red, custom_id='ID >> Button_sair')
        viewrecomecar.add_item(button_recomecar)
        viewrecomecar.add_item(button_sair)
        
        await interact.channel.send(embed=embed3, view=viewrecomecar)

    else:


        button.style = emojis['verde']
        button.label = emojis['diamante']
        num_diamantes_encontrados += 1 
        ganho_diamante = valor_aposta_num * multiplicador  # Calcula o ganho com o diamante
    
        viewbutton_sacar = discord.ui.View()
        if button_sacar_G is None:
            button_sacar = discord.ui.Button(label='Sacar', style=discord.ButtonStyle.green, custom_id=f'ID >> Button_Sacar')
            viewbutton_sacar.add_item(button_sacar)
            button_sacar_G = await canal.send(view=viewbutton_sacar)


        if button_desistir_G:
            try:
                await button_desistir_G.delete()
            except discord.NotFound:
                print('button_desistir_G já foi deletado.')


    diamantes_restantes = num_diamantes - num_diamantes_encontrados

    if diamantes_restantes == 0:

        for i in range(num_slots):

            if i + 1 in bomb_buttons:

                viewbutton.children[i].label = emojis['bomba']
                viewbutton.children[i].style = emojis['vermelho']

            else:

                viewbutton.children[i].label = emojis['diamante']
                viewbutton.children[i].style = emojis['verde']
        print('Encontrado todos')
        for child in viewbutton.children:
            child.disabled = True

    embed2 = discord.Embed(
        title='Campo Minado',
        color=discord.Color.red()
    )
    
    embed2.add_field(
        name='Clique nos botões cinzas para revelar o conteúdo!',
        value=f'ㅤ\n• 💎Diamantes Total: {diamantes_restantes}\n• 💥Bombas: {quantidadeBombas}\n• ⛏Multiplicador {multiplicador}\nㅤ\n• 💰Apostou: R$ {int(valor_aposta)}\n• 💰Saldo: R$ {saldo}\n• 💰Ganho: R$ {int(ganho_diamante)}',
        inline=True
    )

    button.disabled = True
    viewbutton.children[button_number - 1] = button

    try:
        await interact.response.edit_message(view=viewbutton, embed=embed2)

    except discord.errors.NotFound:

        pass 