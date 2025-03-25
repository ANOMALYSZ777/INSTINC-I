import instaloader
import requests
import re
import json
import os
import sys
from bs4 import BeautifulSoup
from colorama import Fore, Style, init

init(autoreset=True)

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    banner = """
██╗███╗   ██╗███████╗████████╗██╗███╗   ██╗ ██████╗ ██╗    
██║████╗  ██║██╔════╝╚══██╔══╝██║████╗  ██║██╔════╝ ██║    
██║██╔██╗ ██║███████╗   ██║   ██║██╔██╗ ██║██║█████╗██║    
██║██║╚██╗██║╚════██║   ██║   ██║██║╚██╗██║██║╚════╝██║    
██║██║ ╚████║███████║   ██║   ██║██║ ╚████║╚██████╗ ██║    
╚═╝╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚═╝╚═╝  ╚═══╝ ╚═════╝ ╚═╝    
    """
    print(Fore.MAGENTA + banner + Style.RESET_ALL)
    print(Fore.MAGENTA + "INSTINC-I")
    print(Fore.LIGHTCYAN_EX + "Version : INSTAGRAM PREMIUM PRO LATEST")
    print(Fore.RED + "Author : ANOMALYSZ777")
    print(Fore.RED + "Github : https://github.com/ANOMALYSZ777")
    print(Fore.RED + "Support : !IBRAHIM404!, GhastUZero, VoidWalkers")
    print(Fore.RED + "Team : VoidWalkers")
    print()
    print(Fore.YELLOW + "Instagram Osint Tool by VoidWalkers Team 🔥")
    print()

def authenticate_instaloader():
    loader = instaloader.Instaloader()
    username = input(Fore.CYAN + "Masukkan username Instagram untuk login (tekan enter untuk skip): " + Style.RESET_ALL)
    if username:
        password = input(Fore.CYAN + "Masukkan password Instagram: " + Style.RESET_ALL)
        try:
            loader.login(username, password)
            print(Fore.GREEN + "[+] Login berhasil!" + Style.RESET_ALL)
        except Exception as e:
            print(Fore.RED + f"[-] Gagal login: {e}" + Style.RESET_ALL)
            sys.exit(1)
    return loader

def get_instagram_profile(loader, username):
    try:
        profile = instaloader.Profile.from_username(loader.context, username)
        data = {
            "Username": profile.username,
            "Full Name": profile.full_name,
            "Bio": profile.biography,
            "Followers": profile.followers,
            "Following": profile.followees,
            "Posts": profile.mediacount,
            "External URL": profile.external_url,
            "Verified": profile.is_verified,
            "Business Account": profile.is_business_account,
            "Profile Picture URL": profile.profile_pic_url,
            "Is Private": profile.is_private,
            "Last Post Timestamp": profile.get_posts()[0].date_utc if profile.mediacount > 0 else "No Posts",
            "Account Status": "Active" if profile.is_private is not None else "Banned/Inactive"
        }
        return data
    except Exception as e:
        return {"error": str(e)}

def download_profile_picture(loader, username):
    try:
        profile = instaloader.Profile.from_username(loader.context, username)
        loader.download_profilepic(profile)
        return Fore.GREEN + f"Profile picture downloaded: {profile.username}_profile_pic.jpg" + Style.RESET_ALL
    except Exception as e:
        return Fore.RED + f"Error downloading profile picture: {str(e)}" + Style.RESET_ALL

def extract_emails(text):
    return re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)

def check_username_footprint(username):
    try:
        response = os.popen(f"holehe {username}").read()
        return response
    except Exception as e:
        return Fore.RED + f"Error checking footprint: {str(e)}" + Style.RESET_ALL

def scrape_posts(loader, username):
    try:
        profile = instaloader.Profile.from_username(loader.context, username)
        posts = []
        for post in profile.get_posts():
            posts.append({
                "Post URL": f"https://www.instagram.com/p/{post.shortcode}/",
                "Likes": post.likes,
                "Comments": post.comments,
                "Caption": post.caption,
                "Hashtags": post.caption_hashtags,
                "Timestamp": post.date_utc
            })
            if len(posts) >= 5:
                break
        return posts
    except Exception as e:
        return {"error": str(e)}

def get_story_highlights(username):
    url = f"https://www.instagram.com/stories/{username}/"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        stories = []
        for script in soup.find_all("script"):
            if "story" in script.text:
                stories.append(script.text)
        return stories if stories else "No stories found"
    return "Unable to fetch stories"

def main():
    clear_terminal()
    print_banner()
    loader = authenticate_instaloader()
    username = input(Fore.CYAN + "Masukkan username Instagram: " + Style.RESET_ALL)
    print(Fore.YELLOW + "[+] Mengambil data profil..." + Style.RESET_ALL)
    profile_data = get_instagram_profile(loader, username)
    
    if "error" in profile_data:
        print(Fore.RED + "[-] Gagal mengambil data profil:" + profile_data["error"] + Style.RESET_ALL)
        return
    
    print(json.dumps(profile_data, indent=4))
    
    print(Fore.YELLOW + "[+] Mengunduh foto profil..." + Style.RESET_ALL)
    print(download_profile_picture(loader, username))
    
    if profile_data["External URL"]:
        print(Fore.YELLOW + "[+] Mencari email dalam bio..." + Style.RESET_ALL)
        emails = extract_emails(profile_data["External URL"])
        if emails:
            print(Fore.GREEN + "[!] Email ditemukan:" + str(emails) + Style.RESET_ALL)
        else:
            print(Fore.RED + "[-] Tidak ada email ditemukan dalam bio." + Style.RESET_ALL)
    
    print(Fore.YELLOW + "[+] Mencari jejak username di platform lain..." + Style.RESET_ALL)
    footprint = check_username_footprint(username)
    print(footprint)
    
    print(Fore.YELLOW + "[+] Mengambil 5 postingan terbaru..." + Style.RESET_ALL)
    posts = scrape_posts(loader, username)
    print(json.dumps(posts, indent=4))
    
    print(Fore.YELLOW + "[+] Mengambil highlight & stories..." + Style.RESET_ALL)
    highlights = get_story_highlights(username)
    print(highlights)
    
if __name__ == "__main__":
    main()
