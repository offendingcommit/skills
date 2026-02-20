#!/usr/bin/env python3
"""Reddit archive tool — download images, GIFs, videos from users or subreddits."""
import argparse, json, os, subprocess, sys
import shutil
import threading

# Check dependencies on import
def check_dependencies():
    """Check and install required dependencies."""
    missing = []
    
    # Check requests
    try:
        import requests
    except ImportError:
        missing.append('requests')
    
    # Check yt-dlp
    ytdlp_path = find_ytdlp()
    if not ytdlp_path:
        missing.append('yt-dlp')
    
    if missing:
        print("Installing missing dependencies:", ", ".join(missing))
        install_dependencies(missing)

def find_ytdlp():
    """Find yt-dlp in common locations or PATH."""
    # Check environment override
    env_path = os.environ.get("YTDLP_PATH")
    if env_path and os.path.isfile(env_path) and os.access(env_path, os.X_OK):
        return env_path
    
    # Check common system paths
    common_paths = [
        "/usr/local/bin/yt-dlp",
        "/opt/homebrew/bin/yt-dlp",
        "/opt/bin/yt-dlp",
        os.path.expanduser("~/.local/bin/yt-dlp"),
    ]
    
    for path in common_paths:
        if os.path.isfile(path) and os.access(path, os.X_OK):
            return path
    
    # Check in PATH
    ytdlp_in_path = shutil.which("yt-dlp")
    if ytdlp_in_path:
        return ytdlp_in_path
    
    return None

def install_dependencies(missing):
    """Install missing Python packages."""
    packages = []
    
    if 'requests' in missing:
        packages.append('requests')
    if 'yt-dlp' in missing:
        packages.append('yt-dlp')
    
    if packages:
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "--user"] + packages,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            print("Dependencies installed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Warning: Failed to install dependencies: {e}")
            print("Please install manually: pip3 install requests yt-dlp")
            sys.exit(1)

# Run dependency check on import
check_dependencies()

# Now import after check
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import time
import requests

HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36", "Accept": "application/json"}
YTDLP = find_ytdlp() or "yt-dlp"
IMAGE_EXTS = (".jpg", ".jpeg", ".png", ".webp")

def reddit_get(url):
    r = requests.get(url, headers=HEADERS, timeout=15)
    r.raise_for_status()
    return r.json()

def to_utc_timestamp(date_str):
    """Convert YYYY-MM-DD to Reddit's created_utc timestamp."""
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return int(dt.replace(tzinfo=timezone.utc).timestamp())

def get_posts(args):
    """Fetch posts from user or subreddit."""
    target = args.user or args.subreddit
    posts = []
    after = None
    page = 0
    
    # Build base URL with sort
    sort = args.sort or "hot"
    if args.user:
        base_url = f"https://www.reddit.com/user/{args.user}/submitted.json?limit=100&raw_json=1"
    else:
        # For subreddits, support sort: hot, new, rising, top, controversial
        base_url = f"https://www.reddit.com/r/{args.subreddit}/{sort}.json?limit=100&raw_json=1"
        # Add time filter for top/controversial
        if sort in ("top", "controversial") and args.time:
            base_url += f"&t={args.time}"
    
    # Add date filters if specified
    if args.after:
        base_url += f"&after=t3_{'a'*6}"  # placeholder, we'll filter manually
    
    while True:
        url = base_url
        if after:
            url += f"&after={after}"
        
        print(f"  fetching page {page + 1}...")
        data = reddit_get(url)
        children = data.get("data", {}).get("children", [])
        
        if not children:
            break
            
        for c in children:
            post = c.get("data", {})
            
            # Date filtering
            created_utc = post.get("created_utc", 0)
            if args.after and created_utc < to_utc_timestamp(args.after):
                continue
            if args.before and created_utc > to_utc_timestamp(args.before):
                continue
                
            posts.append(post)
            
            # Limit check
            if args.limit and len(posts) >= args.limit:
                break
        
        after = data.get("data", {}).get("after")
        page += 1
        
        if not after or (args.limit and len(posts) >= args.limit):
            break
        time.sleep(0.8)
    
    return posts, target

def is_image_url(url, domain):
    url_lower = url.lower()
    # i.redd.it .gif files are static images
    if domain == "i.redd.it" and url_lower.endswith((".jpg", ".jpeg", ".png", ".webp", ".gif")):
        return True
    if domain in ("i.imgur.com", "imgur.com", "m.imgur.com") and any(url_lower.endswith(e) for e in IMAGE_EXTS):
        return True
    return False

def is_gif_url(url, domain):
    # i.redd.it .gif are actually static images, not videos
    if domain == "i.redd.it" and url.lower().endswith(".gif"):
        return False
    if any(x in domain for x in ["gfycat", "redgifs"]):
        return True
    if domain in ("i.imgur.com", "imgur.com", "m.imgur.com"):
        url_lower = url.lower()
        return url_lower.endswith((".gif", ".gifv"))
    return False

def get_reddit_video(post):
    """Extract video URL from Reddit-hosted media (reddit.com/media)."""
    # Check media field
    media = post.get("media", {})
    if media:
        reddit_video = media.get("reddit_video")
        if reddit_video:
            fallback = reddit_video.get("fallback_url")
            if fallback:
                return fallback
    
    # Check secure_media field
    secure_media = post.get("secure_media", {})
    if secure_media:
        reddit_video = secure_media.get("reddit_video")
        if reddit_video:
            fallback = reddit_video.get("fallback_url")
            if fallback:
                return fallback
    
    # Check for crosspost parent
    crosspost = post.get("crosspost_parent_list", [])
    if crosspost:
        return get_reddit_video(crosspost[0])
    
    return None

def get_gallery_images(post):
    """Extract image URLs from Reddit gallery posts."""
    items = []
    gallery_data = post.get("gallery_data", {})
    media_metadata = post.get("media_metadata", {})
    if not gallery_data or not media_metadata:
        return items
    for i, item in enumerate(gallery_data.get("items", []), 1):
        media_id = item.get("media_id")
        if not media_id or media_id not in media_metadata:
            continue
        meta = media_metadata[media_id]
        if meta.get("status") != "valid":
            continue
        mime = meta.get("m", "image/jpeg")
        ext_map = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}
        ext = ext_map.get(mime, ".jpg")
        src = meta.get("s", {})
        url = src.get("u") or src.get("gif")
        if url:
            url = url.replace("&amp;", "&")
            items.append((url, f"_{i}"))
    return items

def download_file(url, out_path):
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    with open(out_path, "wb") as f:
        f.write(r.content)

def download_image(post_id, url, suffix, out_path, skip_existing):
    if skip_existing and os.path.exists(out_path):
        return f"skip  {os.path.basename(out_path)}"
    try:
        download_file(url, out_path)
        return f"✓     {os.path.basename(out_path)}"
    except Exception as e:
        return f"✗     {os.path.basename(out_path)} — {str(e)[:50]}"

def download_video(post_id, url, out_path, skip_existing):
    for ext in ("mp4", "gif", "webm"):
        if os.path.exists(out_path.replace(".%(ext)s", f".{ext}")):
            return f"skip  {os.path.basename(out_path)}"
    if skip_existing and os.path.exists(out_path.replace(".%(ext)s", ".mp4")):
        return f"skip  {os.path.basename(out_path.replace('.%(ext)s', '.mp4'))}"
    result = subprocess.run(
        [YTDLP, url, "-o", out_path, "--no-part", "-q",
         "--merge-output-format", "mp4", "--socket-timeout", "30"],
        capture_output=True, timeout=120
    )
    if result.returncode == 0:
        return f"✓     {os.path.basename(out_path)}"
    else:
        err = result.stderr.decode(errors="ignore").strip().splitlines()
        short_err = err[-1] if err else "unknown"
        return f"✗     {os.path.basename(out_path)} — {short_err[:50]}"

def main():
    parser = argparse.ArgumentParser(description="Archive Reddit posts")
    parser.add_argument("-u", "--user", help="Reddit username")
    parser.add_argument("-s", "--subreddit", help="Subreddit name")
    parser.add_argument("-o", "--output", help="Output directory", 
                        default=None)
    parser.add_argument("--sort", choices=["hot", "new", "rising", "top", "controversial"],
                        default="hot", help="Sort order (subreddits only)")
    parser.add_argument("--time", choices=["hour", "day", "week", "month", "year", "all"],
                        help="Time filter for top/controversial (hour, day, week, month, year, all)")
    parser.add_argument("--after", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--before", help="End date (YYYY-MM-DD)")
    parser.add_argument("--images/--no-images", default=True, dest="images",
                        help="Download images (default: true)")
    parser.add_argument("--gifs/--no-gifs", default=True, dest="gifs",
                        help="Download GIFs/videos (default: true)")
    parser.add_argument("--skip-existing", action="store_true", default=True,
                        help="Skip already-downloaded files")
    parser.add_argument("--workers", type=int, default=4,
                        help="Parallel workers")
    parser.add_argument("--limit", type=int, default=0,
                        help="Max posts to fetch (0 = unlimited)")
    args = parser.parse_args()
    
    if not args.user and not args.subreddit:
        print("Error: specify either --user or --subreddit")
        sys.exit(1)
    if args.user and args.subreddit:
        print("Error: specify either --user OR --subreddit, not both")
        sys.exit(1)
    
    target = args.user or args.subreddit
    outdir = args.output or os.path.expanduser(f"~/temp/.reddit_{target}")
    os.makedirs(outdir, exist_ok=True)
    
    print(f"Fetching posts from {'u/' + args.user if args.user else 'r/' + args.subreddit}...")
    posts, target = get_posts(args)
    print(f"Total posts (filtered): {len(posts)}")
    
    image_tasks = []
    gif_tasks = []
    
    for p in posts:
        domain = p.get("domain", "")
        url = p.get("url", "")
        pid = p.get("id", "unknown")
        
        # Gallery posts
        if args.images and p.get("is_gallery"):
            for img_url, suffix in get_gallery_images(p):
                ext = os.path.splitext(img_url.lower().split("?")[0])[1] or ".jpg"
                out_path = os.path.join(outdir, f"{target}_{pid}{suffix}{ext}")
                image_tasks.append((pid, img_url, suffix, out_path))
        
        # Single image
        elif args.images and is_image_url(url, domain):
            ext = os.path.splitext(url.lower().split("?")[0])[1] or ".jpg"
            out_path = os.path.join(outdir, f"{target}_{pid}{ext}")
            image_tasks.append((pid, url, "", out_path))
        
        # GIFs/videos (external hosts)
        if args.gifs and is_gif_url(url, domain):
            out_tmpl = os.path.join(outdir, f"{target}_{pid}.%(ext)s")
            gif_tasks.append((pid, url, out_tmpl))
        
        # Reddit-hosted videos (reddit.com/media)
        if args.gifs and domain == "reddit.com":
            video_url = get_reddit_video(p)
            if video_url:
                out_tmpl = os.path.join(outdir, f"{target}_{pid}.mp4")
                gif_tasks.append((pid, video_url, out_tmpl))
    
    print(f"Image tasks: {len(image_tasks)}, GIF/video tasks: {len(gif_tasks)}\n")
    
    ok = fail = skip = 0
    
    # Download images
    if image_tasks:
        print("=== Downloading images ===")
        with ThreadPoolExecutor(max_workers=args.workers) as ex:
            futures = {ex.submit(download_image, pid, url, sfx, out, args.skip_existing): (pid, url) 
                       for pid, url, sfx, out in image_tasks}
            for f in as_completed(futures):
                msg = f.result()
                print(msg)
                if msg.startswith("✓"): ok += 1
                elif msg.startswith("✗"): fail += 1
                else: skip += 1
    
    # Download GIFs/videos
    if gif_tasks:
        print("\n=== Downloading GIFs/videos ===")
        with ThreadPoolExecutor(max_workers=args.workers) as ex:
            futures = {ex.submit(download_video, pid, url, out, args.skip_existing): (pid, url) 
                       for pid, url, out in gif_tasks}
            for f in as_completed(futures):
                msg = f.result()
                print(msg)
                if msg.startswith("✓"): ok += 1
                elif msg.startswith("✗"): fail += 1
                else: skip += 1
    
    print(f"\n=== Done: {ok} downloaded, {skip} skipped, {fail} failed ===")
    print(f"Output: {outdir}")

if __name__ == "__main__":
    main()
