import datetime
import os
import re
import unicodedata

from lac.fsjail import JailError, resolve

ENTRY_CAP = 500

TOOLS = [
    {
        "name": "tree",
        "description": "Show the Grimoire skeleton: every topic folder, "
        "name = topic. Use when the user asks to run !tree or to see "
        "the structure.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "load",
        "description": "Load ONE file's FULL text into context, or a "
        "topic path to list its file names and subtopics (names only, "
        "no contents). The user names what to open in any language or "
        "spelling - map it to the real paths from the tree BEFORE "
        "calling. If the user's message names or describes a file, the "
        "next action after the listing MUST be a load call, not a "
        "sentence: list the topic first if you need the real name, "
        "then load that file in the same turn. Ask only when several "
        "files could be "
        "meant, or when the user opened the topic itself and named no "
        "file; then show the listing and let them pick. For narrow "
        "questions prefer search - a whole file is expensive.",
        "input_schema": {
            "type": "object",
            "properties": {
                "args": {
                    "type": "string",
                    "description": "Topic or file path relative to the "
                    "grimoire root, e.g. hobby/topic or "
                    "hobby/topic/notes.md",
                }
            },
            "required": ["args"],
        },
    },
    {
        "name": "delete",
        "description": "Soft-delete: move a file or topic folder into trash/. "
        "Nothing is ever destroyed - it can be recovered from trash by hand. "
        "Use ONLY when the user explicitly asks to delete something. The "
        "user may name the target in any language - map it to the real "
        "folder names from the tree BEFORE calling.",
        "input_schema": {
            "type": "object",
            "properties": {
                "args": {
                    "type": "string",
                    "description": "Path relative to the grimoire root, "
                    "e.g. Work/old_topic",
                }
            },
            "required": ["args"],
        },
    },
    {
        "name": "save",
        "description": "Add to the core memory - the boot file about "
        "the user, their projects and what they have been doing. Each "
        "topic has a section there; a save appends lines and never "
        "touches what is already written, so earlier facts survive. "
        "Only on the user's command, and the write waits for the "
        "user's y/N. Core holds the SURFACE of a topic, never its "
        "contents: what it is and whose it is, decisions taken in the "
        "conversation, what stage the work is at, what is still open, "
        "which file holds what. If a line could be found by loading or "
        "searching the user's own files, it does NOT belong here - no "
        "setting, no characters, no plot, no mechanics, no summary of "
        "a file. Two tests per line: it is absent from every file, and "
        "it still matters in a later session, read on its own months "
        "later without this talk. Gather from the whole conversation, "
        "not just the last turn, in the user's own words where "
        "possible. Never ask in chat whether to save, and never show a "
        "draft first - compose and call; the terminal gate is where "
        "the user says yes or no, and they see the exact text there. "
        "Fit the whole text into " + str(ENTRY_CAP) + " characters. "
        "Read the topic's section "
        "in the core memory first and add only what it does not "
        "already say, in any wording; to correct or tighten what is "
        "there, rewrite the whole section with replace. Several "
        "subjects = one call each, routed by content. No dates, no "
        "quotes, no detail.",
        "input_schema": {
            "type": "object",
            "properties": {
                "args": {
                    "type": "string",
                    "description": "Topic path relative to the grimoire "
                    "root, e.g. hobby/topic",
                },
                "text": {
                    "type": "string",
                    "description": "The facts to carry forward - one "
                    "per line, plain, no headings, no date, nothing "
                    "invented; " + str(ENTRY_CAP) + " characters in "
                    "total at most",
                },
                "replace": {
                    "type": "boolean",
                    "description": "Rewrite the whole section instead "
                    "of adding to it - condensing only, and every fact "
                    "that still holds must survive the rewrite",
                },
            },
            "required": ["args", "text"],
        },
    },
    {
        "name": "unload",
        "description": "Drop loaded file text from this session's "
        "window to free context. No argument clears every loaded file; "
        "a name or path clears only that one. Use when the user asks "
        "to clear or free the memory, or when a topic is finished. The "
        "files on disk are untouched - only the copy in the window "
        "goes.",
        "input_schema": {
            "type": "object",
            "properties": {
                "args": {
                    "type": "string",
                    "description": "Optional file name or path to "
                    "clear; empty clears every loaded file",
                }
            },
        },
    },
    {
        "name": "map_update",
        "description": "Replace or add ONE topic's line in core/map.md - "
        "the keyword route loaded at boot. Call ONLY when the user "
        "explicitly asks to refresh a topic's map line; the write "
        "waits for the user's y/N gate in the terminal. Favor "
        "terms the folder name does not say, include other-language "
        "equivalents; only the topic's lasting CONTENT - never tool "
        "names, engine terms, or props of one scene.",
        "input_schema": {
            "type": "object",
            "properties": {
                "args": {
                    "type": "string",
                    "description": "Topic path relative to the grimoire "
                    "root, e.g. hobby/cooking",
                },
                "text": {
                    "type": "string",
                    "description": "The one-line keyword cloud for the "
                    "topic's map line",
                },
            },
            "required": ["args", "text"],
        },
    },
    {
        "name": "search",
        "description": "Grep the user's files for matching lines. Use "
        "when a question needs facts outside loaded context. MANDATORY: "
        "expand the query into synonyms, jargon, paths, other-language "
        "equivalents - one pattern: term1|term2|term3. Tell the user "
        "which terms you searched.",
        "input_schema": {
            "type": "object",
            "properties": {
                "args": {
                    "type": "string",
                    "description": "Case-insensitive regex pattern, "
                    "terms joined with |, e.g. vlan|network|802.1q",
                },
                "offset": {
                    "type": "integer",
                    "description": "Skip this many matching lines - "
                    "continue a truncated result; the first page is "
                    "offset 0 (the default)",
                },
            },
            "required": ["args"],
        },
    },
]


ENGINE_DIR = "core"


def is_engine_path(path):
    first = path.replace("\\", "/").strip("/").split("/")[0]
    return first.casefold() == ENGINE_DIR


def walk_grimoire(memory_dir):
    """Walk the user's pages: no dot-paths, no engine folder."""
    for root, dirs, files in os.walk(memory_dir):
        rel = os.path.relpath(root, memory_dir)
        dirs[:] = sorted(
            d for d in dirs
            if not d.startswith(".") and not (rel == "." and d == ENGINE_DIR)
        )
        yield root, rel, dirs, files


def cmd_tree(memory_dir):
    lines = []
    for root, rel, dirs, files in walk_grimoire(memory_dir):
        visible = [f for f in files if not f.startswith(".")]
        depth = 0 if rel == "." else rel.count(os.sep) + 1
        if visible:
            note = " (" + str(len(visible)) + " files)"
        else:
            note = " (subtopics)" if dirs else " (empty)"
        lines.append(
            "  " * depth + os.path.basename(root.rstrip(os.sep)) + "/" + note
        )
    return "\n".join(lines)


def name_key(name):
    return re.sub(r"[\s_\-.']+", "", name).casefold()


def same_name(a, b):
    return (
        unicodedata.normalize("NFC", a).casefold()
        == unicodedata.normalize("NFC", b).casefold()
    )


def canon_path(memory_dir, path):
    parts = [p for p in path.replace("\\", "/").split("/") if p and p != "."]
    current = memory_dir
    fixed = []
    for part in parts:
        try:
            entries = os.listdir(current)
        except OSError:
            entries = []
        match = next((e for e in entries if same_name(e, part)), part)
        fixed.append(match)
        current = os.path.join(current, match)
    return "/".join(fixed)


def canon_arg(env, params):
    return canon_path(env["memory"], params.get("args", ""))


# This application's own framing, added to the engine's list of shapes
# that stored text must never be able to wear. The engine polices its
# own; every app polices its own.
EXTRA_FORGERIES = (
    r"#\s*FILE\s*:",
    r"#\s*TOPIC\s*:",
)


def safe_name(env, name):
    """A name from disk, flattened: it cannot forge lines or framing."""
    flat = " ".join(str(name).split())
    if len(flat) > 120:
        flat = flat[:120] + "..."
    return env["scrub"](flat)[0]


def find_topic(memory_dir, path):
    key = name_key(os.path.basename(path.rstrip("/" + os.sep)))
    if not key:
        return []
    hits = []
    for root, _, dirs, _ in walk_grimoire(memory_dir):
        for folder in dirs:
            if name_key(folder) == key:
                full = os.path.join(root, folder)
                hits.append(os.path.relpath(full, memory_dir))
    return hits


def miss_note(env, path):
    hits = find_topic(env["memory"], path)
    if hits:
        return (
            " - did you mean: "
            + ", ".join(safe_name(env, h) for h in hits)
        )
    return (
        " - no folder with a name like it; the tree tool lists the real "
        "names"
    )


def near_miss(env, path):
    """A wrong name inside a real folder: show what the folder holds."""
    parent = os.path.dirname(path.replace("\\", "/").strip("/"))
    if not parent:
        return miss_note(env, path)
    try:
        folder = resolve(env["memory"], parent)
    except JailError:
        return miss_note(env, path)
    if not os.path.isdir(folder):
        return miss_note(env, path)
    names = sorted(n for n in os.listdir(folder) if not n.startswith("."))
    if not names:
        return " - " + safe_name(env, parent) + " is empty"
    return (
        " - " + safe_name(env, parent) + " holds: "
        + ", ".join(safe_name(env, n) for n in names)
        + " - copy one of these names exactly as written, never a "
        "translated or tidied version of it"
    )


LOAD_CAP = 16000
MAP_LINE_CAP = 300
FILE_MARK = "# FILE: "


def one_match(env, path):
    """One obvious file for a partial name - no second round trip."""
    clean = path.replace("\\", "/").strip("/")
    parent, _, fragment = clean.rpartition("/")
    key = name_key(fragment)
    if not key:
        return ""
    try:
        folder = resolve(env["memory"], parent) if parent else env["memory"]
    except JailError:
        return ""
    if not os.path.isdir(folder):
        return ""
    hits = [
        name for name in sorted(os.listdir(folder))
        if not name.startswith(".")
        and os.path.isfile(os.path.join(folder, name))
        and key in name_key(name)
    ]
    if len(hits) != 1:
        return ""
    return parent + "/" + hits[0] if parent else hits[0]


def cmd_load(env, path):
    if not path:
        return "Specify a path. Use !tree to browse."
    if is_engine_path(path):
        return (
            "not a page: " + ENGINE_DIR + "/ is the engine's own boot "
            "memory - already in context, nothing to open"
        )
    try:
        target = resolve(env["memory"], path)
    except JailError as error:
        return str(error)
    if os.path.isfile(target):
        try:
            with open(target, encoding="utf-8") as f:
                text = f.read()
        except UnicodeDecodeError:
            return "not a text file: " + path
        except OSError as error:
            return "load refused: " + str(error)
        if len(text) > LOAD_CAP:
            ask = env.get("confirm")
            if not ask or not ask(
                "load " + path + " - " + str(len(text)) + " chars, over "
                "the " + str(LOAD_CAP) + " cap"
            ):
                return (
                    "not loaded: " + path + " is " + str(len(text))
                    + " chars (cap " + str(LOAD_CAP) + ") - use search "
                    "for specifics"
                )
        env["note"] = (
            "opened " + path + " (" + str(len(text)) + " chars) - the "
            "text is in context but is not an answer: do not retell or "
            "summarise it, and draw on it only when asked, keeping "
            "names, numbers and quotes exactly as they stand"
        )
        return FILE_MARK + safe_name(env, path) + "\n" + env["fence"](text)
    if not os.path.isdir(target):
        guess = one_match(env, path)
        if guess:
            return cmd_load(env, guess)
        return "no such page: " + path + near_miss(env, path)
    files = []
    subs = []
    for name in sorted(os.listdir(target)):
        if name.startswith("."):
            continue
        full = os.path.join(target, name)
        if os.path.isdir(full):
            subs.append(name + "/")
        else:
            files.append(
                "- " + safe_name(env, name) + " ("
                + str(os.path.getsize(full)) + " bytes)"
            )
    if not files and not subs:
        return "empty topic: " + path
    lines = []
    if files:
        lines.append("files:\n" + "\n".join(files))
    if subs:
        lines.append("subtopics: " + ", ".join(subs))
    env["note"] = (
        "names only - no file content is in context yet. Copy each "
        "name exactly as it stands, character for character: never "
        "rename, translate or tidy it, and never name a file that is "
        "not in the listing. If the user already named or described "
        "one of them, load it now instead of asking. Otherwise let "
        "them pick, or search for specifics"
    )
    return (
        "# TOPIC: " + safe_name(env, path) + "\n"
        + env["fence"]("\n".join(lines))
    )


UNLOAD_STUB = (
    "[unloaded - this file's text was dropped from the window; load "
    "it again if it is needed]"
)


def cmd_unload(env, path=""):
    messages = env.get("messages")
    if messages is None:
        return "unload unavailable: the engine did not expose the window"
    wanted = path.strip().casefold()
    dropped = []
    for message in messages:
        content = message.get("content")
        if not isinstance(content, list):
            continue
        for block in content:
            if block.get("type") != "tool_result":
                continue
            body = block.get("content")
            if not isinstance(body, str) or FILE_MARK not in body:
                continue
            name = body.split(FILE_MARK, 1)[1].split(" (", 1)[0].strip()
            if wanted and wanted not in name.casefold():
                continue
            block["content"] = UNLOAD_STUB
            if name not in dropped:
                dropped.append(name)
    if not dropped:
        return "nothing loaded to unload" + (": " + path if path else "")
    env["note"] = (
        "the file text is gone from the window - your own earlier "
        "words about it stay; for exact wording load the file again"
    )
    return "unloaded: " + ", ".join(dropped)


def drop_map_lines(env, topic):
    map_rel = os.path.join("core", "map.md")
    target = resolve(env["memory"], map_rel)
    if not os.path.isfile(target):
        return
    with open(target, encoding="utf-8") as f:
        lines = f.read().splitlines()
    marker = "- **" + topic + "/"
    kept = [line for line in lines if not line.startswith(marker)]
    if len(kept) != len(lines):
        env["write"](map_rel, "\n".join(kept) + "\n")


def cmd_delete(env, path):
    if not path:
        return "Specify a path. Example: !delete Work/old_topic"
    parts = path.strip().strip("/").split("/")
    if any(part.startswith(".") for part in parts) or is_engine_path(path):
        return (
            "delete refused: engine records are not deletable by tool "
            "- only the user's own topics and files can be buried"
        )
    bad_root = root_check(env, path)
    if bad_root:
        return "delete refused: " + bad_root
    if len(parts) < 2:
        return (
            "delete refused: top-level sections are the grimoire "
            "skeleton - only topics inside them can be buried"
        )
    try:
        source = resolve(env["memory"], path)
    except JailError as error:
        return str(error)
    if not os.path.exists(source):
        return "no such page: " + path + miss_note(env, path)
    was_file = os.path.isfile(source)
    stamp = datetime.date.today().isoformat()
    grave_name = os.path.basename(source.rstrip(os.sep)) + "-" + stamp
    try:
        grave = env["trash"](path, grave_name)
    except (JailError, OSError) as error:
        return "delete refused: " + str(error)
    note = ""
    if not was_file:
        try:
            drop_map_lines(env, path.strip().strip("/"))
        except (JailError, OSError) as error:
            note = " (its map lines could not be dropped: " \
                + str(error) + ")"
    return (
        "buried: " + safe_name(env, path) + " -> "
        + safe_name(env, grave) + note
    )


def root_check(env, path):
    root = path.split("/", 1)[0]
    tops = sorted(
        d for d in os.listdir(env["memory"])
        if os.path.isdir(os.path.join(env["memory"], d))
        and not d.startswith(".") and d != ENGINE_DIR
    )
    if root not in tops:
        return (
            "unknown root '" + root + "' - topics live under "
            + ", ".join(tops) + "; resend with a real root"
        )
    return ""


def cmd_map_update(env, path, text):
    if not path or not text:
        return (
            "[map not updated - call map_update with args (topic path) and "
            "text (a one-line keyword cloud for that topic)]"
        )
    topic = path.strip().strip("/")
    bad_root = root_check(env, topic)
    if bad_root:
        return "map refused: " + bad_root
    if not os.path.isdir(os.path.join(env["memory"], topic)):
        return (
            "map refused: no topic folder at " + topic
            + miss_note(env, topic)
        )
    line = "- **" + topic + "/** - " + " ".join(normalize(text).split())
    if len(line) > MAP_LINE_CAP:
        return (
            "map refused: " + str(len(line)) + " chars (cap "
            + str(MAP_LINE_CAP) + ") - resend fewer, denser keywords"
        )
    map_rel = os.path.join("core", "map.md")
    try:
        target = resolve(env["memory"], map_rel)
    except JailError as error:
        return str(error)
    lines = []
    if os.path.isfile(target):
        with open(target, encoding="utf-8") as f:
            lines = f.read().splitlines()
    marker = "- **" + topic + "/**"
    replaced = False
    for index, old in enumerate(lines):
        if old.startswith(marker):
            lines[index] = line
            replaced = True
            break
    if not replaced:
        lines.append(line)
    try:
        env["write"](map_rel, "\n".join(lines) + "\n")
    except (JailError, OSError) as error:
        return "map refused: " + str(error)
    return ("updated map line: " if replaced else "added map line: ") + line


CORE_REL = os.path.join("core", "core.md")
SECTION_CAP = 2500


def plan_save(env, path, text, replace=False):
    """Everything but the write: (problem, whole file, section, note)."""
    topic = path.strip().strip("/")
    bad_root = root_check(env, topic)
    if bad_root:
        return "save refused: " + bad_root, None, None, ""
    if not os.path.isdir(os.path.join(env["memory"], topic)):
        return (
            "save refused: no topic folder at " + topic
            + miss_note(env, topic), None, None, "",
        )
    body = normalize(text).strip()
    entry = [
        "- " + " ".join(one.split())
        for one in body.splitlines()
        if one.strip()
    ]
    if not entry:
        return "save refused: empty text", None, None, ""
    if len(body) > ENTRY_CAP:
        return (
            "save refused: " + str(len(body)) + " chars (cap "
            + str(ENTRY_CAP) + ") - resend shorter: keep the lasting "
            "facts, drop the story. The user has not been asked yet",
            None, None, "",
        )
    try:
        target = resolve(env["memory"], CORE_REL)
    except JailError as error:
        return str(error), None, None, ""
    lines = []
    if os.path.isfile(target):
        with open(target, encoding="utf-8") as f:
            lines = f.read().splitlines()
    heading = "## " + topic
    start = None
    for index, line in enumerate(lines):
        if line.strip() == heading:
            start = index
            break
    if start is None:
        if lines and lines[-1].strip():
            lines.append("")
        lines.extend([heading] + entry)
        return "", lines, entry, "new section"
    end = start + 1
    while end < len(lines) and not lines[end].startswith("## "):
        end += 1
    kept = [one for one in lines[start + 1:end] if one.strip()]
    fresh = entry if replace else [one for one in entry if one not in kept]
    if not fresh:
        return (
            "already in core: " + topic + " - nothing new to add",
            None, None, "",
        )
    block = fresh if replace else kept + fresh
    size = sum(len(one) + 1 for one in block)
    if size > SECTION_CAP:
        return (
            "save refused: " + topic + " would grow to " + str(size)
            + " chars (cap " + str(SECTION_CAP) + ") - the section "
            "needs condensing: call save again with replace true and "
            "the whole section rewritten short, keeping every fact "
            "that still holds", None, None, "",
        )
    lines[start + 1:end] = block + [""]
    note = "section rewritten" if replace else "added to " + topic
    return "", lines, block, note


def cmd_save(env, path, text, replace=False):
    if not path or not text:
        return (
            "[nothing written - call save with args (the topic path) "
            "and text (what is worth carrying to the next session)]"
        )
    problem, lines, section, note = plan_save(env, path, text, replace)
    if problem:
        return problem
    try:
        env["write"](CORE_REL, "\n".join(lines).rstrip() + "\n")
    except (JailError, OSError) as error:
        return "save refused: " + str(error)
    env["note"] = (
        "the section now stands exactly as returned - later saves add "
        "to it, never repeating what it already says. Tell the user "
        "what went in and what you left out; detail and full text "
        "belong in their own files, written by their hand"
    )
    return (
        note + "\n## " + path.strip().strip("/") + "\n" + "\n".join(section)
    )


SEARCH_PAGE = 40
SEARCH_LINE_CAP = 200


def cmd_search(env, pattern, offset=0):
    if not pattern:
        return "Specify a pattern. Example: !search vlan|network"
    try:
        regex = re.compile(pattern, re.IGNORECASE)
    except re.error as error:
        return "search error: bad pattern: " + str(error)
    try:
        offset = max(0, int(offset))
    except (TypeError, ValueError):
        offset = 0
    memory_dir = env["memory"]
    lines = []
    for root, _, _, files in walk_grimoire(memory_dir):
        for name in sorted(files):
            if name.startswith("."):
                continue
            full = os.path.join(root, name)
            try:
                with open(full, encoding="utf-8") as f:
                    for number, line in enumerate(f, 1):
                        if regex.search(line):
                            rel = os.path.relpath(full, memory_dir)
                            text = line.rstrip()
                            if len(text) > SEARCH_LINE_CAP:
                                text = (
                                    text[:SEARCH_LINE_CAP]
                                    + " ...(line cut - load the file "
                                    "for the rest)"
                                )
                            lines.append(
                                rel + ":" + str(number) + ":" + text
                            )
            except (UnicodeDecodeError, OSError):
                continue
    if not lines:
        return "no matches: " + pattern
    total = len(lines)
    page = lines[offset:offset + SEARCH_PAGE]
    if not page:
        return (
            "no matches past offset " + str(offset) + " - only "
            + str(total) + " matching lines in total"
        )
    left = total - offset - len(page)
    if left > 0:
        page = page + [
            "... (" + str(left) + " more lines - search again with "
            "offset " + str(offset + SEARCH_PAGE) + ", or narrow the "
            "pattern)"
        ]
    return env["fence"]("\n".join(page))


FOLD_TASK = (
    "Fold the conversation above into a short digest: decisions, facts, "
    "open threads. Plain lines, no commentary. The digest replaces these "
    "turns in context - keep every fact needed to continue; drop "
    "pleasantries and dead ends."
)
TOOL_STUB = (
    "(trimmed to free context - call the tool again if the content "
    "is needed)"
)

DASH_QUOTES = {
    chr(0x2014): "-",  # em dash
    chr(0x2013): "-",  # en dash
    chr(0x2018): "'",  # curly quotes
    chr(0x2019): "'",
    chr(0x201C): '"',
    chr(0x201D): '"',
}
def normalize(text):
    for wrong, right in DASH_QUOTES.items():
        text = text.replace(wrong, right)
    return text


def on_text(env, text):
    return normalize(text)


ON_TEXT = on_text


def message_weight(message):
    return len(str(message["content"])) // 3


def cut_point(messages, keep):
    index = len(messages)
    total = 0
    for i in range(len(messages) - 1, -1, -1):
        total += message_weight(messages[i])
        if total > keep:
            break
        message = messages[i]
        if message["role"] == "user" and isinstance(message["content"], str):
            index = i
    return index


def flat_transcript(messages):
    lines = []
    for message in messages:
        content = message["content"]
        if isinstance(content, str):
            lines.append(message["role"] + ": " + content)
            continue
        for block in content:
            if block["type"] == "text":
                lines.append(message["role"] + ": " + block["text"])
            elif block["type"] == "tool_use":
                lines.append(
                    "tool call " + block["name"] + ": " + repr(block["input"])
                )
            elif block["type"] == "tool_result":
                lines.append("tool result: " + str(block["content"]))
    return "\n\n".join(lines)


def on_turn(env, messages, window):
    if window - env.get("law_size", 0) <= env["budget"]:
        return
    cut = cut_point(messages, env["budget"] // 2)
    if cut < 4 or cut >= len(messages):
        return
    head = messages[:cut]
    fold_input = flat_transcript(head) + "\n\n" + FOLD_TASK
    try:
        reply = env["main"]([{"role": "user", "content": fold_input}])
    except Exception as error:
        print("[compress failed]", error)
        return
    digest = "".join(
        b["text"] for b in reply["content"] if b["type"] == "text"
    ).strip()
    if not digest:
        print("[compress failed] empty digest - keeping the window")
        return
    tail = messages[cut:]
    for message in tail[:-6]:
        content = message["content"]
        if not isinstance(content, list):
            continue
        for block in content:
            if block.get("type") == "tool_result":
                block["content"] = TOOL_STUB
    messages[:] = [
        {
            "role": "user",
            "content": "[digest of earlier turns, folded to free "
            "context - detail beyond it is gone from this session; "
            "the user's files hold the canon]\n" + digest,
        }
    ] + tail
    print("[compress]", len(head), "messages folded")


ON_TURN = on_turn


def on_boot(env):
    # UNFINISHED: the tree size cap is a separate budget task.
    tasks_path = os.path.join(env["memory"], "core", "tasks.md")
    if os.path.isfile(tasks_path):
        with open(tasks_path, encoding="utf-8") as f:
            tasks = f.read().strip()
        if tasks:
            print()
            print("--- tasks (core/tasks.md) ---")
            print(tasks)
    return (
        "# GRIMOIRE TREE (counted at boot - file counts are real, "
        "contents are not shown; the tree tool re-checks)\n"
        + cmd_tree(env["memory"])
    )


ON_BOOT = on_boot


COMMANDS = {
    "tree": lambda env, p: env["fence"](cmd_tree(env["memory"])),
    "load": lambda env, p: cmd_load(env, canon_arg(env, p)),
    "search": lambda env, p: cmd_search(
        env, p.get("args", ""), p.get("offset", 0)
    ),
    "save": lambda env, p: cmd_save(
        env, canon_arg(env, p), p.get("text", ""), p.get("replace", False)
    ),
    "unload": lambda env, p: cmd_unload(env, p.get("args", "")),
    "delete": lambda env, p: cmd_delete(env, canon_arg(env, p)),
    "map_update": lambda env, p: cmd_map_update(
        env, canon_arg(env, p), p.get("text", "")
    ),
}

VALIDATE = {
    "save": lambda env, p: plan_save(
        env, canon_arg(env, p), p.get("text", ""), p.get("replace", False)
    )[0] if p.get("args") and p.get("text") else "",
}

CONFIRM = {"delete", "map_update", "save"}

WRITABLE = {"core/map.md", "core/core.md"}
