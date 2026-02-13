import os
import re
import sys
from itertools import islice

import instaloader
from colorama import Fore, Style, init


def print_info(message: str) -> None:
    print(f"{Fore.CYAN}{message}{Style.RESET_ALL}")


def print_success(message: str) -> None:
    print(f"{Fore.GREEN}{message}{Style.RESET_ALL}")


def print_error(message: str) -> None:
    print(f"{Fore.RED}{message}{Style.RESET_ALL}")


def extract_shortcode(value: str) -> str | None:
    value = value.strip()
    if not value:
        return None

    if "/" not in value:
        return value

    match = re.search(r"/(p|reel|tv)/([A-Za-z0-9_-]+)/?", value)
    if not match:
        return None

    return match.group(2)


def handle_single_post(loader: instaloader.Instaloader, url: str) -> None:
    shortcode = extract_shortcode(url)
    if not shortcode:
        print_error("Invalid URL or shortcode.")
        return

    print_info("Starting download...")
    try:
        post = instaloader.Post.from_shortcode(loader.context, shortcode)
        username = post.owner_username
        os.makedirs(username, exist_ok=True)
        loader.download_post(post, target=username)
        print_success(f"Success: Post saved to '{username}'.")
    except instaloader.BadResponseException:
        print_error("Failed to fetch the post. Check the URL and try again.")
    except instaloader.QueryReturnedNotFoundException:
        print_error("Post not found.")
    except instaloader.PrivateProfileNotFollowedException:
        print_error("Private account: login required or follow the account first.")
    except Exception as exc:
        print_error(f"Unexpected error: {exc}")


def handle_profile_posts(loader: instaloader.Instaloader, username: str) -> None:
    username = username.strip()
    if not username:
        print_error("Username cannot be empty.")
        return

    print_info("Starting download...")
    try:
        profile = instaloader.Profile.from_username(loader.context, username)
        os.makedirs(username, exist_ok=True)

        posts = islice(profile.get_posts(), 5)
        downloaded = 0
        for index, post in enumerate(posts, start=1):
            print_info(f"Downloading post {index}/5...")
            loader.download_post(post, target=username)
            downloaded += 1

        if downloaded == 0:
            print_info("No posts found to download.")
        else:
            print_success(f"Success: {downloaded} post(s) saved to '{username}'.")
    except instaloader.ProfileNotExistsException:
        print_error("Profile not found.")
    except instaloader.PrivateProfileNotFollowedException:
        print_error("Private account: login required or follow the account first.")
    except instaloader.BadResponseException:
        print_error("Failed to fetch profile data. Try again later.")
    except Exception as exc:
        print_error(f"Unexpected error: {exc}")


def main() -> None:
    init(autoreset=True)
    print_info("Choose an option:")
    print_info("A) Download a single post via URL")
    print_info("B) Download the last 5 posts from a profile")
    choice = input("Enter A or B: ").strip().lower()

    loader = instaloader.Instaloader(
        dirname_pattern="{target}",
        save_metadata=False,
        download_videos=True,
        download_video_thumbnails=False,
        download_geotags=False,
        download_comments=False,
    )

    if choice == "a":
        url = input("Enter the post URL (or shortcode): ").strip()
        handle_single_post(loader, url)
    elif choice == "b":
        username = input("Enter the profile username: ").strip()
        handle_profile_posts(loader, username)
    else:
        print_error("Invalid option. Please enter A or B.")
        sys.exit(1)


if __name__ == "__main__":
    main()
