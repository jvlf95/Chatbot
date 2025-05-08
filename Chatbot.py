import discord
from discord.ext import commands
import requests
import json
import os

# Intents -> permissões que o discord precisa para funcionar, e estou guardando as permissões dentro da variável intents
intents = discord.Intents.all()
# a variável bot representa o meu Bot e todas as suas propriedades
bot = commands.Bot(".", intents=intents)
# Qual modelo de IA estamos utilizando do OLLama
MODEL_NAME = "mistral"
# URL de acesso pode ser alterada caso queira mudar onde está a IA
URL_IA = "http://localhost:11434/api/chat"

def perguntar_ollama(pergunta):
    url = URL_IA
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "user", "content": pergunta}
        ],
        "stream": True,
    }

    resposta = ""
    with requests.post(url, json=payload, stream=True) as response:
        for linha in response.iter_lines():
            if linha:
                dados = json.loads(linha.decode("utf-8"))
                resposta += dados.get("message", {}).get("content", "")

    return resposta.strip()

#Por conta do limite de caracteres do Discord pode ser necessário dividir em partes
def dividir_em_partes(texto, limite=2000):
    return [texto[i:i+limite] for i in range(0, len(texto), limite)]


# evento disparado quando o bot liga
@bot.event
# async -> uma função assícrona que será executada várias vezes, que se conecta com a API
async def on_ready():
    print("Bot funcionando")


@bot.event
# msg --> objeto que representa a mensagem enviada
async def on_message(msg:discord.Message):
    # evita que o evento se repita quando vê a mensagem do próprio bot
    if msg.author.bot:
        return

    #Se a mesagem começar com esse comando vai ser direcionada a IA
    if msg.content.startswith('!pergunta'):
        pergunta = msg.content[len('!pergunta '):].strip()
        
        await msg.channel.send("Pensando...")
        resposta = perguntar_ollama(pergunta)
        partes = dividir_em_partes(resposta)
        for parte in partes:
            await msg.channel.send(parte)

@bot.event
# membro --> objeto que representa um novo membro
async def on_member_join(membro:discord.Member):
    canal = bot.get_channel(1360053873146069086)
    await canal.send(f"{membro.mention} entrou no servidor")

@bot.event
async def on_reaction_add(reacao:discord.Reaction, membro:discord.Member):
    await reacao.message.reply(f"O membro {membro.name} reagiu a mensagem com {reacao.emoji}")

@bot.command()
# a função ola() é executada assim que o usuário digita .ola no chat do discord
# ctx --> objeto que representa o contexto
# reply --> operação/ função para responder o usuário, responder direatamente a mensagem enviada pelo usuário
async def ola(ctx:commands.Context):
    # essa variável irá guardar o valor referetne ao nome do usuário que executar o comando .ola para se comunicar com o bot
    # ctx.author.nome --> o objeto ctx pega o nome do usuário
    nome = ctx.author.name
    await ctx.reply(f"Olá {nome}!")
    await ctx.send("Em que posso te ajudar?")

# @bot.command()
# # comando que faz o bot pegar o texto do usuário e copiar e colar
# async def falar(ctx:commands.Context,num1,num2):
#     num1_int = int(num1)
#     num2_int = int(num2)
#     await ctx.reply(f"A soma entre {num1_int} e {num2_int} é igual a {num1_int+num2_int}")


bot.run("")