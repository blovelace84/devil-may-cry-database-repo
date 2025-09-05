
import streamlit as st
import pandas as pd
from pathlib import Path
from urllib.parse import urlencode

st.set_page_config(page_title="Devil May Cry Database", page_icon="😈", layout="wide")

DATA_DIR = Path(__file__).parent / "data"

@st.cache_data
def load_data():
    characters = pd.read_csv(DATA_DIR / "characters.csv")
    weapons = pd.read_csv(DATA_DIR / "weapons.csv")
    bosses = pd.read_csv(DATA_DIR / "bosses.csv")
    missions = pd.read_csv(DATA_DIR / "missions.csv")
    return characters, weapons, bosses, missions

def card(img, title, subtitle=None, body=None, footer=None, key=None):
    with st.container(border=True):
        cols = st.columns([1, 2])
        with cols[0]:
            if isinstance(img, str) and img:
                st.image(img, use_container_width=True)
        with cols[1]:
            st.subheader(title)
            if subtitle:
                st.caption(subtitle)
            if body:
                st.write(body)
            if footer:
                st.markdown(footer)

def search_and_filter(df, text_cols, extra_filters=None):
    search = st.text_input("Search", placeholder="Type to filter by name, game, etc.")
    if search:
        s = search.lower()
        mask = False
        for c in text_cols:
            mask = mask | df[c].astype(str).str.lower().str.contains(s, na=False)
        df = df[mask]
    if extra_filters:
        for label, col in extra_filters:
            values = sorted([v for v in df[col].dropna().astype(str).unique() if v])
            sel = st.multiselect(label, values)
            if sel:
                df = df[df[col].astype(str).isin(sel)]
    return df

def list_page():
    st.title("😈 Devil May Cry Database")
    st.write("Browse characters, weapons, bosses, and missions. Use the tabs below.")
    characters, weapons, bosses, missions = load_data()

    t1, t2, t3, t4 = st.tabs(["Characters", "Weapons", "Bosses", "Missions"])

    with t1:
        cdf = search_and_filter(characters, ["name","game","affiliation","style"],
                                [("Game", "game"), ("Affiliation","affiliation")])
        for _, row in cdf.iterrows():
            params = urlencode({"type":"character","id":row["id"]})
            link = f"?{params}"
            card(row.get("image_url",""),
                 row["name"],
                 subtitle=f'{row.get("affiliation","")} • {row.get("game","")}',
                 body=row.get("description",""),
                 footer=f"[Open details]({link})")

    with t2:
        wdf = search_and_filter(weapons, ["name","type","wielder","game","style"],
                                [("Game", "game"), ("Type","type"), ("Wielder","wielder")])
        for _, row in wdf.iterrows():
            params = urlencode({"type":"weapon","id":row["id"]})
            link = f"?{params}"
            card(row.get("image_url",""),
                 row["name"],
                 subtitle=f'{row.get("type","")} • {row.get("game","")}',
                 body=row.get("description",""),
                 footer=f"[Open details]({link})")

    with t3:
        bdf = search_and_filter(bosses, ["name","title","game","description"],
                                [("Game","game")])
        for _, row in bdf.iterrows():
            params = urlencode({"type":"boss","id":row["id"]})
            link = f"?{params}"
            card(row.get("image_url",""),
                 f'{row["name"]} — {row.get("title","")}',
                 subtitle=row.get("game",""),
                 body=row.get("description",""),
                 footer=f"[Open details]({link})")

    with t4:
        mdf = search_and_filter(missions, ["game","mission","objective","notes"],
                                [("Game","game")])
        st.dataframe(mdf, use_container_width=True)
        st.download_button("Download filtered missions (CSV)", mdf.to_csv(index=False), "missions_filtered.csv", "text/csv")

def detail_page(item_type: str, item_id: int):
    characters, weapons, bosses, missions = load_data()
    if item_type == "character":
        df = characters
    elif item_type == "weapon":
        df = weapons
    elif item_type == "boss":
        df = bosses
    else:
        st.switch_page("app.py")

    row = df[df["id"]==item_id]
    if row.empty:
        st.error("Item not found.")
        st.page_link("app.py", label="Back to list")
        return
    row = row.iloc[0]

    st.page_link("app.py", label="← Back to list")
    st.title(row.get("name","Details"))
    if "image_url" in row and isinstance(row["image_url"], str) and row["image_url"]:
        st.image(row["image_url"], use_container_width=True)

    meta = {k: v for k, v in row.items() if k not in ("id","name","description","image_url")}
    st.write(row.get("description",""))
    st.divider()
    cols = st.columns(2)
    items = list(meta.items())
    mid = (len(items)+1)//2
    with cols[0]:
        for k, v in items[:mid]:
            st.write(f"**{k.replace('_',' ').title()}**: {v}")
    with cols[1]:
        for k, v in items[mid:]:
            st.write(f"**{k.replace('_',' ').title()}**: {v}")

def main():
    q = st.query_params
    if "type" in q and "id" in q:
        try:
            detail_page(q.get("type"), int(q.get("id")))
        except Exception:
            list_page()
    else:
        list_page()

if __name__ == "__main__":
    main()
