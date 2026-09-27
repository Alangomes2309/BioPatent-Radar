import streamlit as st
import pandas as pd
import altair as alt
import os

from urllib.parse import quote
from dotenv import load_dotenv
from google import genai


# =========================================================
# SETTINGS
# =========================================================

HIGH_RELEVANCE_THRESHOLD = 15


# =========================================================
# ENV + AI CLIENT
# =========================================================

load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(
    api_key=gemini_api_key
)


# =========================================================
# COUNTRY NAMES
# =========================================================

COUNTRY_NAMES = {
    "US": "United States",
    "CN": "China",
    "JP": "Japan",
    "KR": "South Korea",
    "DE": "Germany",
    "FR": "France",
    "GB": "United Kingdom",
    "BR": "Brazil",
    "ES": "Spain",
    "IT": "Italy",
    "NL": "Netherlands",
    "BE": "Belgium",
    "CH": "Switzerland",
    "AT": "Austria",
    "SE": "Sweden",
    "DK": "Denmark",
    "NO": "Norway",
    "FI": "Finland",
    "CA": "Canada",
    "AU": "Australia",
    "NZ": "New Zealand",
    "IN": "India",
    "SG": "Singapore",
    "IL": "Israel",
    "MX": "Mexico",
    "AR": "Argentina",
    "CL": "Chile",
    "ZA": "South Africa",
    "TW": "Taiwan",
    "RU": "Russia",
    "PL": "Poland",
    "CZ": "Czech Republic",
    "EP": "European Patent Office",
    "WO": "WIPO / International"
}


def get_country_name(code):

    if pd.isna(code):
        return "Unknown"

    code = str(code).strip()

    return COUNTRY_NAMES.get(
        code,
        code
    )


# =========================================================
# AI FUNCTIONS
# =========================================================

def analyze_patent(title, abstract, language):

    prompt = f"""
You are a biotechnology patent intelligence analyst.

Analyze the patent below.

Title:
{title}

Abstract:
{abstract}

LANGUAGE INSTRUCTION:

Write the CONTENT of the analysis in {language}.

IMPORTANT:
The section headings MUST remain EXACTLY in English.
Do NOT translate the section headings.

Use EXACTLY these headings:

Technical Summary:
Main Innovation:
Process:
Organism:
Product:
Industrial Relevance:

Do not add any other headings.

Keep every section concise, clear and technically useful.

Focus on biotechnology, fermentation, bioprocessing,
industrial biotechnology and potential industrial applications.

If information is not explicitly available in the abstract,
state that it is not clearly specified instead of inventing information.
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )

    return response.text


def parse_ai_analysis(text):

    sections = {
        "Technical Summary": "",
        "Main Innovation": "",
        "Process": "",
        "Organism": "",
        "Product": "",
        "Industrial Relevance": ""
    }

    current_section = None

    for line in text.splitlines():

        line = line.strip()

        if not line:
            continue

        section_found = False

        for section in sections:

            if line.startswith(section + ":"):

                current_section = section

                content = line.replace(
                    section + ":",
                    "",
                    1
                ).strip()

                sections[section] = content

                section_found = True
                break

        if not section_found and current_section:

            if sections[current_section]:
                sections[current_section] += " " + line
            else:
                sections[current_section] = line

    return sections


# =========================================================
# DATE FUNCTION
# =========================================================

def format_publication_date(value):

    if pd.isna(value):
        return "Unknown"

    value = str(value).strip()

    if value.endswith(".0"):
        value = value[:-2]

    if len(value) == 8 and value.isdigit():

        try:

            date = pd.to_datetime(
                value,
                format="%Y%m%d"
            )

            return date.strftime("%Y-%m-%d")

        except ValueError:

            return value

    date = pd.to_datetime(
        value,
        errors="coerce"
    )

    if pd.notna(date):

        return date.strftime("%Y-%m-%d")

    return value


# =========================================================
# PATENT LINK FUNCTIONS
# =========================================================

def clean_patent_part(value):

    if pd.isna(value):
        return ""

    value = str(value).strip()

    if value.endswith(".0"):
        value = value[:-2]

    return value.replace(" ", "")


def build_publication_number(patent):

    country = clean_patent_part(
        patent["pais"]
    )

    number = clean_patent_part(
        patent["numero"]
    )

    kind = clean_patent_part(
        patent["tipo"]
    )

    return f"{country}{number}{kind}"


def build_espacenet_url(patent):

    publication_number = build_publication_number(
        patent
    )

    query = quote(
        f'pn="{publication_number}"'
    )

    return (
        "https://worldwide.espacenet.com/"
        f"patent/search?q={query}"
    )


def build_ep_pdf_url(patent):

    country = clean_patent_part(
        patent["pais"]
    )

    number = clean_patent_part(
        patent["numero"]
    )

    kind = clean_patent_part(
        patent["tipo"]
    )

    if country != "EP":
        return None

    return (
        "https://data.epo.org/"
        "publication-server/pdf-document"
        f"?cc={country}"
        f"&pn={number}"
        f"&ki={kind}"
    )


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="BioPatent Radar",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# CUSTOM CSS
# =========================================================

CUSTOM_CSS = """
<style>

.block-container {
    max-width: 1500px;
    padding-top: 1.8rem;
    padding-bottom: 3rem;
}

h1, h2, h3 {
    letter-spacing: -0.02em;
}

.hero-title {
    text-align: center;
    font-size: 4.2rem;
    font-weight: 800;
    margin-top: 0.5rem;
    margin-bottom: 0.2rem;
    line-height: 1.05;
}

.hero-title span {
    color: #19a582;
}

.hero-subtitle {
    text-align: center;
    font-size: 1.15rem;
    opacity: 0.78;
    margin-top: 0.5rem;
    margin-bottom: 0.7rem;
}

.hero-features {
    text-align: center;
    font-size: 0.92rem;
    opacity: 0.65;
    margin-bottom: 2.5rem;
}

.section-label {
    font-size: 0.76rem;
    font-weight: 700;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: #19a582;
    margin-bottom: -0.7rem;
}

[data-testid="stMetric"] {
    border: 1px solid rgba(128, 128, 128, 0.18);
    border-radius: 16px;
    padding: 18px 20px;
    background: rgba(128, 128, 128, 0.035);
    min-height: 105px;
}

[data-testid="stMetricLabel"] {
    font-weight: 600;
}

[data-testid="stMetricValue"] {
    font-weight: 750;
}

[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 16px;
}

.stButton > button {
    border-radius: 10px;
    font-weight: 650;
}

.stLinkButton > a {
    border-radius: 10px;
    font-weight: 650;
}

[data-testid="stSidebar"] {
    border-right: 1px solid rgba(128,128,128,0.14);
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #19a582;
}

.patent-title {
    font-size: 1.65rem;
    font-weight: 760;
    line-height: 1.3;
    margin-bottom: 1rem;
}

.top-category-label {
    font-size: 0.88rem;
    opacity: 0.82;
    font-weight: 600;
}

.top-category-name {
    font-size: 1.30rem;
    font-weight: 750;
    line-height: 1.15;
    margin-top: 0.35rem;
}

.footer {
    text-align: center;
    opacity: 0.55;
    font-size: 0.82rem;
    padding-top: 1rem;
}

</style>
"""

st.markdown(
    CUSTOM_CSS,
    unsafe_allow_html=True
)


# =========================================================
# HERO
# =========================================================

st.markdown(
    """
    <div class="hero-title">
        🧬 BioPatent <span>Radar</span>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="hero-subtitle">
        Patent intelligence for bioprocessing,
        fermentation and industrial biotechnology.
    </div>

    <div class="hero-features">
        Discover emerging technologies &nbsp; • &nbsp;
        Monitor patent activity &nbsp; • &nbsp;
        Explore technical trends &nbsp; • &nbsp;
        Generate AI-powered intelligence
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# LOAD DATA
# =========================================================

data = pd.read_csv(
    "patentes.csv",
    dtype={
        "numero": str,
        "data": str
    }
)

data["relevancia"] = pd.to_numeric(
    data["relevancia"],
    errors="coerce"
).fillna(0)

data["data_formatada"] = data["data"].apply(
    format_publication_date
)

data["country_name"] = data["pais"].apply(
    get_country_name
)


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.markdown(
    "## 🔎 Patent Radar"
)

st.sidebar.caption(
    "Search and filter the biotechnology patent landscape."
)

search_term = st.sidebar.text_input(
    "Search patents",
    placeholder="fermentation, fed-batch, bioreactor..."
)


country_options = (
    data[
        ["pais", "country_name"]
    ]
    .dropna()
    .drop_duplicates()
    .sort_values(
        by="country_name"
    )
)


country_display_options = (
    ["All"]
    + country_options["country_name"].tolist()
)


selected_country_name = st.sidebar.selectbox(
    "Country",
    country_display_options
)


selected_country_code = None


if selected_country_name != "All":

    selected_country_code = (
        country_options[
            country_options["country_name"]
            == selected_country_name
        ]["pais"]
        .iloc[0]
    )


categories = sorted(
    data["categoria_dominante"]
    .dropna()
    .replace("", pd.NA)
    .dropna()
    .unique()
)


selected_category = st.sidebar.selectbox(
    "Technology category",
    ["All"] + list(categories)
)


maximum_relevance = int(
    data["relevancia"].max()
)


minimum_relevance = st.sidebar.slider(
    "Minimum relevance score",
    min_value=0,
    max_value=maximum_relevance,
    value=0
)


st.sidebar.caption(
    f"High Relevance is defined as a technical score ≥ "
    f"{HIGH_RELEVANCE_THRESHOLD}."
)


st.sidebar.divider()


st.sidebar.markdown(
    "### 🤖 AI Intelligence"
)


ai_language = st.sidebar.selectbox(
    "Analysis language",
    [
        "English",
        "Português",
        "Español"
    ]
)


st.sidebar.divider()


st.sidebar.markdown(
    "### ℹ️ About"
)


st.sidebar.caption(
    """
BioPatent Radar combines patent data and AI-assisted
analysis to help identify relevant developments in
bioprocessing, fermentation and industrial biotechnology.
"""
)


st.sidebar.caption(
    """
AI-generated interpretations are informational
and are not legal advice.
"""
)


# =========================================================
# APPLY FILTERS
# =========================================================

filtered_data = data.copy()


if selected_country_code:

    filtered_data = filtered_data[
        filtered_data["pais"]
        == selected_country_code
    ]


if selected_category != "All":

    filtered_data = filtered_data[
        filtered_data["categoria_dominante"]
        == selected_category
    ]


filtered_data = filtered_data[
    filtered_data["relevancia"]
    >= minimum_relevance
]


if search_term:

    search_term_lower = search_term.lower()

    title_match = (
        filtered_data["titulo"]
        .fillna("")
        .str.lower()
        .str.contains(
            search_term_lower,
            regex=False
        )
    )

    abstract_match = (
        filtered_data["abstract"]
        .fillna("")
        .str.lower()
        .str.contains(
            search_term_lower,
            regex=False
        )
    )

    terms_match = (
        filtered_data["termos_detectados"]
        .fillna("")
        .str.lower()
        .str.contains(
            search_term_lower,
            regex=False
        )
    )

    filtered_data = filtered_data[
        title_match
        | abstract_match
        | terms_match
    ]


filtered_data = filtered_data.sort_values(
    by="relevancia",
    ascending=False
)


# =========================================================
# RADAR OVERVIEW
# =========================================================

st.markdown(
    '<div class="section-label">Intelligence Dashboard</div>',
    unsafe_allow_html=True
)

st.markdown(
    "## Radar Overview"
)


high_relevance_count = len(
    filtered_data[
        filtered_data["relevancia"]
        >= HIGH_RELEVANCE_THRESHOLD
    ]
)


top_category = "N/A"


if not filtered_data.empty:

    category_counts = (
        filtered_data["categoria_dominante"]
        .replace("", pd.NA)
        .dropna()
        .value_counts()
    )

    if not category_counts.empty:

        top_category = (
            category_counts.index[0]
        )


# Slightly wider final column
k1, k2, k3, k4, k5 = st.columns(
    [1, 1, 1, 1, 1.35]
)


k1.metric(
    "📄 Patents",
    len(filtered_data)
)


k2.metric(
    f"⭐ High Relevance (≥{HIGH_RELEVANCE_THRESHOLD})",
    high_relevance_count
)


k3.metric(
    "🏢 Applicants",
    filtered_data["applicante"]
    .replace("", pd.NA)
    .dropna()
    .nunique()
)


k4.metric(
    "🌍 Countries",
    filtered_data["country_name"]
    .nunique()
)


# =========================================================
# TOP CATEGORY CARD
# =========================================================

with k5:

    with st.container(
        border=True
    ):

        st.markdown(
            '<div class="top-category-label">'
            '🧬 Top Category'
            '</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            f'<div class="top-category-name">'
            f'{top_category}'
            f'</div>',
            unsafe_allow_html=True
        )


# =========================================================
# TECHNOLOGY LANDSCAPE
# =========================================================

st.markdown(
    "<br>",
    unsafe_allow_html=True
)


st.markdown(
    '<div class="section-label">Technology Intelligence</div>',
    unsafe_allow_html=True
)


st.markdown(
    "## Technology Landscape"
)


chart1, chart2 = st.columns(2)


# =========================================================
# CATEGORY CHART
# =========================================================

with chart1:

    with st.container(
        border=True
    ):

        st.markdown(
            "### 🧬 Patents by Category"
        )

        category_data = (
            filtered_data["categoria_dominante"]
            .replace("", "Unclassified")
            .fillna("Unclassified")
            .value_counts()
            .rename_axis("Category")
            .reset_index(name="Patents")
        )


        category_chart = (
            alt.Chart(
                category_data
            )
            .mark_bar(
                cornerRadiusEnd=4
            )
            .encode(

                x=alt.X(
                    "Patents:Q",
                    title="Patents",
                    scale=alt.Scale(
                        domainMin=0
                    )
                ),

                y=alt.Y(
                    "Category:N",
                    sort="-x",
                    title=None,
                    axis=alt.Axis(
                        labelLimit=260
                    )
                ),

                tooltip=[
                    alt.Tooltip(
                        "Category:N",
                        title="Category"
                    ),
                    alt.Tooltip(
                        "Patents:Q",
                        title="Patents"
                    )
                ]
            )
            .properties(
                height=360
            )
        )


        st.altair_chart(
            category_chart,
            use_container_width=True
        )


# =========================================================
# COUNTRY CHART
# =========================================================

with chart2:

    with st.container(
        border=True
    ):

        st.markdown(
            "### 🌍 Patents by Country"
        )

        country_data = (
            filtered_data["country_name"]
            .fillna("Unknown")
            .value_counts()
            .head(10)
            .rename_axis("Country")
            .reset_index(name="Patents")
        )


        country_chart = (
            alt.Chart(
                country_data
            )
            .mark_bar(
                cornerRadiusEnd=4
            )
            .encode(

                x=alt.X(
                    "Country:N",
                    sort="-y",
                    title=None,
                    axis=alt.Axis(
                        labelAngle=-35,
                        labelLimit=140
                    )
                ),

                y=alt.Y(
                    "Patents:Q",
                    title="Patents",
                    scale=alt.Scale(
                        domainMin=0
                    )
                ),

                tooltip=[
                    alt.Tooltip(
                        "Country:N",
                        title="Country"
                    ),
                    alt.Tooltip(
                        "Patents:Q",
                        title="Patents"
                    )
                ]
            )
            .properties(
                height=360
            )
        )


        st.altair_chart(
            country_chart,
            use_container_width=True
        )


# =========================================================
# TOP APPLICANTS
# =========================================================

with st.container(
    border=True
):

    st.markdown(
        "### 🏢 Top Applicants"
    )


    applicant_data = (
        filtered_data["applicante"]
        .replace("", "Unknown")
        .fillna("Unknown")
        .value_counts()
        .head(10)
        .rename_axis("Applicant")
        .reset_index(name="Patents")
    )


    applicant_chart = (
        alt.Chart(
            applicant_data
        )
        .mark_bar(
            cornerRadiusEnd=4
        )
        .encode(

            x=alt.X(
                "Patents:Q",
                title="Patents",
                scale=alt.Scale(
                    domainMin=0
                )
            ),

            y=alt.Y(
                "Applicant:N",
                sort="-x",
                title=None,
                axis=alt.Axis(
                    labelLimit=350
                )
            ),

            tooltip=[
                alt.Tooltip(
                    "Applicant:N",
                    title="Applicant"
                ),
                alt.Tooltip(
                    "Patents:Q",
                    title="Patents"
                )
            ]
        )
        .properties(
            height=350
        )
    )


    st.altair_chart(
        applicant_chart,
        use_container_width=True
    )


# =========================================================
# PATENT EXPLORER
# =========================================================

st.markdown(
    "<br>",
    unsafe_allow_html=True
)


st.markdown(
    '<div class="section-label">Patent Intelligence</div>',
    unsafe_allow_html=True
)


st.markdown(
    "## Patent Explorer"
)


st.caption(
    f"Showing {len(filtered_data)} patents"
)


columns_to_display = [
    "titulo",
    "applicante",
    "country_name",
    "categoria_dominante",
    "relevancia",
    "data_formatada"
]


table_data = (
    filtered_data
    .reset_index(drop=True)
)


if table_data.empty:

    st.warning(
        "No patents match the current filters."
    )


else:

    display_table = table_data[
        columns_to_display
    ].copy()


    display_table = display_table.rename(
        columns={
            "titulo": "Title",
            "applicante": "Applicant",
            "country_name": "Country",
            "categoria_dominante": "Category",
            "relevancia": "Relevance",
            "data_formatada": "Publication Date"
        }
    )


    table_event = st.dataframe(
        display_table,
        use_container_width=True,
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row",
        key="patent_table",
        height=430,

        column_config={

            "Title":
                st.column_config.TextColumn(
                    "Title",
                    width="large"
                ),

            "Applicant":
                st.column_config.TextColumn(
                    "Applicant",
                    width="medium"
                ),

            "Country":
                st.column_config.TextColumn(
                    "Country",
                    width="medium"
                ),

            "Category":
                st.column_config.TextColumn(
                    "Category",
                    width="medium"
                ),

            "Relevance":
                st.column_config.NumberColumn(
                    "Relevance",
                    width="small"
                ),

            "Publication Date":
                st.column_config.TextColumn(
                    "Publication Date",
                    width="medium"
                )
        }
    )


    selected_rows = (
        table_event.selection.rows
    )


    if len(selected_rows) == 0:

        st.info(
            "👆 Select a patent in the table "
            "to open its intelligence panel."
        )


    else:

        selected_row = selected_rows[0]

        patent = table_data.iloc[
            selected_row
        ]


        publication_number = (
            build_publication_number(
                patent
            )
        )


        espacenet_url = (
            build_espacenet_url(
                patent
            )
        )


        ep_pdf_url = (
            build_ep_pdf_url(
                patent
            )
        )


        analysis_key = (
            f'{patent["pais"]}_'
            f'{patent["numero"]}_'
            f'{patent["tipo"]}_'
            f'{ai_language}'
        )


        # =====================================================
        # SELECTED PATENT
        # =====================================================

        st.markdown(
            "<br>",
            unsafe_allow_html=True
        )


        st.markdown(
            '<div class="section-label">Deep Dive</div>',
            unsafe_allow_html=True
        )


        st.markdown(
            "## Selected Patent"
        )


        with st.container(
            border=True
        ):

            st.markdown(
                f"""
                <div class="patent-title">
                    {patent["titulo"]}
                </div>
                """,
                unsafe_allow_html=True
            )


            meta1, meta2, meta3, meta4 = (
                st.columns(4)
            )


            meta1.metric(
                "⭐ Technical Score",
                int(
                    patent["relevancia"]
                )
            )


            meta2.metric(
                "🌍 Country",
                patent["country_name"]
            )


            meta3.metric(
                "🧬 Category",
                patent["categoria_dominante"]
            )


            meta4.metric(
                "📄 Publication",
                publication_number
            )


            info1, info2 = st.columns(2)


            with info1:

                st.markdown(
                    f"""
                    **Applicant**  
                    {patent["applicante"]}
                    """
                )


            with info2:

                st.markdown(
                    f"""
                    **Publication date**  
                    {patent["data_formatada"]}
                    """
                )


            # =================================================
            # FULL PATENT
            # =================================================

            st.divider()


            st.markdown(
                "### 📑 Full Patent Document"
            )


            if ep_pdf_url:

                link1, link2 = (
                    st.columns(2)
                )


                with link1:

                    st.link_button(
                        "🔎 View Full Patent",
                        espacenet_url,
                        use_container_width=True
                    )


                with link2:

                    st.link_button(
                        "📥 Open Official PDF",
                        ep_pdf_url,
                        use_container_width=True
                    )


            else:

                st.link_button(
                    "🔎 View Full Patent",
                    espacenet_url,
                    use_container_width=True
                )


            st.caption(
                "Opens the original publication "
                "in an external patent service."
            )


            # =================================================
            # ABSTRACT
            # =================================================

            st.markdown(
                "### 📖 Abstract"
            )


            st.write(
                patent["abstract"]
            )


            # =================================================
            # AI INTELLIGENCE
            # =================================================

            st.divider()


            st.markdown(
                "### ✨ AI Intelligence"
            )


            ai_head1, ai_head2 = (
                st.columns(
                    [3, 1]
                )
            )


            with ai_head1:

                st.caption(
                    f"Analysis language: "
                    f"{ai_language}"
                )


            with ai_head2:

                generate_analysis = st.button(
                    "✨ Generate AI Analysis",

                    key=(
                        f'generate_'
                        f'{patent["pais"]}_'
                        f'{patent["numero"]}_'
                        f'{patent["tipo"]}_'
                        f'{ai_language}'
                    ),

                    use_container_width=True
                )


            if generate_analysis:

                with st.spinner(
                    f"Generating analysis "
                    f"in {ai_language}..."
                ):

                    ai_result = analyze_patent(
                        patent["titulo"],
                        patent["abstract"],
                        ai_language
                    )


                    analysis = (
                        parse_ai_analysis(
                            ai_result
                        )
                    )


                    st.session_state[
                        analysis_key
                    ] = analysis


            # =================================================
            # SHOW AI ANALYSIS
            # =================================================

            if analysis_key in st.session_state:

                analysis = (
                    st.session_state[
                        analysis_key
                    ]
                )


                with st.container(
                    border=True
                ):

                    st.markdown(
                        "#### 📋 Technical Summary"
                    )

                    st.write(
                        analysis[
                            "Technical Summary"
                        ]
                    )


                with st.container(
                    border=True
                ):

                    st.markdown(
                        "#### 💡 Main Innovation"
                    )

                    st.write(
                        analysis[
                            "Main Innovation"
                        ]
                    )


                ai_col1, ai_col2 = (
                    st.columns(2)
                )


                with ai_col1:

                    with st.container(
                        border=True
                    ):

                        st.markdown(
                            "#### ⚙️ Process"
                        )

                        st.write(
                            analysis[
                                "Process"
                            ]
                        )


                    with st.container(
                        border=True
                    ):

                        st.markdown(
                            "#### 🦠 Organism"
                        )

                        st.write(
                            analysis[
                                "Organism"
                            ]
                        )


                with ai_col2:

                    with st.container(
                        border=True
                    ):

                        st.markdown(
                            "#### 🧪 Product"
                        )

                        st.write(
                            analysis[
                                "Product"
                            ]
                        )


                    with st.container(
                        border=True
                    ):

                        st.markdown(
                            "#### 🏭 Industrial Relevance"
                        )

                        st.write(
                            analysis[
                                "Industrial Relevance"
                            ]
                        )


            # =================================================
            # TECHNICAL SIGNALS
            # =================================================

            st.divider()


            st.markdown(
                "### 📡 Technical Signals"
            )


            signal1, signal2, signal3 = (
                st.columns(3)
            )


            with signal1:

                with st.container(
                    border=True
                ):

                    st.markdown(
                        "**Technical terms**"
                    )

                    st.write(
                        patent[
                            "termos_detectados"
                        ]
                    )


            with signal2:

                with st.container(
                    border=True
                ):

                    st.markdown(
                        "**Microorganisms**"
                    )

                    st.write(
                        patent[
                            "microorganismos"
                        ]
                    )


            with signal3:

                with st.container(
                    border=True
                ):

                    st.markdown(
                        "**Products / markets**"
                    )

                    st.write(
                        patent[
                            "produtos"
                        ]
                    )


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    "<br>",
    unsafe_allow_html=True
)

st.divider()

st.markdown(
    """
    <div class="footer">
        BioPatent Radar · AI-assisted biotechnology patent intelligence
        <br>
        AI-generated content is informational and is not legal advice.
    </div>
    """,
    unsafe_allow_html=True
)