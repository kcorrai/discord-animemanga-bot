from app_token import giphy_token, mal_client_id, mal_client_secret
import requests
import random
from bs4 import BeautifulSoup

def fetch_anime_data(anime_name):
    url = f"https://api.jikan.moe/v4/anime?q={anime_name}"
    response = requests.get(url)
    return response.json()

def extract_important_anime_info(anime_data, anime_name):
    if (anime_data['data']):
        anime = anime_data['data'][0]
        info = {
            'title': anime['title'],
            'score': anime['score'],
            'url': anime['url'],
            'image_url': anime['images']['jpg']['image_url'],
            'rank': anime['rank'],
            'popularity': anime['popularity'],
            'members': anime['members']
        }
        return info
    return None

def fetch_manga_data(manga_name):
    url = f"https://api.jikan.moe/v4/manga?q={manga_name}"
    response = requests.get(url)
    return response.json()

def extract_important_manga_info(manga_data, manga_name):
    if (manga_data['data']):
        manga = manga_data['data'][0]
        info = {
            'title': manga['title'],
            'score': manga['score'],
            'url': manga['url'],
            'image_url': manga['images']['jpg']['image_url'],
            'rank': manga['rank'],
            'popularity': manga['popularity'],
            'members': manga['members']
        }
        return info
    return None

def fetch_manhwa_data(manhwa_name):
    url = f"https://api.jikan.moe/v4/manga?q={manhwa_name}&type=manhwa"
    response = requests.get(url)
    return response.json()

def extract_important_manhwa_info(manhwa_data, manhwa_name):
    if (manhwa_data['data']):
        manhwa = manhwa_data['data'][0]
        info = {
            'title': manhwa['title'],
            'score': manhwa['score'],
            'url': manhwa['url'],
            'image_url': manhwa['images']['jpg']['image_url'],
            'rank': manhwa['rank'],
            'popularity': manhwa['popularity'],
            'members': manhwa['members']
        }
        return info
    return None

def fetch_user_data(username):
    url = "https://graphql.anilist.co"
    query = '''
    query ($username: String) {
        User(name: $username) {
            id
            name
            about
            avatar {
                large
            }
            bannerImage
            siteUrl
            updatedAt
            statistics {
                anime {
                    count
                    meanScore
                    minutesWatched
                }
                manga {
                    count
                    meanScore
                    chaptersRead
                }
            }
        }
    }
    '''
    variables = {
        'username': username
    }
    response = requests.post(url, json={'query': query, 'variables': variables})
    
    if (response.status_code == 200):
        data = response.json()
        if ('data' in data and 'User' in data['data']):
            user = data['data']['User']
            user_info = {
                'id': user['id'],
                'username': user['name'],
                'about': user['about'],
                'avatar_url': user['avatar']['large'],
                'banner_image': user['bannerImage'],
                'url': user['siteUrl'],
                'last_online': user['updatedAt'],
                'anime_stats': user['statistics']['anime'],
                'manga_stats': user['statistics']['manga']
            }
            return user_info
        else:
            print("User not found.")
            return None
    else:
        print(f"Failed to fetch user data. Status code: {response.status_code}, Response: {response.text}")
        return None

def get_mal_access_token():
    url = "https://myanimelist.net/v1/oauth2/token"
    data = {
        'grant_type': 'client_credentials',
        'client_id': mal_client_id,
        'client_secret': mal_client_secret
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.post(url, data=data, headers=headers)
    
    if (response.status_code == 200):
        return response.json().get('access_token')
    else:
        print(f"Failed to obtain access token. Status code: {response.status_code}")
        print(f"Response content: {response.content.decode('utf-8')}")
        return None

def fetch_user_anime_list(username):
    url = "https://graphql.anilist.co"
    query = '''
    query ($username: String) {
        MediaListCollection(userName: $username, type: ANIME, status: COMPLETED) {
            lists {
                entries {
                    media {
                        title {
                            romaji
                        }
                        averageScore
                        siteUrl
                        coverImage {
                            large
                        }
                    }
                }
            }
        }
    }
    '''
    variables = {
        'username': username
    }
    response = requests.post(url, json={'query': query, 'variables': variables})
    
    if response.status_code == 200:
        data = response.json()
        if 'data' in data and 'MediaListCollection' in data['data'] and data['data']['MediaListCollection']['lists']:
            anime_list = data['data']['MediaListCollection']['lists'][0]['entries']
            sorted_anime = sorted(anime_list, key=lambda x: (x['media']['averageScore'] is not None, x['media']['averageScore']), reverse=True)
            top_5_anime = [{'title': anime['media']['title']['romaji'], 'score': anime['media']['averageScore']} for anime in sorted_anime[:5]]
            return top_5_anime
        else:
            print("No data found in anime list response.")
    else:
        print(f"Failed to fetch anime list. Status code: {response.status_code}, Response: {response.text}")
    return None

def fetch_user_manga_list(username):
    url = "https://graphql.anilist.co"
    query = '''
    query ($username: String) {
        MediaListCollection(userName: $username, type: MANGA, status: COMPLETED) {
            lists {
                entries {
                    media {
                        title {
                            romaji
                        }
                        averageScore
                        siteUrl
                        coverImage {
                            large
                        }
                    }
                }
            }
        }
    }
    '''
    variables = {
        'username': username
    }
    response = requests.post(url, json={'query': query, 'variables': variables})
    
    if response.status_code == 200:
        data = response.json()
        if 'data' in data and 'MediaListCollection' in data['data'] and data['data']['MediaListCollection']['lists']:
            manga_list = data['data']['MediaListCollection']['lists'][0]['entries']
            sorted_manga = sorted(manga_list, key=lambda x: (x['media']['averageScore'] is not None, x['media']['averageScore']), reverse=True)
            top_5_manga = [{'title': manga['media']['title']['romaji'], 'score': manga['media']['averageScore']} for manga in sorted_manga[:5]]
            return top_5_manga
        else:
            print("No data found in manga list response.")
    else:
        print(f"Failed to fetch manga list. Status code: {response.status_code}, Response: {response.text}")
    return None

def fetch_full_user_anime_list(username):
    url = "https://graphql.anilist.co"
    query = '''
    query ($username: String) {
        MediaListCollection(userName: $username, type: ANIME, status: COMPLETED) {
            lists {
                entries {
                    media {
                        id
                        title {
                            romaji
                        }
                        averageScore
                        siteUrl
                        coverImage {
                            large
                        }
                    }
                }
            }
        }
    }
    '''
    variables = {
        'username': username
    }
    response = requests.post(url, json={'query': query, 'variables': variables})
    
    if response.status_code == 200:
        data = response.json()
        if 'data' in data and 'MediaListCollection' in data['data'] and data['data']['MediaListCollection']['lists']:
            anime_list = data['data']['MediaListCollection']['lists'][0]['entries']
            sorted_anime = sorted(anime_list, key=lambda x: (x['media']['averageScore'] is not None, x['media']['averageScore']), reverse=True)
            full_anime_list = [{'id': anime['media']['id'], 'title': anime['media']['title']['romaji'], 'score': anime['media']['averageScore']} for anime in sorted_anime]
            return full_anime_list
        else:
            print("No data found in anime list response.")
    else:
        print(f"Failed to fetch anime list. Status code: {response.status_code}, Response: {response.text}")
    return None

def fetch_full_user_manga_list(username):
    url = "https://graphql.anilist.co"
    query = '''
    query ($username: String) {
        MediaListCollection(userName: $username, type: MANGA, status: COMPLETED) {
            lists {
                entries {
                    media {
                        title {
                            romaji
                        }
                        averageScore
                        siteUrl
                        coverImage {
                            large
                        }
                    }
                }
            }
        }
    }
    '''
    variables = {
        'username': username
    }
    response = requests.post(url, json={'query': query, 'variables': variables})
    
    if response.status_code == 200:
        data = response.json()
        if 'data' in data and 'MediaListCollection' in data['data'] and data['data']['MediaListCollection']['lists']:
            manga_list = data['data']['MediaListCollection']['lists'][0]['entries']
            sorted_manga = sorted(manga_list, key=lambda x: (x['media']['averageScore'] is not None, x['media']['averageScore']), reverse=True)
            full_manga_list = [{'title': manga['media']['title']['romaji'], 'score': manga['media']['averageScore']} for manga in sorted_manga]
            return full_manga_list
        else:
            print("No data found in manga list response.")
    else:
        print(f"Failed to fetch manga list. Status code: {response.status_code}, Response: {response.text}")
    return None

def fetch_gif(anime_name):
    url = f"https://api.giphy.com/v1/gifs/search?api_key={giphy_token}&q={anime_name}&limit=1&rating=g"
    response = requests.get(url)
    gif_data = response.json()
    
    if 'data' in gif_data and len(gif_data['data']) > 0:
        gif_url = gif_data['data'][0]['images']['original']['url']
        return gif_url
    return None

def calculate_compatibility(list1, list2):
    set1 = set(item['title'] for item in list1)
    set2 = set(item['title'] for item in list2)
    intersection = set1.intersection(set2)
    union = set1.union(set2)
    if not union:
        return 0
    return (len(intersection) / len(union)) * 100

def fetch_similar_anime(anime_id):
    url = f"https://api.jikan.moe/v4/anime/{anime_id}/recommendations"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if 'data' in data:
            return data['data']
    return []

def fetch_similar_anime_anilist(anime_id):
    url = "https://graphql.anilist.co"
    query = '''
    query ($id: Int) {
        Media(id: $id) {
            recommendations {
                edges {
                    node {
                        mediaRecommendation {
                            id
                            title {
                                romaji
                            }
                            averageScore
                            siteUrl
                            coverImage {
                                large
                            }
                        }
                    }
                }
            }
        }
    }
    '''
    variables = {
        'id': anime_id
    }
    response = requests.post(url, json={'query': query, 'variables': variables})
    if response.status_code == 200:
        data = response.json()
        if 'data' in data and 'Media' in data['data'] and 'recommendations' in data['data']['Media']:
            return data['data']['Media']['recommendations']['edges']
    return []

def fetch_kitsu_anime_data(anime_name):
    url = f"https://kitsu.io/api/edge/anime?filter[text]={anime_name}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data['data']:
            anime = data['data'][0]
            return {
                'title': anime['attributes']['canonicalTitle'],
                'average_rating': anime['attributes']['averageRating'],
                'popularity_rank': anime['attributes']['popularityRank'],
                'rating_rank': anime['attributes']['ratingRank'],
                'start_date': anime['attributes']['startDate'],
                'end_date': anime['attributes']['endDate'],
                'synopsis': anime['attributes']['synopsis'],
                'poster_image': anime['attributes']['posterImage']['original']
            }
    return None

def fetch_kitsu_manga_data(manga_name):
    url = f"https://kitsu.io/api/edge/manga?filter[text]={manga_name}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data['data']:
            manga = data['data'][0]
            return {
                'title': manga['attributes']['canonicalTitle'],
                'average_rating': manga['attributes']['averageRating'],
                'popularity_rank': manga['attributes']['popularityRank'],
                'rating_rank': manga['attributes']['ratingRank'],
                'start_date': manga['attributes']['startDate'],
                'end_date': manga['attributes']['endDate'],
                'synopsis': manga['attributes']['synopsis'],
                'poster_image': manga['attributes']['posterImage']['original']
            }
    return None

def compare_anime_manga(anime1, anime2):
    comparison = {
        'title1': anime1['title'],
        'title2': anime2['title'],
        'average_rating1': anime1['average_rating'],
        'average_rating2': anime2['average_rating'],
        'popularity_rank1': anime1['popularity_rank'],
        'popularity_rank2': anime2['popularity_rank'],
        'rating_rank1': anime1['rating_rank'],
        'rating_rank2': anime2['rating_rank'],
        'poster_image1': anime1['poster_image'],
        'poster_image2': anime2['poster_image']
    }
    return comparison