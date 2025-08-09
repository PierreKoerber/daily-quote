#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
daily_quote.py — Affiche une citation quotidienne.
Usage:
  python3 daily_quote.py            # citation du jour (déterministe)
  python3 daily_quote.py --random   # citation aléatoire
  python3 daily_quote.py --add "Texte|Auteur"   # ajoute une citation
  python3 daily_quote.py --list     # liste toutes les citations
Le fichier de base se trouve à ~/.local/share/daily_quote/quotes.json (copié au premier lancement).
"""
import argparse, json, os, sys, datetime, hashlib, random, textwrap

DEFAULT_DB = os.path.expanduser("./quotes.json")
SEED_ENV = "DAILY_QUOTE_SEED"

def ensure_db(source_db):
    os.makedirs(os.path.dirname(DEFAULT_DB), exist_ok=True)
    if not os.path.exists(DEFAULT_DB):
        # Première installation : copie depuis le bundle
        with open(source_db, "r", encoding="utf-8") as fsrc, open(DEFAULT_DB, "w", encoding="utf-8") as fdst:
            fdst.write(fsrc.read())

def load_quotes(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    # normalisation minimale
    cleaned = []
    for q in data:
        if isinstance(q, dict) and "text" in q and "author" in q:
            cleaned.append({"text": q["text"].strip(), "author": q["author"].strip()})
    if not cleaned:
        raise SystemExit("La base de citations est vide ou invalide.")
    return cleaned

def pick_today(quotes):
    # Déterministe par jour et machine (seed facultative via env)
    today = datetime.date.today().isoformat()
    base = today + os.uname().nodename + os.getenv(SEED_ENV, "")
    h = int(hashlib.sha256(base.encode("utf-8")).hexdigest(), 16)
    return quotes[h % len(quotes)]

def pick_random(quotes):
    random.seed()  # non déterministe
    return random.choice(quotes)

def add_quote(path, item):
    txt, author = (part.strip() for part in item.split("|", 1))
    data = load_quotes(path)
    data.append({"text": txt, "author": author or "Anonyme"})
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("✅ Citation ajoutée. Total:", len(data))

def print_quote(q):
    wrapped = textwrap.fill(f"« {q['text']} »", width=88)
    print("🗓️  Citation du jour")
    print(wrapped)
    print(f"— {q['author']}")

def list_quotes(path):
    data = load_quotes(path)
    for i, q in enumerate(data, 1):
        print(f"{i:02d}. {q['text']} — {q['author']}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--random", action="store_true", help="Afficher une citation aléatoire")
    parser.add_argument("--add", metavar="TEXTE|AUTEUR", help="Ajouter une citation")
    parser.add_argument("--list", action="store_true", help="Lister toutes les citations")
    args = parser.parse_args()

    # Assure l'installation locale de la base
    bundled_db = os.path.join(os.path.dirname(__file__), "quotes.json")
    ensure_db(bundled_db)

    if args.add:
        return add_quote(DEFAULT_DB, args.add)
    if args.list:
        return list_quotes(DEFAULT_DB)

    quotes = load_quotes(DEFAULT_DB)
    q = pick_random(quotes) if args.random else pick_today(quotes)
    print_quote(q)

if __name__ == "__main__":
    main()