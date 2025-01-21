import discord
from discord.ext import commands
from discord import app_commands
import aiohttp

# Replace these variables with your bot's information and your server settings
TOKEN = 'YOUR_BOT_TOKEN_HERE'  # Replace with your bot token
GUILD_ID = YOUR_GUILD_ID_HERE  # Replace with your guild/server ID
REGNBAGE_ROLE_ID = YOUR_REGNBAGE_ROLE_ID_HERE  # Replace with the role ID for "Regnbage"

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

async def get_battlemetrics_hours(steam_id):
    """Fetch the Rust playtime in hours from BattleMetrics."""
    api_url = f"https://api.battlemetrics.com/players/{steam_id}"
    headers = {"Authorization": "Bearer YOUR_BATTLEMETRICS_API_KEY_HERE"}  # Replace with your API key
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    rust_hours = data.get("data", {}).get("attributes", {}).get("timePlayed", 0) / 3600  # Convert seconds to hours
                    return rust_hours
                else:
                    return None
    except Exception as e:
        print(f"Error fetching BattleMetrics data: {e}")
        return None

@bot.event
async def on_ready():
    print(f'Bot connected as {bot.user}')
    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} command(s).')
    except Exception as e:
        print(f'Error syncing commands: {e}')

@bot.command()
async def register(ctx):
    if ctx.channel.name == 'registration':
        await ctx.author.send(
            "Welcome to Regnbage! To play, you must register your Steam ID.\n"
            "Please use the command: `/register <Steam 64>` in the server."
        )
    else:
        await ctx.send("Please use this command in the #registration channel.")

@bot.tree.command(name="register")
@app_commands.describe(steam_id="Your Steam 64 ID")
async def register_command(interaction: discord.Interaction, steam_id: str):
    guild = interaction.guild
    member = interaction.user

    # Fetch Rust hours from BattleMetrics
    rust_hours = await get_battlemetrics_hours(steam_id)

    if rust_hours is None:
        await interaction.response.send_message(
            "Unable to fetch playtime from BattleMetrics. Please check your Steam ID and try again.",
            ephemeral=True
        )
        return

    if rust_hours < 1000:
        await interaction.response.send_message(
            f"Your playtime is {rust_hours:.2f} hours, which is below the required 1000 hours to join.",
            ephemeral=True
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

    # Create and assign the custom role
    custom_role_name = steam_id
    existing_role = discord.utils.get(guild.roles, name=custom_role_name)

    if not existing_role:
        custom_role = await guild.create_role(name=custom_role_name, color=discord.Color.default(), hoist=False)
    else:
        custom_role = existing_role

    await member.add_roles(custom_role)

    # Send confirmation message
    await interaction.response.send_message(
        f"Successfully registered! The 'Regnbage' role and your custom role `{custom_role_name}` have been assigned."
        f" Your playtime is {rust_hours:.2f} hours.",
        ephemeral=True
    )

# Run the bot
bot.run(TOKEN)
