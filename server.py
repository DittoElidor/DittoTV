import http.server
import socketserver
import json
import os
import posixpath
import urllib.parse
import re

PORT = 8000
HOST_IP = "10.100.102.10"
MEDIA_DIR = 'media'
WEB_DIR = 'web'
METADATA_FILE = 'metadata.json'

def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]+)', s)]

def load_metadata():
    if os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def find_poster(path):
    poster_path = os.path.join(path, 'poster.jpg')
    if os.path.exists(poster_path):
        return urllib.parse.quote(os.path.relpath(poster_path, os.getcwd()).replace("\\", "/"))
    return None

def get_description_from_metadata(metadata, category, title, season=None, episode_key=None):
    try:
        if category == 'movies':
            return metadata.get('movies', {}).get(title, {}).get('description')
        elif category == 'tv_shows':
            show_data = metadata.get('tv_shows', {}).get(title, {})
            if season and episode_key:
                return show_data.get('seasons', {}).get(season, {}).get(episode_key)
            return show_data.get('description')
    except Exception:
        return None
    return None

def generate_media_index():
    metadata = load_metadata()
    index = {"movies": [], "tv_shows": {}}

    movies_dir = os.path.join(MEDIA_DIR, 'Movies')
    if os.path.exists(movies_dir):
        for movie_folder in os.listdir(movies_dir):
            movie_path = os.path.join(movies_dir, movie_folder)
            if os.path.isdir(movie_path):
                movie_file = next((f for f in os.listdir(movie_path) if f.lower().endswith(('.mp4', '.mkv', '.avi'))), None)
                if movie_file:
                    index["movies"].append({
                        "title": movie_folder,
                        "poster_path": find_poster(movie_path),
                        "description": get_description_from_metadata(metadata, 'movies', movie_folder),
                        "path": f"{MEDIA_DIR}/Movies/{urllib.parse.quote(movie_folder)}/{urllib.parse.quote(movie_file)}"
                    })

    tv_shows_dir = os.path.join(MEDIA_DIR, 'TV Shows')
    if os.path.exists(tv_shows_dir):
        for show_name in os.listdir(tv_shows_dir):
            show_path = os.path.join(tv_shows_dir, show_name)
            if os.path.isdir(show_path):
                index["tv_shows"][show_name] = {
                    "poster_path": find_poster(show_path),
                    "description": get_description_from_metadata(metadata, 'tv_shows', show_name),
                    "seasons": {}
                }
                for season_name in os.listdir(show_path):
                    season_path = os.path.join(show_path, season_name)
                    if os.path.isdir(season_path):
                        index["tv_shows"][show_name]["seasons"][season_name] = []
                        sorted_episodes = sorted(os.listdir(season_path), key=natural_sort_key)
                        for episode_file in sorted_episodes:
                            if episode_file.lower().endswith(('.mp4', '.mkv', '.avi')):
                                base_name, _ = os.path.splitext(episode_file)
                                index["tv_shows"][show_name]["seasons"][season_name].append({
                                    "title": base_name,
                                    "description": get_description_from_metadata(metadata, 'tv_shows', show_name, season_name, base_name),
                                    "path": f"{MEDIA_DIR}/TV Shows/{urllib.parse.quote(show_name)}/{urllib.parse.quote(season_name)}/{urllib.parse.quote(episode_file)}"
                                })

    with open(os.path.join(WEB_DIR, 'media_index.json'), 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=4, ensure_ascii=False)
    print("✅ Media index from metadata generated successfully.")

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        path = path.split('?',1)[0].split('#',1)[0]
        path = posixpath.normpath(urllib.parse.unquote(path))
        words = [w for w in path.split('/') if w]
        path = os.getcwd()
        for word in words:
            path = os.path.join(path, word)
        return path

if __name__ == "__main__":
    generate_media_index()
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer((HOST_IP, PORT), CustomHandler) as httpd:
        print(f"🚀 Server starting at http://{HOST_IP}:{PORT}")
        httpd.serve_forever()

