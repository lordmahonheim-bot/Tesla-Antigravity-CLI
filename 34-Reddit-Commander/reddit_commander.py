#!/usr/bin/env python3
import os
import sys
import argparse
import logging
import time
from typing import Optional

# Set up local paths so it can import adjacent modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import reddit_db as db
from reddit_client import RedditClient
from reddit_forms import RedditFormsEngine

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("reddit_commander")


def cmd_init_db(args: argparse.Namespace) -> None:
    logger.info("Initializing Reddit Commander SQLite Database...")
    db.init_db()
    print("[✓] Database initialized successfully.")


def cmd_add_watch(args: argparse.Namespace) -> None:
    db.init_db()
    db.update_watchlist(args.subreddit, 0.0, "")
    print(f"[✓] Added r/{args.subreddit} to watchlist.")


def cmd_watch(args: argparse.Namespace) -> None:
    db.init_db()
    watchlist = db.get_watchlist()
    if not watchlist:
        logger.warning("Watchlist is empty. Adding r/python and r/test as default.")
        db.update_watchlist("python", 0.0, "")
        db.update_watchlist("test", 0.0, "")
        watchlist = db.get_watchlist()

    client = RedditClient(mock=args.mock)
    
    digest_content = [
        "---",
        "type: digest",
        "tags: [reddit, watch, curation]",
        f"date: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        "confidence_score: 100%",
        "---",
        "",
        "# Reddit Watch Digest",
        f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')} UTC",
        ""
    ]
    
    new_posts_found = 0
    
    for item in watchlist:
        sub = item["subreddit"]
        after = item["after_cursor"] or ""
        logger.info(f"Scanning r/{sub} (after cursor: '{after}')")
        
        try:
            posts = client.get_subreddit_posts(sub, limit=10)
            
            if not posts:
                logger.info(f"No posts found in r/{sub}.")
                continue
                
            sub_content = [f"## Subreddit: r/{sub}", ""]
            sub_posts_count = 0
            
            for p in posts:
                content_hash = db.compute_content_hash(p["permalink"])
                if db.check_duplicate_content(content_hash):
                    continue
                
                sub_content.append(f"### [{p['title']}]({p['url']})")
                sub_content.append(f"- **Author**: u/{p['author']}")
                sub_content.append(f"- **ID**: {p['id']}")
                sub_content.append(f"- **Permalink**: [{p['permalink']}](https://reddit.com{p['permalink']})")
                if p["body"]:
                    body_snippet = p["body"][:300] + "..." if len(p["body"]) > 300 else p["body"]
                    sub_content.append(f"\n> {body_snippet}\n")
                sub_content.append("---")
                
                db.add_ledger_entry(
                    action="watch_scan",
                    subreddit=sub,
                    target_id=p["id"],
                    content_hash=content_hash,
                    status="SUCCESS",
                    reddit_url=f"https://reddit.com{p['permalink']}",
                    approval_ref="automated_watcher"
                )
                sub_posts_count += 1
                new_posts_found += 1
                
            if sub_posts_count > 0:
                digest_content.extend(sub_content)
                db.update_watchlist(sub, time.time(), posts[0]["id"])
                
        except Exception as e:
            logger.error(f"Error scanning r/{sub}: {e}")
            
    if new_posts_found > 0:
        workspace_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        inbox_dir = os.path.join(workspace_dir, "Avalon", "00-Inbox", "reddit_digests")
        os.makedirs(inbox_dir, exist_ok=True)
        
        digest_filename = f"reddit_digest_{int(time.time())}.md"
        digest_filepath = os.path.join(inbox_dir, digest_filename)
        
        with open(digest_filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(digest_content))
            
        print(f"\n[✓] Watch complete. Created digest file: {digest_filepath}")
        print("[*] Recommending running indexing via: python3 indexer_hybrid.py")
    else:
        print("\n[✓] Watch complete. No new posts found since last scan.")


def cmd_research(args: argparse.Namespace) -> None:
    client = RedditClient(mock=args.mock)
    logger.info(f"Researching r/{args.subreddit} (limit {args.limit})...")
    try:
        posts = client.get_subreddit_posts(args.subreddit, limit=args.limit)
        print(f"\n--- Submissions in r/{args.subreddit} ---")
        for idx, p in enumerate(posts, 1):
            print(f"{idx}. [{p['id']}] {p['title']}")
            print(f"   Author: u/{p['author']}")
            print(f"   Link: https://reddit.com{p['permalink']}")
            if p["body"]:
                print(f"   Body snippet: {p['body'][:100]}...")
            print("-" * 40)
    except Exception as e:
        logger.error(f"Research failed: {e}")
        sys.exit(1)


def cmd_publish(args: argparse.Namespace) -> None:
    db.init_db()
    content_hash = db.compute_content_hash(args.body)
    
    if db.check_duplicate_content(content_hash):
        print(f"[!] Error: Semantically identical post already exists in ledger. Action blocked.")
        sys.exit(1)
        
    client = RedditClient(mock=args.mock)
    
    print("\n--- PENDING PUBLICATION ---")
    print(f"Subreddit: r/{args.subreddit}")
    print(f"Title: {args.title}")
    print(f"Body: {args.body[:200]}...")
    print(f"Safe Mode Status: {client.safe_mode}")
    print("-" * 30)
    
    if not args.yes:
        confirm = input("Confirm publication? [y/N]: ").strip().lower()
        if confirm != "y":
            print("Aborted.")
            sys.exit(0)

    try:
        result = client.create_post(args.subreddit, args.title, args.body)
        
        db.add_ledger_entry(
            action="post",
            subreddit=args.subreddit,
            target_id=result["id"],
            content_hash=content_hash,
            status=result["status"],
            reddit_url=f"https://reddit.com{result['permalink']}" if "permalink" in result else "",
            approval_ref=args.approval or "manual_operator"
        )
        
        print(f"[✓] Publication executed. Result status: {result['status']}")
        if "permalink" in result:
            print(f"    URL: https://reddit.com{result['permalink']}")
            
    except Exception as e:
        logger.error(f"Publication failed: {e}")
        sys.exit(1)


def cmd_engage(args: argparse.Namespace) -> None:
    db.init_db()
    content_hash = db.compute_content_hash(args.body)
    
    if db.check_duplicate_content(content_hash):
        print(f"[!] Error: Semantically identical comment already exists in ledger. Action blocked.")
        sys.exit(1)
        
    client = RedditClient(mock=args.mock)
    
    print("\n--- PENDING COMMENT REPLY ---")
    print(f"Parent ID: {args.parent}")
    print(f"Body: {args.body[:200]}...")
    print(f"Safe Mode Status: {client.safe_mode}")
    print("-" * 30)
    
    if not args.yes:
        confirm = input("Confirm reply? [y/N]: ").strip().lower()
        if confirm != "y":
            print("Aborted.")
            sys.exit(0)

    try:
        result = client.create_comment(args.parent, args.body)
        
        db.add_ledger_entry(
            action="comment",
            subreddit="",
            target_id=result["id"],
            content_hash=content_hash,
            status=result["status"],
            reddit_url=f"https://reddit.com{result['permalink']}" if "permalink" in result else "",
            approval_ref=args.approval or "manual_operator"
        )
        print(f"[✓] Reply executed. Result status: {result['status']}")
    except Exception as e:
        logger.error(f"Reply failed: {e}")
        sys.exit(1)


def cmd_edit(args: argparse.Namespace) -> None:
    db.init_db()
    client = RedditClient(mock=args.mock)
    
    print("\n--- PENDING EDIT ---")
    print(f"Item ID: {args.id}")
    print(f"New Body: {args.body[:200]}...")
    print("-" * 30)
    
    if not args.yes:
        confirm = input("Confirm edit? [y/N]: ").strip().lower()
        if confirm != "y":
            print("Aborted.")
            sys.exit(0)

    try:
        result = client.edit_content(args.id, args.body)
        print(f"[✓] Edit executed. Result status: {result['status']}")
    except Exception as e:
        logger.error(f"Edit failed: {e}")
        sys.exit(1)


def cmd_form(args: argparse.Namespace) -> None:
    engine = RedditFormsEngine()
    try:
        if args.post:
            if not args.subreddit or not args.title or not args.body:
                print("[!] Error: --subreddit, --title, and --body are required for autofill post form.")
                sys.exit(1)
            print(f"Launching Playwright Form Assistant for post on r/{args.subreddit}")
            engine.autofill_post(args.subreddit, args.title, args.body)
        elif args.comment:
            if not args.url or not args.body:
                print("[!] Error: --url and --body are required for autofill comment form.")
                sys.exit(1)
            print(f"Launching Playwright Form Assistant for comment on {args.url}")
            engine.autofill_comment(args.url, args.body)
        else:
            print("[!] Error: Specify either --post or --comment for the form assistant.")
            sys.exit(1)
    finally:
        engine.close()


def cmd_audit(args: argparse.Namespace) -> None:
    db.init_db()
    entries = db.get_ledger(limit=args.limit)
    print(f"\n--- Ledger Audit (Last {args.limit} actions) ---")
    for entry in entries:
        print(f"[{entry['timestamp']}] Action: {entry['action']}")
        print(f"   Subreddit: r/{entry['subreddit']} | ID: {entry['target_id']}")
        print(f"   Status: {entry['status']} | Approval: {entry['approval_ref']}")
        print(f"   URL: {entry['reddit_url']}")
        print(f"   Content Hash: {entry['content_hash']}")
        print("-" * 50)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Tesla Reddit Commander CLI - Official API PRAW / Playwright Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument("--mock", action="store_true", help="Run in mock mode (bypasses actual Reddit calls)")
    subparsers = parser.add_subparsers(dest="command", required=True, help="Subcommand to run")
    
    subparsers.add_parser("init-db", help="Initialize the local SQLite database")
    
    parser_add_watch = subparsers.add_parser("add-watch", help="Add subreddit to the watchlist")
    parser_add_watch.add_argument("subreddit", type=str, help="Subreddit name to add")
    
    subparsers.add_parser("watch", help="Incremental check of watched subreddits and digest creation")
    
    parser_research = subparsers.add_parser("research", help="Search/read posts from a subreddit")
    parser_research.add_argument("subreddit", type=str, help="Subreddit name")
    parser_research.add_argument("--limit", type=int, default=10, help="Maximum posts to fetch")
    
    parser_publish = subparsers.add_parser("publish", help="Publish a post via official API")
    parser_publish.add_argument("subreddit", type=str, help="Subreddit name")
    parser_publish.add_argument("title", type=str, help="Post title")
    parser_publish.add_argument("body", type=str, help="Post body text")
    parser_publish.add_argument("-y", "--yes", action="store_true", help="Confirm publication without prompt")
    parser_publish.add_argument("--approval", type=str, help="Approval reference code")
    
    parser_engage = subparsers.add_parser("engage", help="Comment reply to a post or comment")
    parser_engage.add_argument("parent", type=str, help="Parent fullname (e.g. t3_xyz123 or t1_abc456)")
    parser_engage.add_argument("body", type=str, help="Comment body text")
    parser_engage.add_argument("-y", "--yes", action="store_true", help="Confirm reply without prompt")
    parser_engage.add_argument("--approval", type=str, help="Approval reference code")
    
    parser_edit = subparsers.add_parser("edit", help="Edit a submission or comment")
    parser_edit.add_argument("id", type=str, help="Item fullname (e.g. t3_xyz123 or t1_abc456)")
    parser_edit.add_argument("body", type=str, help="New body text")
    parser_edit.add_argument("-y", "--yes", action="store_true", help="Confirm edit without prompt")
    
    parser_form = subparsers.add_parser("form", help="Assist form input via headed Playwright browser")
    parser_form.add_argument("--post", action="store_true", help="Fill post form")
    parser_form.add_argument("--comment", action="store_true", help="Fill comment form")
    parser_form.add_argument("--subreddit", type=str, help="Subreddit name for post")
    parser_form.add_argument("--title", type=str, help="Post title")
    parser_form.add_argument("--url", type=str, help="Post URL for comment")
    parser_form.add_argument("--body", type=str, help="Body content")
    
    parser_audit = subparsers.add_parser("audit", help="Audit the immutable database ledger")
    parser_audit.add_argument("--limit", type=int, default=20, help="Maximum entries to display")

    args = parser.parse_args()

    if args.command == "init-db":
        cmd_init_db(args)
    elif args.command == "add-watch":
        cmd_add_watch(args)
    elif args.command == "watch":
        cmd_watch(args)
    elif args.command == "research":
        cmd_research(args)
    elif args.command == "publish":
        cmd_publish(args)
    elif args.command == "engage":
        cmd_engage(args)
    elif args.command == "edit":
        cmd_edit(args)
    elif args.command == "form":
        cmd_form(args)
    elif args.command == "audit":
        cmd_audit(args)


if __name__ == "__main__":
    main()
