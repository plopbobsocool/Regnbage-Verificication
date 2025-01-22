import discord
from discord.ext import commands
from discord import app_commands
from keep_alive import keep_alive  # Import keep_alive function

# Replace these variables with your bot's information and your server settings
TOKEN = 'MTMzMTQwMTMzNzIyOTAxNzE3OQ.GyYnNp.pJgojKmwHH42sqPhtUXkNXMznbUS1YN0WAesWI'  # Replace with your bot token
GUILD_ID = 1330642510351171616  # Replace with your guild/server ID
REGNBAGE_ROLE_ID = 1299054694697533483  # Replace with the role ID for "Regnbage"
REGISTRATION_CHANNEL_ID = 1331565396980924477  # Replace with the ID of the registration channel
REGISTERED_PLAYERS_CHANNEL_ID = 1331565541097476106  # Replace with the ID of the channel for registered players

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Dictionary to store user Steam ID registrations
user_steam_ids = {}

@bot.event
async def on_ready():
    print(f'Bot connected as {bot.user}')
    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} command(s).')
    except Exception as e:
        print(f'Error syncing commands: {e}')

@bot.event
async def on_member_join(member):
    guild = member.guild
    channel = guild.get_channel(REGISTRATION_CHANNEL_ID)
    if channel:
        await channel.send(
            f"Welcome to Regnbage, {member.mention}! To play, you must register your Steam ID.\n"
            "Please use the command: `/register <Steam 64>` in the server."
        )

@bot.tree.command(name="register")
@app_commands.describe(steam_id="Your Steam 64 ID")
async def register_command(interaction: discord.Interaction, steam_id: str):
    guild = interaction.guild
    member = interaction.user

    # Check if the user has already registered a Steam ID
    if member.id in user_steam_ids:
        await interaction.response.send_message(
            f"You have already registered with Steam ID `{user_steam_ids[member.id]}`.", ephemeral=True
        )
        return

    # Assign the "Regnbage" role
    regnbage_role = guild.get_role(REGNBAGE_ROLE_ID)
    if regnbage_role:
        await member.add_roles(regnbage_role)
    else:
        await interaction.response.send_message(
            "The 'Regnbage' role is not configured correctly.", ephemeral=True
        )
        return

    # Check if a role with the Steam ID already exists
    existing_role = discord.utils.get(guild.roles, name=steam_id)
    if existing_role:
        await interaction.response.send_message(
            f"The Steam ID `{steam_id}` is already registered by another user.", ephemeral=True
        )
        return

    # Create and assign the custom role
    custom_role = await guild.create_role(name=steam_id, color=discord.Color.default(), hoist=False)
    await member.add_roles(custom_role)

    # Store the user's Steam ID
    user_steam_ids[member.id] = steam_id

    # Get the "Registered Players" channel by ID
    registered_players_channel = guild.get_channel(REGISTERED_PLAYERS_CHANNEL_ID)
    if registered_players_channel is None:
        await interaction.response.send_message(
            "The 'Registered Players' channel does not exist. Please check the channel ID.", ephemeral=True
        )
        return

    # Output the registration information in the "Registered Players" channel
    await registered_players_channel.send(
        f"{member.name} : {steam_id} : /clan invite {steam_id}"
    )

    # Send confirmation message to the user
    await interaction.response.send_message(
        f"Successfully registered! The 'Regnbage' role has been assigned, and your registration info has been posted.",
        ephemeral=True
    )

# Call keep_alive to keep the bot alive
keep_alive()

# Run the bot
bot.run(TOKEN)
