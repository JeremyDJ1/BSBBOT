import discord
from discord.ext import commands


class Respond_Button(discord.ui.View, commands.Cog):

  def __init__(self, Respondent_Member_Object, Recipient_Member_Obejct,
               Payment_Request_Title, bot):
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
