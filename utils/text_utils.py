import unicodedata
from difflib import get_close_matches
from typing import Optional
import streamlit as st

from config.settings import DEVELOPERS

def normalize_text(text: Optional[str]) -> Optional[str]:
    if not text:
        return None
    text = text.lower().strip()
    text = unicodedata.normalize('NFKD', text)
    text = ''.join([c for c in text if not unicodedata.combining(c)])
    return text

def match_epic(epic_text: Optional[str]) -> Optional[str]:
    epic_text = normalize_text(epic_text)
    if not epic_text:
        return None
    epic_mapping = {}
    if "config" in st.session_state and st.session_state.config.get("epic_mapping"):
        epic_mapping = st.session_state.config["epic_mapping"]
    if not epic_mapping:
        return None
    epics = list(epic_mapping.keys())
    # Try exact/fuzzy match first
    matches = get_close_matches(epic_text, [normalize_text(e) for e in epics], n=1, cutoff=0.6)
    if matches:
        return epics[[normalize_text(e) for e in epics].index(matches[0])]
    # Try matching with number prefix (e.g., '1 - Chatbot')
    if " - " in epic_text:
        _, epic_name = epic_text.split(" - ", 1)
        epic_name = normalize_text(epic_name)
        matches = get_close_matches(epic_name, [normalize_text(e) for e in epics], n=1, cutoff=0.6)
        if matches:
            return epics[[normalize_text(e) for e in epics].index(matches[0])]
    return None

def match_developer(name: Optional[str]) -> Optional[str]:
    name = normalize_text(name)
    if not name:
        return None
    # Try exact match
    for dev in DEVELOPERS:
        if normalize_text(dev) == name:
            return dev
    # Try first name match
    first_name = name.split()[0]
    for dev in DEVELOPERS:
        if normalize_text(dev.split()[0]) == first_name:
            return dev
    # Fallback to fuzzy match
    matches = get_close_matches(name, [normalize_text(d) for d in DEVELOPERS], n=1, cutoff=0.6)
    if matches:
        return DEVELOPERS[[normalize_text(d) for d in DEVELOPERS].index(matches[0])]
    return None 