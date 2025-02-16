import discord
from discord.ext import commands
from data import fetch_user_data, fetch_manga_data, fetch_anime_data, fetch_manhwa_data, extract_important_manga_info, extract_important_anime_info, extract_important_manhwa_info, fetch_gif, fetch_user_anime_list, fetch_user_manga_list, fetch_full_user_anime_list, fetch_full_user_manga_list, calculate_compatibility, fetch_kitsu_anime_data, fetch_kitsu_manga_data, compare_anime_manga
from app_token import token

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.command()
async def ping(ctx):
    await ctx.send('Pong!')

@bot.command()
async def manga(ctx, *manga_name):
    manga_name = " ".join(manga_name)
    manga_data = fetch_manga_data(manga_name)
    important_info = extract_important_manga_info(manga_data, manga_name)
    if important_info:
        embed = discord.Embed(title=important_info['title'], url=important_info['url'])
        embed.add_field(name="Score", value=important_info['score'])
        embed.add_field(name="Rank", value=important_info['rank'])
        embed.add_field(name="Popularity", value=important_info['popularity'])
        embed.add_field(name="Members", value=important_info['members'])
        embed.set_image(url=important_info['image_url'])
        await ctx.send(embed=embed)
    else:
        await ctx.send(f"Could not find manga with name {manga_name}")

@bot.command()
async def anime(ctx, *anime_name):
    anime_name = " ".join(anime_name)
    anime_data = fetch_anime_data(anime_name)
    important_info = extract_important_anime_info(anime_data, anime_name)
    if important_info:
        embed = discord.Embed(title=important_info['title'], url=important_info['url'])
        embed.add_field(name="Score", value=important_info['score'])
        embed.add_field(name="Rank", value=important_info['rank'])
        embed.add_field(name="Popularity", value=important_info['popularity'])
        embed.add_field(name="Members", value=important_info['members'])
        embed.set_image(url=important_info['image_url'])
        await ctx.send(embed=embed)
    else:
        await ctx.send(f"Could not find anime with name {anime_name}")

@bot.command()
async def manhwa(ctx, *manhwa_name):
    manhwa_name = " ".join(manhwa_name)
    manhwa_data = fetch_manhwa_data(manhwa_name)
    important_info = extract_important_manhwa_info(manhwa_data, manhwa_name)
    if important_info:
        embed = discord.Embed(title=important_info['title'], url=important_info['url'])
        embed.add_field(name="Score", value=important_info['score'])
        embed.add_field(name="Rank", value=important_info['rank'])
        embed.add_field(name="Popularity", value=important_info['popularity'])
        embed.add_field(name="Members", value=important_info['members'])
        embed.set_image(url=important_info['image_url'])
        await ctx.send(embed=embed)
    else:
        await ctx.send(f"Could not find manhwa with name {manhwa_name}")

@bot.command()
async def user(ctx, username):
    user_data = fetch_user_data(username)
    top_5_anime = fetch_user_anime_list(username)
    top_5_manga = fetch_user_manga_list(username)
    if user_data and top_5_anime and top_5_manga:
        embed = discord.Embed(title=user_data['username'], url=user_data['url'])
        
        about = user_data['about'] or "No information available"
        if len(about) > 1024:
            about = about[:1021] + "..."
        embed.add_field(name="About", value=about, inline=False)
        
        embed.add_field(name="Anime Count", value=user_data['anime_stats']['count'])
        embed.add_field(name="Anime Mean Score", value=user_data['anime_stats']['meanScore'])
        embed.add_field(name="Minutes Watched", value=user_data['anime_stats']['minutesWatched'])
        embed.add_field(name="Manga Count", value=user_data['manga_stats']['count'])
        embed.add_field(name="Manga Mean Score", value=user_data['manga_stats']['meanScore'])
        embed.add_field(name="Chapters Read", value=user_data['manga_stats']['chaptersRead'])
        embed.set_image(url=user_data['avatar_url'])
        if user_data['banner_image']:
            embed.set_thumbnail(url=user_data['banner_image'])
        
        anime_list_str = "\n".join([f"{anime['title']} - {anime['score']}" for anime in top_5_anime])
        if len(anime_list_str) > 1024:
            anime_list_str = anime_list_str[:1021] + "..."
        embed.add_field(name="Top 5 Completed Anime", value=anime_list_str, inline=False)
        
        manga_list_str = "\n".join([f"{manga['title']} - {manga['score']}" for manga in top_5_manga])
        if len(manga_list_str) > 1024:
            manga_list_str = manga_list_str[:1021] + "..."
        embed.add_field(name="Top 5 Completed Manga", value=manga_list_str, inline=False)
        
        await ctx.send(embed=embed)
    else:
        await ctx.send(f"Could not find user with username {username}")

@bot.command()
async def animegif(ctx, *, anime_name):
    gif_url = fetch_gif(anime_name)
    if gif_url:
        await ctx.send(gif_url)
    else:
        await ctx.send(f"Could not find a GIF for {anime_name}")

@bot.command()
async def usercompare(ctx, username1, username2):
    anime_list1 = fetch_full_user_anime_list(username1)
    anime_list2 = fetch_full_user_anime_list(username2)
    manga_list1 = fetch_full_user_manga_list(username1)
    manga_list2 = fetch_full_user_manga_list(username2)
    
    if anime_list1 is None or anime_list2 is None or manga_list1 is None or manga_list2 is None:
        await ctx.send(f"Could not fetch anime or manga lists for one or both users: {username1}, {username2}")
        return
    
    common_anime = [anime for anime in anime_list1 if anime in anime_list2]
    common_manga = [manga for manga in manga_list1 if manga in manga_list2]
    
    anime_jaccard = calculate_compatibility(anime_list1, anime_list2)
    manga_jaccard = calculate_compatibility(manga_list1, manga_list2)
    overall_jaccard = (anime_jaccard + manga_jaccard) / 2
    
    embed = discord.Embed(title=f"Common Anime and Manga between {username1} and {username2}", color=0x00ff00)
    
    if common_anime:
        common_anime_str = "\n".join([f"{anime['title']} - {anime['score']}" for anime in common_anime])
        if len(common_anime_str) > 1024:
            common_anime_str = common_anime_str[:1021] + "..."
        embed.add_field(name="Common Anime", value=common_anime_str, inline=False)
    else:
        embed.add_field(name="Common Anime", value="No common anime found", inline=False)
    
    if common_manga:
        common_manga_str = "\n".join([f"{manga['title']} - {manga['score']}" for manga in common_manga])
        if len(common_manga_str) > 1024:
            common_manga_str = common_manga_str[:1021] + "..."
        embed.add_field(name="Common Manga", value=common_manga_str, inline=False)
    else:
        embed.add_field(name="Common Manga", value="No common manga found", inline=False)
    
    embed.add_field(name="Anime Compatibility", value=f"{anime_jaccard:.2f}%", inline=False)
    embed.add_field(name="Manga Compatibility", value=f"{manga_jaccard:.2f}%", inline=False)
    embed.add_field(name="Overall Compatibility", value=f"{overall_jaccard:.2f}%", inline=False)
    
    await ctx.send(embed=embed)

@bot.command()
async def animecompare(ctx, *, anime_names):
    try:
        anime1_name, anime2_name = anime_names.split(' - ')
    except ValueError:
        await ctx.send("Please use the format: !animecompare <anime1> - <anime2>")
        return
    
    anime1_data = fetch_kitsu_anime_data(anime1_name)
    anime2_data = fetch_kitsu_anime_data(anime2_name)
    
    if anime1_data and anime2_data:
        comparison = compare_anime_manga(anime1_data, anime2_data)
        
        embed = discord.Embed(title=f"Comparison between {comparison['title1']} and {comparison['title2']}", color=0x00ff00)
        
        embed.add_field(name=comparison['title1'], value=f"Average Rating: {comparison['average_rating1']}\nPopularity Rank: {comparison['popularity_rank1']}\nRating Rank: {comparison['rating_rank1']}\nPoster Image: {comparison['poster_image1']}", inline=True)
        
        embed.add_field(name=comparison['title2'], value=f"Average Rating: {comparison['average_rating2']}\nPopularity Rank: {comparison['popularity_rank2']}\nRating Rank: {comparison['rating_rank2']}\nPoster Image: {comparison['poster_image2']}", inline=True)
        
        await ctx.send(embed=embed)
    else:
        await ctx.send(f"Could not find data for one or both anime: {anime1_name}, {anime2_name}")

@bot.command()
async def mangacompare(ctx, *, manga_names):
    try:
        manga1_name, manga2_name = manga_names.split(' - ')
    except ValueError:
        await ctx.send("Please use the format: !mangacompare <manga1> - <manga2>")
        return
    
    manga1_data = fetch_kitsu_manga_data(manga1_name)
    manga2_data = fetch_kitsu_manga_data(manga2_name)
    
    if manga1_data and manga2_data:
        comparison = compare_anime_manga(manga1_data, manga2_data)
        
        embed = discord.Embed(title=f"Comparison between {comparison['title1']} and {comparison['title2']}", color=0x00ff00)
        
        embed.add_field(name=comparison['title1'], value=f"Average Rating: {comparison['average_rating1']}\nPopularity Rank: {comparison['popularity_rank1']}\nRating Rank: {comparison['rating_rank1']}\nPoster Image: {comparison['poster_image1']}", inline=True)
        
        embed.add_field(name=comparison['title2'], value=f"Average Rating: {comparison['average_rating2']}\nPopularity Rank: {comparison['popularity_rank2']}\nRating Rank: {comparison['rating_rank2']}\nPoster Image: {comparison['poster_image2']}", inline=True)
        
        await ctx.send(embed=embed)
    else:
        await ctx.send(f"Could not find data for one or both manga: {manga1_name}, {manga2_name}")

@bot.command(name='commands')
async def show_commands(ctx):
    embed = discord.Embed(title="Bot Commands", description="List of available commands", color=0x00ff00)
    
    embed.add_field(name="!ping", value="Check if the bot is online. Responds with 'Pong!'", inline=False)
    embed.add_field(name="!manga <manga_name>", value="Fetch information about a manga by its name.", inline=False)
    embed.add_field(name="!anime <anime_name>", value="Fetch information about an anime by its name.", inline=False)
    embed.add_field(name="!manhwa <manhwa_name>", value="Fetch information about a manhwa by its name.", inline=False)
    embed.add_field(name="!user <username>", value="Fetch information about a user and their top 5 anime.", inline=False)
    embed.add_field(name="!animegif <anime_name>", value="Fetch a GIF related to the specified anime.", inline=False)
    embed.add_field(name="!usercompare <username1> <username2>", value="Compare anime and manga lists between two users.", inline=False)
    embed.add_field(name="!animecompare <anime1> - <anime2>", value="Compare two anime using the Kitsu API.", inline=False)
    embed.add_field(name="!mangacompare <manga1> - <manga2>", value="Compare two manga using the Kitsu API.", inline=False)
    
    await ctx.send(embed=embed)

bot.run(token)