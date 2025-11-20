# BITTE ALLE FELDBEZEICHNUNGEN & PROJEKTSPEZIFIKA IM SKRIPT NOCH ANPASSEN !!!
#!/usr/bin/env python3
"""
OCR - Quality Control & Correction App
Streamlit-basierte Webanwendung zur Ergebniskontrolle und Korrektur
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import json
from PIL import Image
import os

# === KONFIGURATION === PFADE BITTE ENTSPRECHEND ANPASSEN !
CSV_DIR = "XXXXXX/output_batches/csv"
JSON_DIR = "XXXXXXX/output_batches/json"
MASTER_CSV = "XXXXXXX/results/metadata_vlm_complete_UPDATED.csv"
IMAGE_BASE_DIR = "XXXXXXX/jpeg_output"
LOGO_PATH = "XXXXXXXX/WUNSCH_Logo.png"

# Felder die editierbar sein sollen - BITTE ANPASSEN !
EDITABLE_FIELDS = [
    "Komponist", "Signatur", "Titel", "Textanfang",
    "Verlag", "Material", "Textdichter", "Bearbeiter", "Bemerkungen"
]

# === PAGE CONFIG ===
st.set_page_config(
    page_title="OCR - Qualitätskontrolle",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# === SESSION STATE INITIALISIERUNG ===
if 'card_index' not in st.session_state:
    st.session_state.card_index = 0

# === CUSTOM CSS ===
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stTextInput > div > div > input {
        background-color: #f0f2f6;
    }
    .stTextArea > div > div > textarea {
        background-color: #f0f2f6;
    }
    .card-preview {
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .field-label {
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 0.2rem;
    }
    .stat-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 5px;
        text-align: center;
    }
    .warning-box {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 1rem;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        padding: 1rem;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# === HILFSFUNKTIONEN ===

@st.cache_data
def load_csv_data(csv_path):
    """Lädt CSV-Daten mit Caching."""
    try:
        df = pd.read_csv(csv_path, encoding="utf-8-sig")
        return df
    except Exception as e:
        st.error(f"Fehler beim Laden: {e}")
        return None

def load_image(batch, filename):
    """Lädt Karteikarten-Bild."""
    try:
        # Versuche verschiedene Pfad-Kombinationen
        possible_paths = [
            Path(IMAGE_BASE_DIR) / batch / filename,
            Path(IMAGE_BASE_DIR) / filename,
            Path(IMAGE_BASE_DIR).parent / batch / filename,
        ]
        
        for img_path in possible_paths:
            if img_path.exists():
                return Image.open(img_path)
        
        return None
    except Exception as e:
        st.error(f"Fehler beim Laden des Bildes: {e}")
        return None

def save_corrections(df, csv_path):
    """Speichert korrigierte Daten."""
    try:
        df.to_csv(csv_path, index=False, encoding="utf-8-sig")
        return True
    except Exception as e:
        st.error(f"Fehler beim Speichern: {e}")
        return False

def get_batch_list():
    """Gibt Liste aller verfügbaren Batches zurück."""
    csv_dir = Path(CSV_DIR)
    if csv_dir.exists():
        batches = sorted([f.stem for f in csv_dir.glob("*.csv")])
        return batches
    return []

def calculate_statistics(df):
    """Berechnet Statistiken für ein DataFrame."""
    total = len(df)
    
    stats = {
        "total": total,
        "komponist": (df['Komponist'].fillna('').str.strip() != '').sum(),
        "signatur": (df['Signatur'].fillna('').str.strip() != '').sum(),
        "titel": (df['Titel'].fillna('').str.strip() != '').sum(),
    }
    
    # Vollständigkeit (mindestens 6 Felder gefüllt)
    field_counts = df[EDITABLE_FIELDS].fillna('').apply(
        lambda row: sum(str(val).strip() != '' for val in row), axis=1
    )
    stats["complete"] = (field_counts >= 6).sum()
    stats["sparse"] = (field_counts <= 2).sum()
    
    return stats

# === SIDEBAR ===

with st.sidebar:
    # Logo
    if Path(LOGO_PATH).exists():
        st.image(LOGO_PATH, width=200)
    
    st.title("Projektname")
    st.markdown("### Qualitätskontrolle")
    st.markdown("---")
    
    # Modus-Auswahl
    mode = st.radio(
        "Ansicht:",
        ["📦 Batch-Ansicht", "📊 Gesamt-Übersicht", "🔍 Suche"],
        index=0
    )
    
    st.markdown("---")
    
    # Batch-Auswahl (nur im Batch-Modus)
    if mode == "📦 Batch-Ansicht":
        batches = get_batch_list()
        if batches:
            selected_batch = st.selectbox(
                "Batch wählen:",
                batches,
                index=0
            )
        else:
            st.warning("Keine Batches gefunden!")
            selected_batch = None
    
    st.markdown("---")
    
    # Info
    st.markdown("### ℹ️ Info")
    st.markdown("""
    **Funktionen:**
    - ✏️ Metadaten bearbeiten
    - 💾 Änderungen speichern
    - 📊 Statistiken ansehen
    - 🔍 Karteikarten durchsuchen
    """)
    
    st.markdown("---")
    st.markdown("**TEAMNAME**") # BITTE ANPASSEN
    st.markdown("EINRICHTUNG") # BITTE ANPASSEN

# === HAUPTBEREICH ===

if mode == "📦 Batch-Ansicht" and selected_batch:
    
    # Header
    st.title(f"📦 {selected_batch}")
    
    # Lade Batch-Daten
    csv_path = Path(CSV_DIR) / f"{selected_batch}.csv"
    df = load_csv_data(str(csv_path))
    
    if df is not None and len(df) > 0:
        
        # Statistiken
        stats = calculate_statistics(df)
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.markdown(f"""
            <div class="stat-box">
                <h3>{stats['total']}</h3>
                <p>Gesamt</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            pct = (stats['komponist'] / stats['total'] * 100) if stats['total'] > 0 else 0
            st.markdown(f"""
            <div class="stat-box">
                <h3>{stats['komponist']}</h3>
                <p>Komponist ({pct:.1f}%)</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            pct = (stats['signatur'] / stats['total'] * 100) if stats['total'] > 0 else 0
            st.markdown(f"""
            <div class="stat-box">
                <h3>{stats['signatur']}</h3>
                <p>Signatur ({pct:.1f}%)</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            pct = (stats['titel'] / stats['total'] * 100) if stats['total'] > 0 else 0
            st.markdown(f"""
            <div class="stat-box">
                <h3>{stats['titel']}</h3>
                <p>Titel ({pct:.1f}%)</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col5:
            pct = (stats['sparse'] / stats['total'] * 100) if stats['total'] > 0 else 0
            st.markdown(f"""
            <div class="stat-box" style="background-color: #fff3cd;">
                <h3>{stats['sparse']}</h3>
                <p>Spärlich ({pct:.1f}%)</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Filter-Optionen
        col_filter1, col_filter2 = st.columns(2)
        
        with col_filter1:
            filter_option = st.selectbox(
                "Filter:",
                ["Alle Karten", "Problematische Karten", "Ohne Komponist", "Ohne Signatur"]
            )
        
        with col_filter2:
            sort_option = st.selectbox(
                "Sortierung:",
                ["Nach Dateiname", "Nach Komponist", "Nach Signatur"]
            )
        
        # Filtere DataFrame
        filtered_df = df.copy()
        
        if filter_option == "Problematische Karten":
            field_counts = filtered_df[EDITABLE_FIELDS].fillna('').apply(
                lambda row: sum(str(val).strip() != '' for val in row), axis=1
            )
            filtered_df = filtered_df[field_counts <= 2]
        elif filter_option == "Ohne Komponist":
            filtered_df = filtered_df[filtered_df['Komponist'].fillna('').str.strip() == '']
        elif filter_option == "Ohne Signatur":
            filtered_df = filtered_df[filtered_df['Signatur'].fillna('').str.strip() == '']
        
        # Sortiere
        if sort_option == "Nach Komponist":
            filtered_df = filtered_df.sort_values('Komponist')
        elif sort_option == "Nach Signatur":
            filtered_df = filtered_df.sort_values('Signatur')
        else:
            filtered_df = filtered_df.sort_values('Datei')
        
        filtered_df = filtered_df.reset_index(drop=True)
        
        st.markdown(f"**{len(filtered_df)} Karten** (gefiltert)")
        
        # Karteikarten-Navigation
        if len(filtered_df) > 0:
            
            # === FIX: Session State für card_index ===
            # Stelle sicher, dass card_index im gültigen Bereich liegt
            if st.session_state.card_index >= len(filtered_df):
                st.session_state.card_index = len(filtered_df) - 1
            
            col_nav1, col_nav2, col_nav3 = st.columns([1, 3, 1])
            
            with col_nav2:
                # === FIX: Slider an Session State binden ===
                card_index = st.slider(
                    "Karteikarte:",
                    0,
                    len(filtered_df) - 1,
                    value=st.session_state.card_index,  # Session State als value verwenden
                    format="Karte %d"
                )
                # Session State aktualisieren
                st.session_state.card_index = card_index
            
            st.markdown("---")
            
            # Aktuelle Karte
            current_row = filtered_df.iloc[card_index]
            original_index = df[df['Datei'] == current_row['Datei']].index[0]
            
            # Layout: Bild links, Metadaten rechts
            col_img, col_meta = st.columns([1, 1])
            
            with col_img:
                st.markdown("### 🖼️ Karteikarte")
                
                # Lade und zeige Bild
                img = load_image(selected_batch, current_row['Datei'])
                
                if img is not None:
                    st.image(img, use_container_width=True)
                else:
                    st.warning(f"Bild nicht gefunden: {current_row['Datei']}")
                    st.info(f"Erwarteter Pfad: {IMAGE_BASE_DIR}/{selected_batch}/{current_row['Datei']}")
                
                # Dateiinfo
                st.markdown(f"**Datei:** `{current_row['Datei']}`")
                st.markdown(f"**Batch:** `{selected_batch}`")
            
            with col_meta:
                st.markdown("### ✏️ Metadaten")
                
                # Bearbeitbare Felder
                edited_data = {}
                
                for field in EDITABLE_FIELDS:
                    current_value = str(current_row.get(field, '')) if pd.notna(current_row.get(field)) else ''
                    
                    # Farbmarkierung für leere Felder
                    if current_value.strip() == '':
                        label = f"⚠️ {field}"
                    else:
                        label = field
                    
                    # Textarea für längere Felder
                    if field in ['Textanfang', 'Bemerkungen']:
                        edited_data[field] = st.text_area(
                            label,
                            value=current_value,
                            height=80,
                            key=f"{field}_{card_index}"
                        )
                    else:
                        edited_data[field] = st.text_input(
                            label,
                            value=current_value,
                            key=f"{field}_{card_index}"
                        )
                
                st.markdown("---")
                
                # Speichern-Button
                col_save1, col_save2, col_save3 = st.columns([1, 1, 1])
                
                with col_save2:
                    if st.button("💾 Änderungen speichern", use_container_width=True):
                        # Update DataFrame
                        for field, value in edited_data.items():
                            df.at[original_index, field] = value
                        
                        # Speichere CSV
                        if save_corrections(df, csv_path):
                            st.success("✅ Änderungen gespeichert!")
                            # Cache leeren damit Änderungen sichtbar werden
                            st.cache_data.clear()
                            st.rerun()
                        else:
                            st.error("❌ Fehler beim Speichern!")
                
                st.markdown("---")
                
                # === FIX: Navigation Buttons mit Session State Update ===
                col_prev, col_next = st.columns(2)
                
                with col_prev:
                    if card_index > 0:
                        if st.button("⬅️ Vorherige", use_container_width=True, key="btn_prev"):
                            st.session_state.card_index = max(0, card_index - 1)
                            st.rerun()
                
                with col_next:
                    if card_index < len(filtered_df) - 1:
                        if st.button("Nächste ➡️", use_container_width=True, key="btn_next"):
                            st.session_state.card_index = min(len(filtered_df) - 1, card_index + 1)
                            st.rerun()
        
        else:
            st.warning("Keine Karten entsprechen dem Filter.")

elif mode == "📊 Gesamt-Übersicht":
    
    st.title("📊 Gesamt-Übersicht")
    
    # Lade Master-CSV
    if Path(MASTER_CSV).exists():
        df = load_csv_data(MASTER_CSV)
        
        if df is not None:
            # Gesamt-Statistiken
            stats = calculate_statistics(df)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"""
                <div class="stat-box">
                    <h2>{stats['total']:,}</h2>
                    <p>Gesamt-Karteikarten</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                pct = (stats['komponist'] / stats['total'] * 100) if stats['total'] > 0 else 0 #BITTE ANPASSEN
                st.markdown(f"""
                <div class="stat-box">
                    <h2>{pct:.1f}%</h2>
                    <p>Mit Komponist</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                pct = (stats['signatur'] / stats['total'] * 100) if stats['total'] > 0 else 0 #BITTE ANPASSEN
                st.markdown(f"""
                <div class="stat-box">
                    <h2>{pct:.1f}%</h2>
                    <p>Mit Signatur</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Vollständigkeit
            st.markdown("### 📈 Vollständigkeit")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                pct = (stats['complete'] / stats['total'] * 100) if stats['total'] > 0 else 0
                st.metric("Vollständig (≥6 Felder)", f"{stats['complete']:,}", f"{pct:.1f}%")
            
            with col2:
                medium = stats['total'] - stats['complete'] - stats['sparse']
                pct = (medium / stats['total'] * 100) if stats['total'] > 0 else 0
                st.metric("Mittel (3-5 Felder)", f"{medium:,}", f"{pct:.1f}%")
            
            with col3:
                pct = (stats['sparse'] / stats['total'] * 100) if stats['total'] > 0 else 0
                st.metric("Spärlich (≤2 Felder)", f"{stats['sparse']:,}", f"{pct:.1f}%")
            
            st.markdown("---")
            
            # Feld-Vollständigkeit
            st.markdown("### 📋 Feld-Vollständigkeit")
            
            field_stats = []
            for field in EDITABLE_FIELDS:
                filled = (df[field].fillna('').str.strip() != '').sum()
                percentage = (filled / len(df)) * 100
                field_stats.append({
                    'Feld': field,
                    'Ausgefüllt': filled,
                    'Prozent': percentage
                })
            
            field_df = pd.DataFrame(field_stats)
            field_df = field_df.sort_values('Prozent', ascending=False)
            
            st.dataframe(
                field_df.style.format({'Ausgefüllt': '{:,}', 'Prozent': '{:.1f}%'}),
                use_container_width=True,
                hide_index=True
            )
            
            st.markdown("---")
            
            # Batch-Vergleich
            st.markdown("### 📦 Batch-Vergleich")
            
            if 'Batch' in df.columns:
                batch_stats = df.groupby('Batch').agg({
                    'Datei': 'count',
                    'Komponist': lambda x: (x.fillna('').str.strip() != '').sum(), #BITTE ANPASSEN
                    'Signatur': lambda x: (x.fillna('').str.strip() != '').sum() #BITTE ANPASSEN
                }).rename(columns={
                    'Datei': 'Gesamt',
                    'Komponist': 'Mit Komponist', #BITTE ANPASSEN
                    'Signatur': 'Mit Signatur' #BITTE ANPASSEN
                })
                
                batch_stats['% Komponist'] = (batch_stats['Mit Komponist'] / batch_stats['Gesamt'] * 100).round(1) #BITTE ANPASSEN
                batch_stats['% Signatur'] = (batch_stats['Mit Signatur'] / batch_stats['Gesamt'] * 100).round(1) #BITTE ANPASSEN
                
                st.dataframe(
                    batch_stats.style.format({
                        'Gesamt': '{:,}',
                        'Mit Komponist': '{:,}', #BITTE ANPASSEN
                        'Mit Signatur': '{:,}', #BITTE ANPASSEN
                        '% Komponist': '{:.1f}%', #BITTE ANPASSEN
                        '% Signatur': '{:.1f}%' #BITTE ANPASSEN
                    }),
                    use_container_width=True
                )
            
            st.markdown("---")
            
            # Export
            st.markdown("### 💾 Export")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Download CSV
                csv = df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
                st.download_button(
                    label="📥 CSV herunterladen",
                    data=csv,
                    file_name="XXXX_complete.csv", #Bitte anpassen!
                    mime="text/csv"
                )
            
            with col2:
                # Download Problematische Karten
                field_counts = df[EDITABLE_FIELDS].fillna('').apply(
                    lambda row: sum(str(val).strip() != '' for val in row), axis=1
                )
                problematic = df[field_counts <= 2]
                
                if len(problematic) > 0:
                    csv_prob = problematic[['Datei', 'Batch', 'Komponist', 'Signatur']].to_csv( #BITTE ANPASSEN
                        index=False, 
                        encoding='utf-8-sig'
                    ).encode('utf-8-sig')
                    st.download_button(
                        label="⚠️ Problematische Karten",
                        data=csv_prob,
                        file_name="problematic_cards.csv",
                        mime="text/csv"
                    )
    else:
        st.error(f"Master-CSV nicht gefunden: {MASTER_CSV}")

elif mode == "🔍 Suche":
    
    st.title("🔍 Suche")
    
    # Lade Master-CSV
    if Path(MASTER_CSV).exists():
        df = load_csv_data(MASTER_CSV)
        
        if df is not None:
            # Suchfeld
            search_term = st.text_input(
                "Suchbegriff:",
                placeholder="Komponist, Titel, Signatur..." #BITTE ANPASSEN
            )
            
            if search_term:
                # Suche in allen relevanten Feldern
                mask = (
                    df['Komponist'].fillna('').str.contains(search_term, case=False) | #BITTE ANPASSEN
                    df['Titel'].fillna('').str.contains(search_term, case=False) | #BITTE ANPASSEN
                    df['Signatur'].fillna('').str.contains(search_term, case=False) | #BITTE ANPASSEN
                    df['Textanfang'].fillna('').str.contains(search_term, case=False) #BITTE ANPASSEN
                )
                
                results = df[mask]
                
                st.markdown(f"**{len(results)} Treffer** für '{search_term}'")
                
                if len(results) > 0:
                    st.markdown("---")
                    
                    # Zeige Ergebnisse
                    display_cols = ['Datei', 'Batch', 'Komponist', 'Signatur', 'Titel'] #BITTE ANPASSEN
                    st.dataframe(
                        results[display_cols],
                        use_container_width=True,
                        hide_index=True
                    )
                    
                    # Export Suchergebnisse
                    csv = results.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
                    st.download_button(
                        label="📥 Suchergebnisse exportieren",
                        data=csv,
                        file_name=f"search_{search_term}.csv",
                        mime="text/csv"
                    )
            else:
                st.info("Gib einen Suchbegriff ein, um Karteikarten zu finden.")
    else:
        st.error(f"Master-CSV nicht gefunden: {MASTER_CSV}")

# === FOOTER ===
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p><strong>Indexcards OCR Quality Control</strong></p> #Bei Bedarf bitte anpassen
    <p>Name Museum | Team oder Arbeitsgruppe</p> #Bitte anpassen!
</div>
""", unsafe_allow_html=True)
