import discord
from discord.ext import commands

bot = commands.Bot(intents=discord.Intents.all(), command_prefix="/")

USERS_DICT = {}


class Account:

  def __init__(self, User_ID, User_Name, BSB, Account_Number, Account_Name):
    self.User_ID = User_ID
    self.User_Name = User_Name
    self.BSB = BSB
    self.Account_Number = Account_Number
    self.Account_Name = Account_Name

  def Fetch_Embed_Info(self, Member_Object):
    embed = discord.Embed(
      title=Member_Object.name,
      description=str(Member_Object.name + "#" + Member_Object.discriminator),
      color=Member_Object.accent_color,
    )
    embed.set_thumbnail(url=Member_Object.avatar)
    embed.add_field(name="BSB", value=self.BSB, inline=True)
    embed.add_field(name="Account Number",
                    value=self.Account_Number,
                    inline=True)
    embed.add_field(name="Account Name", value=self.Account_Name, inline=True)
    return embed

  def Fetch_Embed_Pay_Request(self, Member_Object, input, Payers):
    Title = input[0]
    Price = input[1]
    Divisor = len(input) - 2
    Description = "Price Per Person : ${0}".format(
      str(round(float(Price) / int(Divisor), 2)))

    embed = discord.Embed(
      title=Title,
      description=Description,
      color=Member_Object.accent_color,
    )
    embed.set_author(name=Member_Object.name +
                     " Has Opened a New Payment Request!",
                     icon_url=Member_Object.avatar)
    embed.add_field(name="BSB", value=self.BSB, inline=True)
    embed.add_field(name="Account Number",
                    value=self.Account_Number,
                    inline=True)
    embed.add_field(name="Account Name", value=self.Account_Name, inline=True)

    recipients = ""
    for x in Payers:
      recipients += x.name + ", "
    recipients = recipients[:-2]
    embed.add_field(name="Recipient's", value=recipients)
    return embed

  def To_CSV(self):
    return "{0},{1},{2},{3},{4}".format(str(self.User_ID), self.User_Name,
                                        self.BSB, self.Account_Number,
                                        self.Account_Name)


class Payment_Request:

  def __init__():
    pass


class Respond_Button(discord.ui.View):

  def __init__(self, Respondent_Member_Object, Recipient_Member_Obejct,
               Payment_Request_Title):
    super().__init__()
    self.Respondent_Member_Object = Respondent_Member_Object
    self.Recipient_Member_Obejct = Recipient_Member_Obejct
    self.Payment_Request_Title = Payment_Request_Title

  @discord.ui.button(label="I Have Paid!", style=discord.ButtonStyle.primary)
  async def button_callback(
    self,
    interaction,
    button,
  ):
    embed = discord.Embed(title="{0}#{1} has paid for {2}".format(
      self.Recipient_Member_Obejct.name,
      self.Recipient_Member_Obejct.discriminator, self.Payment_Request_Title))

    await self.Respondent_Member_Object.send(embed=embed)
    button.disabled = True
    button.label = "Thank you! {0}#{1} has been informed.".format(
      self.Respondent_Member_Object.name,
      self.Respondent_Member_Object.discriminator,
    )
    await interaction.response.edit_message(view=self)


@bot.event
async def on_ready():
  Read()


def Read():
  file = open("data.txt", "r")
  for i in file.readlines():
    if i.strip():
      split = i.rstrip('\n').split(',')
      temp = Account(split[0], split[1], split[2], split[3], split[4])
      USERS_DICT[split[0]] = temp
  file.close()


def Store():
  file = open("data.txt", "w")
  for Account in USERS_DICT:
    obj = USERS_DICT[Account]
    file.write(obj.To_CSV())
    file.write('\n')
  file.close()


def Clean_Tag(str):
  return str.replace("@", "").replace("<", "").replace(">", "")


@bot.command()
async def register(ctx, *input):
  if len(input) != 3 or not input:
    embed = discord.Embed(title="Hmm....Something is Missing",
                          description='''
      Please use the format '/register BSB ACC_NUMBER ACC_NAME' with each 
      element seperated by spaces.
      ''')
    await ctx.channel.send(embed=embed)
    return

  BSB, ACC, NAME = input[0], input[1], input[2]

  #validation for user already in database
  if str(ctx.author.id) in USERS_DICT:
    embed = discord.Embed(title="User Already Registered!")
    await ctx.channel.send(embed=embed)
    return

  else:

    temp = Account(str(ctx.author.id), str(ctx.author.name), BSB, ACC, NAME)
    USERS_DICT[str(ctx.author.id)] = temp

    embed = discord.Embed(title="User Registered!")
    await ctx.channel.send(embed=embed)
    Store()


@bot.command()
async def info(ctx, name=None):
  if not name:
    embed = discord.Embed(title="Hmm....Something is Missing",
                          description='''
      Please use the format '/info "@username".
      ''')
    await ctx.channel.send(embed=embed)
    return

  temp = USERS_DICT[Clean_Tag(name)]
  if temp:
    temp_member_object = await bot.fetch_user(temp.User_ID)
    embed = temp.Fetch_Embed_Info(temp_member_object)
    await ctx.channel.send(embed=embed)
    return
  else:
    embed = discord.Embed(
      title="User Could Not Be Found!",
      description="To register use the '/register' command")
    await ctx.channel.send(embed=embed)


@bot.command()
async def remove(ctx):
  if str(ctx.author.id) in USERS_DICT:
    USERS_DICT.pop(str(ctx.author.id))
    embed = discord.Embed(title="User {0} Deleted!".format(ctx.author.name), )
    await ctx.channel.send(embed=embed)
    print(USERS_DICT)
    Store()
  else:
    embed = discord.Embed(
      title="User Could Not Be Found!",
      description="To register use the '/register' command")
    await ctx.channel.send(embed=embed)
    return


@bot.command()
async def payme(ctx, *input):
  ##ERROR VALIDATION##
  if len(input) < 3:
    embed = discord.Embed(title="Hmm....Something is Missing",
                          description='''
      Make sure the payment request has the correct arguments and at least one recipient.
      ''')
    await ctx.channel.send(embed=embed)
    return
  ##ERROR VALIDATION##
  if isinstance(input[1], float):
    embed = discord.Embed(title="Hmm....Something is Missing",
                          description='''
      Please make sure that the price is a valid number.
      ''')
    await ctx.channel.send(embed=embed)
    return
  ##ERROR VALIDATION##
  if not str(ctx.author.id) in USERS_DICT:
    embed = discord.Embed(
      title="User Could Not Be Found!",
      description="To register use the '/register' command")
    await ctx.channel.send(embed=embed)
    return

  Payers = []
  for x in range(2, len(input)):
    Payers.append(await bot.fetch_user((Clean_Tag(input[x]))))

  Author_Account = USERS_DICT[str(ctx.author.id)]
  Author_Member_Object = await bot.fetch_user(Author_Account.User_ID)
  embed = Author_Account.Fetch_Embed_Pay_Request(Author_Member_Object, input,
                                                 Payers)
  await ctx.channel.send(embed=embed)

  for x in Payers:
    await x.send(
      "Hey!, just letting you know that you have been mentioned in a new PayMe request.",
      embed=embed)
    await x.send(view=Respond_Button(Author_Member_Object, x, input[0]))
  return


bot.run(
  'MTA1OTAxNTcxMTE5Mzg0NTc3MQ.GCnLAi.zX84vazatek27kBFVGil7iylPTgOt92ZG08Smg')
