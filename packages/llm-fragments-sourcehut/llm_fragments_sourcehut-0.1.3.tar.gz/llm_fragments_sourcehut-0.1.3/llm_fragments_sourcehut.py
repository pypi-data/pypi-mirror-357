from typing import List, Tuple
import httpx
import llm
import os
import pathlib
import re
import subprocess
import tempfile
from urllib.parse import urlparse


@llm.hookimpl
def register_fragment_loaders(register):
    register("srht", srht_loader)
    register("todo", srht_todo_loader)


def srht_loader(argument: str) -> List[llm.Fragment]:
    """
    Load files from a SourceHut repository as fragments

    Argument is a SourceHut repository URL or ~user/repo
    """
    # Normalize the repository argument
    if argument.startswith("~"):
        repo_url = f"https://git.sr.ht/{argument}"
    elif not argument.startswith(("http://", "https://")):
        # Fallback for user/repo, though ~user/repo is standard
        repo_url = f"https://git.sr.ht/~{argument}"
    else:
        repo_url = argument

    # Create a temporary directory to clone the repository
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # Clone the repository
            subprocess.run(
                ["git", "clone", "--depth=1", repo_url, temp_dir],
                check=True,
                capture_output=True,
                text=True,
            )

            # Process the cloned repository
            repo_path = pathlib.Path(temp_dir)
            fragments = []

            # Walk through all files in the repository, excluding .git directory
            for root, dirs, files in os.walk(repo_path):
                # Remove .git from dirs to prevent descending into it
                if ".git" in dirs:
                    dirs.remove(".git")

                # Process files
                for file in files:
                    file_path = pathlib.Path(root) / file
                    if file_path.is_file():
                        try:
                            # Try to read the file as UTF-8
                            content = file_path.read_text(encoding="utf-8")

                            # Create a relative path for the fragment identifier
                            relative_path = file_path.relative_to(repo_path)

                            # Add the file as a fragment
                            fragments.append(
                                llm.Fragment(
                                    content, f"{argument}/{relative_path}"
                                )
                            )
                        except UnicodeDecodeError:
                            # Skip files that can't be decoded as UTF-8
                            continue

            return fragments
        except subprocess.CalledProcessError as e:
            # Handle Git errors
            raise ValueError(
                f"Failed to clone repository {repo_url}: {e.stderr}"
            )
        except Exception as e:
            # Handle other errors
            raise ValueError(
                f"Error processing repository {repo_url}: {str(e)}"
            )


def srht_todo_loader(argument: str) -> llm.Fragment:
    """
    Fetch SourceHut todo and comments as Markdown

    Argument is either "~owner/repo/NUMBER", "instance.com/~owner/repo/NUMBER", or URL to a todo
    """
    try:
        instance, owner, repo, number = _parse_srht_todo_argument(argument)
    except ValueError as ex:
        raise ValueError(
            "Fragment must be todo:~owner/repo/NUMBER, todo:instance.com/~owner/repo/NUMBER, or a full "
            "SourceHut todo URL – received {!r}".format(argument)
        ) from ex

    client = _srht_client()
    api_url = f"{instance}/query"

    query = """
    query ticketByUser($username: String!, $tracker: String!, $id: Int!) {
        user(username: $username) {
            tracker(name: $tracker) {
                ticket(id: $id) {
                    subject
                    body
                    submitter {
                        canonicalName
                    }
                    events {
                        results {
                            changes {
                                __typename
                                ... on Comment {
                                    author {
                                        canonicalName
                                    }
                                    text
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    """
    variables = {"username": owner.lstrip("~"), "tracker": repo, "id": number}

    response = client.post(
        api_url, json={"query": query, "variables": variables}
    )
    _raise_for_status(response, api_url)

    data = response.json()
    if "errors" in data:
        raise ValueError(f"SourceHut API error: {data['errors'][0]['message']}")

    try:
        ticket = data["data"]["user"]["tracker"]["ticket"]
        if not ticket:
            raise ValueError(f"Todo #{number} not found in {owner}/{repo}")
    except (KeyError, TypeError, IndexError):
        raise ValueError(f"Todo or tracker not found: {argument}")

    comments = []
    if ticket.get("events") and ticket["events"].get("results"):
        raw_comments = []
        for event in ticket["events"]["results"]:
            for change in event.get("changes", []):
                if change.get("__typename") == "Comment":
                    raw_comments.append(
                        {
                            "user": {
                                "login": change["author"]["canonicalName"]
                            },
                            "body": change["text"],
                        }
                    )
        comments = list(reversed(raw_comments))

    todo_data = {
        "title": ticket["subject"],
        "user": {"login": ticket["submitter"]["canonicalName"]},
        "body": ticket.get("body") or "",
    }
    markdown = _to_srht_markdown(todo_data, comments)

    source_url = f"{instance}/{owner}/{repo}/{number}"
    return llm.Fragment(markdown, source=source_url)


def _parse_srht_todo_argument(arg: str) -> Tuple[str, str, str, int]:
    """
    Returns (instance, owner, repo, number) or raises ValueError
    instance is the full base URL (e.g., "https://todo.sr.ht")
    owner starts with '~'
    """
    # Form 1: full URL
    if arg.startswith("http://") or arg.startswith("https://"):
        parsed = urlparse(arg)
        parts = parsed.path.strip("/").split("/")
        if len(parts) == 3 and parts[0].startswith("~"):
            owner, repo, number = parts
            instance = f"{parsed.scheme}://{parsed.netloc}"
            return instance, owner, repo, int(number)

    # Form 2: instance.com/~owner/repo/number (custom instance)
    if "/" in arg and not arg.startswith("~"):
        # Split on first occurrence of /~
        if "/~" in arg:
            instance_part, path_part = arg.split("/~", 1)
            parts = path_part.split("/")
            if len(parts) == 3:
                owner_without_tilde, repo, number = parts
                owner = "~" + owner_without_tilde
                # Support scheme-less input, defaulting to HTTPS
                if instance_part.startswith(("http://", "https://")):
                    instance = instance_part
                else:
                    instance = f"https://{instance_part}"
                return instance, owner, repo, int(number)

    # Form 3: ~owner/repo/number (default instance)
    m = re.match(r"(~[^/]+)/([^/]+)/(\d+)$", arg)
    if m:
        owner, repo, number = m.groups()
        instance = "https://todo.sr.ht"
        return instance, owner, repo, int(number)

    raise ValueError(
        "Argument should be ~owner/repo/NUMBER, instance.com/~owner/repo/NUMBER, or a full SourceHut todo URL"
    )


def _srht_client() -> httpx.Client:
    headers = {"Accept": "application/json"}
    token = os.getenv("SRHT_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return httpx.Client(headers=headers, timeout=30.0, follow_redirects=True)


def _raise_for_status(resp: httpx.Response, url: str) -> None:
    try:
        resp.raise_for_status()
    except httpx.HTTPStatusError as ex:
        raise ValueError(
            f"API request failed [{resp.status_code}] for {url}"
        ) from ex


def _to_srht_markdown(todo: dict, comments: List[dict]) -> str:
    md: List[str] = []
    md.append(f"# {todo['title']}\n")
    md.append(f"*Posted by {todo['user']['login']}*\n")
    if todo.get("body"):
        md.append(todo["body"] + "\n")

    if comments:
        md.append("---\n")
        for c in comments:
            md.append(f"### Comment by {c['user']['login']}\n")
            if c.get("body"):
                md.append(c["body"] + "\n")
            md.append("---\n")

    return "\n".join(md).rstrip() + "\n"
