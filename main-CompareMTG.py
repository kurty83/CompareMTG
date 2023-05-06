import discord
import requests,sys,getopt
from bs4 import BeautifulSoup
import json
from urllib.request import urlopen



async def send_message(message, user_message, is_private):
    try:
        await message.author.send(message) if is_private else await message.channel.send(message)
    except Exception as Myexception:
        print(Myexception)

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

async def search_magicCorp(searchString, message):
    #on remplace les " " par des + pour une meileure efficacité de la recherche
    #newsearchString = searchString.replace (" ", "+")
    #newsearchString = newsearchString.replace ("\"", "")
    URL = "https://boutique.magiccorporation.com/magic.php?text=" + searchString + "&submit=Ok"
    print(f"{URL}")
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")
    resultshref = soup.find('p', attrs={'class' :"titre"})
    resultsprice = soup.find('span', attrs={'class' :"prix"})
    if (resultshref and resultsprice):    
        await message.channel.send("MagicCorp : " + resultsprice.text + " =======> https://boutique.magiccorporation.com/" + resultshref.a['href'] )

async def search_Philibert(searchString, message):
    #on remplace les " " par des + pour une meileure efficacité de la recherche
    #newsearchString = searchString.replace (" ", "+")
    #newsearchString = newsearchString.replace ("\"", "")
    URL = "https://www.philibertnet.com/fr/recherche?search_query=" + searchString + "&submit_search="
    page = requests.get(URL)
    print(f"{URL}")
    soup = BeautifulSoup(page.content, "html.parser")
    resultshref = soup.find('p', attrs={'class' :"s_title_block"})
    resultsprice = soup.find('span', attrs={'class' :"price"})
    if (resultshref and resultsprice):
        await message.channel.send("Philibert : " + resultsprice.text + " =======> " + resultshref.a['href'])

async def search_play_in(searchString, message):
    #on remplace les " " par des + pour une meileure efficacité de la recherche
    #newsearchString = searchString.replace (" ", "+")
    #on remplace les " " au début et à la fin de la commande reçue par l'utilisateur
    #newsearchString = newsearchString.replace ("\"", "")
    #crafting de l'url
    URL =  "https://www.play-in.com/recherche/result.php?s=" + searchString
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")
    ### on recupere le PRIX
    # 1er cas si la recherche trouve 1 seul produit
    resultsprice = soup.find('div', attrs={'class' :"price"})
    if not resultsprice:
        #2e cas si la recherche trouve plusieurs produits
        resultsprice = soup.find('div', attrs={'class' :"price_product simple_price_product"})

    ### on recupere le LIEN produit avec soup
    resultshref = soup.find('div', attrs={'class' :"container_img_product"})
    if not resultshref:
        #lien recupéré sur la base canonical dans 1 cas
        resultshref = soup.find('link', attrs={'rel' : "canonical"})
        #on craft le message envoyé au channel
        messageToSend = "PlayIn : " + resultsprice.text + " =======> " + resultshref['href']
        print(f"{messageToSend}")
    else:
        #lien recupéré en soup pour le 2e cas, craft du message envoyé au channel
        messageToSend = "PlayIn : " + resultsprice.text + " =======> https://www.play-in.com" + resultshref.a['href']
    print(f"{resultshref}")
    ### SI PRIX ET LIEN OK , on envoi le message dans le channel
    if (resultshref != "" and resultsprice != ""):
        await message.channel.send(messageToSend)

async def search_parkage(searchString, message):
    #on remplace les " " par des + pour une meileure efficacité de la recherche
    #newsearchString = searchString.replace (" ", "+")
    #on remplace les " " au début et à la fin de la commande reçue par l'utilisateur
    #newsearchString = newsearchString.replace ("\"", "")
    #crafting de l'url
    URL = "https://search.luciole.tech/api/search?text="+ searchString + "&namespace=fr&_ref=2"
    #début du parsing json
    response = urlopen(URL)
    data_json = json.loads(response.read())
    #on lit la valeur price du premier élément
    price = data_json['list'][0]['price_discount']
    #on cast la valeur en string au lieu d'int
    price = str(price)
    #on recupere l'id du produit pour construire l'url du produit
    id = data_json['list'][0]['id']
    resultshref = "0" + str(id) + "-" + data_json['list'][0]['taxonomy_value_permalink'][2]['permalink'] + "/"
    ### SI PRIX ET LIEN OK , on envoi le message dans le channel 
    if (resultshref and price):
        await message.channel.send("Parkage : " + price + "€ =======> https://www.parkage.com/" + resultshref)  
    
@client.event
async def on_ready():
    print(f'{client.user} is online !')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    username = str(message.author)
    user_message = str(message.content)
    channel = str(message.channel)

    print(f"{username} a dit : '{user_message}' ({channel})")

    searchString = user_message.split(" ", 1)
    newSearchString = searchString[1].replace (" ", "+")
    newSearchString = newSearchString.replace ("\"", "")
    #si l'utilisateur tape une commande commencant par !prix alors on execute nos recherches en mode asynchrone
    if message.content.startswith("!prix"):
        await search_Philibert(newSearchString, message)
        await search_magicCorp(newSearchString, message)
        await search_play_in(newSearchString, message)
        await search_parkage(newSearchString, message)

    if user_message[0] == '?':
        user_message = user_message[1:]
        await send_message(message, user_message, is_private=True)
    #else:
    #    await send_message(message, user_message, is_private=False)

client.run("write your own discord token key")



