import requests
from dotenv import load_dotenv
import os
import xml.etree.ElementTree as ET
import csv
import re
import time


# =====================================================================
# BIOPATENT RADAR
# =====================================================================
#
# Patent search, extraction and technical classification engine.
#
# Main areas:
#
# - Fermentation
# - Fed-Batch & Feeding Strategy
# - Bioreactor & Mass Transfer
# - Strain & Metabolic Engineering
# - Downstream Processing
# - Process Monitoring & Control
# - Scale-up & Industrialization
# - Precision Fermentation
#
# =====================================================================


# =====================================================================
# 1. TECHNICAL CLASSIFICATION TERMS
# =====================================================================


# ---------------------------------------------------------------------
# FERMENTATION PROCESS
# ---------------------------------------------------------------------

termos_fermentacao = {

    # Generic term intentionally has low weight
    "fermentation": 1,

    "microbial fermentation": 3,

    "batch fermentation": 4,

    "continuous fermentation": 5,

    "submerged fermentation": 5,

    "solid-state fermentation": 5,
    "solid state fermentation": 5,

    "anaerobic fermentation": 4,

    "aerobic fermentation": 4,

    "fermentation medium": 3,

    "fermentation broth": 3,

    "culture medium": 2,

    "inoculum": 2,

    "fermentation process": 4,

    "fermentation conditions": 3,
}


# ---------------------------------------------------------------------
# FED-BATCH & FEEDING STRATEGY
# ---------------------------------------------------------------------

termos_fed_batch = {

    "fed-batch": 7,

    "fed batch": 7,

    "fed-batch fermentation": 8,

    "fed batch fermentation": 8,

    "feeding strategy": 6,

    "feed strategy": 6,

    "substrate feeding": 6,

    "nutrient feeding": 5,

    "feeding profile": 6,

    "feed profile": 6,

    "feed rate": 4,

    "feeding rate": 4,

    "controlled feeding": 5,

    "continuous feeding": 4,

    "exponential feeding": 7,

    "constant feeding": 5,

    "pulse feeding": 5,

    "carbon feeding": 5,

    "glucose feeding": 5,

    "carbon source feeding": 5,

    "substrate addition": 4,

    "nutrient addition": 3,

    "high cell density": 6,

    "high-cell-density": 6,

    "high cell density fermentation": 7,

    "high cell density culture": 6,

    "high-density culture": 5,

    "specific growth rate": 4,
}


# ---------------------------------------------------------------------
# BIOREACTOR & MASS TRANSFER
# ---------------------------------------------------------------------

termos_biorreator = {

    "bioreactor": 5,

    "fermenter": 4,

    "fermentor": 4,

    "oxygen transfer": 5,

    "oxygen transfer rate": 6,

    "mass transfer": 5,

    "volumetric mass transfer": 6,

    "dissolved oxygen": 4,

    "agitation": 3,

    "aeration": 3,

    "stirred tank": 5,

    "stirred-tank": 5,

    "airlift": 5,

    "bubble column": 5,

    "sparger": 4,

    "impeller": 4,

    "mixing time": 4,

    "gas-liquid": 4,

    "gas liquid": 4,

    "oxygen uptake rate": 5,

    "kla": 6,
}


# ---------------------------------------------------------------------
# STRAIN & METABOLIC ENGINEERING
# ---------------------------------------------------------------------

termos_engenharia_genetica = {

    "metabolic engineering": 7,

    "genetically modified": 5,

    "genetically engineered": 5,

    "engineered microorganism": 6,

    "engineered microbial": 5,

    "engineered strain": 6,

    "strain improvement": 5,

    "strain engineering": 7,

    "recombinant": 2,

    "recombinant microorganism": 5,

    "gene expression": 4,

    "heterologous expression": 5,

    "expression vector": 4,

    "crispr": 5,

    "crispr-cas": 6,

    "synthetic biology": 6,

    "mutant strain": 4,

    "plasmid": 2,

    "gene knockout": 5,

    "gene deletion": 4,

    "gene overexpression": 5,

    "biosynthetic pathway": 5,

    "metabolic pathway": 4,

    "pathway engineering": 6,
}


# ---------------------------------------------------------------------
# DOWNSTREAM PROCESSING
# ---------------------------------------------------------------------

termos_downstream = {

    "downstream processing": 7,

    "product recovery": 6,

    "recovery process": 4,

    "purification": 4,

    "filtration": 2,

    "microfiltration": 4,

    "ultrafiltration": 5,

    "nanofiltration": 5,

    "centrifugation": 4,

    "chromatography": 5,

    "extraction": 2,

    "solvent extraction": 4,

    "separation process": 4,

    "membrane separation": 5,

    "cell separation": 4,

    "biomass separation": 4,

    "crystallization": 4,

    "precipitation": 3,

    "cell disruption": 4,

    "product isolation": 5,

    "drying": 1,

    "spray drying": 4,
}


# ---------------------------------------------------------------------
# PROCESS MONITORING & CONTROL
# ---------------------------------------------------------------------

termos_monitoramento = {

    "process monitoring": 6,

    "real-time monitoring": 7,

    "real time monitoring": 7,

    "online monitoring": 6,

    "on-line monitoring": 6,

    "process control": 6,

    "bioprocess control": 6,

    "fermentation control": 6,

    "feedback control": 5,

    "automated control": 4,

    "automatic control": 4,

    "process analytical technology": 7,

    "soft sensor": 6,

    "biosensor": 3,

    "process sensor": 4,

    "raman spectroscopy": 5,

    "near infrared": 4,

    "near-infrared": 4,

    "digital twin": 7,

    "predictive control": 6,

    "model predictive control": 7,

    "ph control": 3,

    "temperature control": 3,

    "dissolved oxygen control": 5,

    "biomass monitoring": 5,
}


# ---------------------------------------------------------------------
# SCALE-UP & INDUSTRIALIZATION
# ---------------------------------------------------------------------

termos_escala = {

    "scale-up": 7,

    "scale up": 7,

    "scale-down": 5,

    "scale down": 5,

    "pilot scale": 6,

    "pilot-scale": 6,

    "industrial scale": 7,

    "industrial-scale": 7,

    "large scale": 5,

    "large-scale": 5,

    "commercial scale": 6,

    "commercial-scale": 6,

    "commercial production": 4,

    "industrial production": 5,

    "industrial fermentation": 6,

    "manufacturing process": 3,

    "production capacity": 3,

    "production scale": 5,

    "scale-up strategy": 7,

    "scale up strategy": 7,
}


# ---------------------------------------------------------------------
# PRECISION FERMENTATION
# ---------------------------------------------------------------------

termos_precisao = {

    "precision fermentation": 9,

    "cell-free protein synthesis": 7,

    "cell free protein synthesis": 7,

    "microbial protein production": 6,

    "recombinant protein production": 5,

    "heterologous protein production": 6,

    "microbial production of protein": 6,

    "animal-free protein": 7,

    "animal free protein": 7,

    "alternative protein": 4,

    "single cell protein": 4,

    "single-cell protein": 4,
}


# =====================================================================
# 2. TAGS
# =====================================================================


# ---------------------------------------------------------------------
# MICROORGANISMS
# ---------------------------------------------------------------------

termos_microorganismos = {

    "yeast": 1,

    "saccharomyces": 2,

    "saccharomyces cerevisiae": 3,

    "bacteria": 1,

    "bacterial": 1,

    "escherichia coli": 3,

    "e. coli": 3,

    "bacillus": 2,

    "lactobacillus": 2,

    "lactic acid bacteria": 2,

    "fungal": 1,

    "fungi": 1,

    "filamentous fungi": 2,

    "aspergillus": 2,

    "pichia": 2,

    "komagataella": 2,

    "algae": 1,

    "microalgae": 2,

    "cyanobacteria": 2,

    "clostridium": 2,

    "corynebacterium": 2,

    "streptomyces": 2,
}


# ---------------------------------------------------------------------
# PRODUCTS / MARKETS
# ---------------------------------------------------------------------

termos_produtos = {

    "biofuel": 2,

    "bioethanol": 2,

    "biodiesel": 2,

    "bioplastic": 2,

    "biopolymer": 2,

    "enzyme": 1,

    "enzyme production": 2,

    "organic acid": 2,

    "lactic acid": 2,

    "succinic acid": 2,

    "citric acid": 2,

    "amino acid": 2,

    "recombinant protein": 2,

    "single cell protein": 3,

    "single-cell protein": 3,

    "alternative protein": 2,

    "biosurfactant": 2,

    "cultivated meat": 2,

    "biomaterial": 2,

    "antibiotic": 2,

    "vitamin": 2,

    "flavor": 1,

    "flavour": 1,

    "fragrance": 1,

    "pigment": 1,

    "lipid": 1,

    "fatty acid": 2,
}


# ---------------------------------------------------------------------
# SUSTAINABILITY
# ---------------------------------------------------------------------

termos_sustentabilidade = {

    "waste valorization": 3,

    "waste valorisation": 3,

    "circular economy": 3,

    "lignocellulosic": 2,

    "agricultural waste": 2,

    "industrial waste": 2,

    "carbon capture": 3,

    "carbon dioxide utilization": 3,

    "carbon dioxide utilisation": 3,

    "renewable feedstock": 3,

    "renewable raw material": 2,

    "green chemistry": 2,

    "by-product valorization": 3,

    "by-product valorisation": 3,

    "waste stream": 2,

    "side stream": 2,
}


# =====================================================================
# 3. MASTER CLASSIFICATION DICTIONARIES
# =====================================================================

CATEGORIAS_SCORE = {

    "Fermentation Process":
        termos_fermentacao,

    "Fed-Batch & Feeding Strategy":
        termos_fed_batch,

    "Bioreactor & Mass Transfer":
        termos_biorreator,

    "Strain & Metabolic Engineering":
        termos_engenharia_genetica,

    "Downstream Processing":
        termos_downstream,

    "Process Monitoring & Control":
        termos_monitoramento,

    "Scale-up & Industrialization":
        termos_escala,

    "Precision Fermentation":
        termos_precisao,
}


CATEGORIAS_TAGS = {

    "microorganismos":
        termos_microorganismos,

    "produtos":
        termos_produtos,

    "sustentabilidade":
        termos_sustentabilidade,
}


# =====================================================================
# 4. TEXT MATCHING
# =====================================================================

def contem_termo(texto, termo):

    if not texto or not termo:
        return False

    padrao = (
        r"(?<!\w)"
        + re.escape(termo.lower())
        + r"(?!\w)"
    )

    return re.search(
        padrao,
        texto.lower()
    ) is not None


# =====================================================================
# 5. TECHNICAL CLASSIFICATION
# =====================================================================

def classificar_relevancia(titulo, abstract):

    titulo = titulo or ""
    abstract = abstract or ""

    titulo_lower = titulo.lower()
    abstract_lower = abstract.lower()

    pontos_por_categoria = {}

    termos_detectados = []


    # -------------------------------------------------------------
    # CATEGORY SCORING
    #
    # Match in TITLE:
    # weight x 2
    #
    # Match only in ABSTRACT:
    # normal weight
    # -------------------------------------------------------------

    for nome_categoria, termos in CATEGORIAS_SCORE.items():

        pontos_categoria = 0

        for palavra, peso in termos.items():

            encontrado_titulo = contem_termo(
                titulo_lower,
                palavra
            )

            encontrado_abstract = contem_termo(
                abstract_lower,
                palavra
            )


            if encontrado_titulo:

                pontos_categoria += (
                    peso * 2
                )

                termos_detectados.append(
                    palavra
                )


            elif encontrado_abstract:

                pontos_categoria += peso

                termos_detectados.append(
                    palavra
                )


        pontos_por_categoria[
            nome_categoria
        ] = pontos_categoria


    # -------------------------------------------------------------
    # TOTAL TECHNICAL SCORE
    # -------------------------------------------------------------

    pontuacao_total = sum(
        pontos_por_categoria.values()
    )


    # -------------------------------------------------------------
    # DOMINANT CATEGORY
    # -------------------------------------------------------------

    if pontuacao_total > 0:

        categoria_dominante = max(
            pontos_por_categoria,
            key=pontos_por_categoria.get
        )

    else:

        categoria_dominante = ""


    # -------------------------------------------------------------
    # REMOVE DUPLICATED TERMS
    # -------------------------------------------------------------

    termos_detectados = list(
        dict.fromkeys(
            termos_detectados
        )
    )


    # -------------------------------------------------------------
    # TAGS
    # -------------------------------------------------------------

    texto_completo = (
        titulo_lower
        + " "
        + abstract_lower
    )


    tags_microorganismos = []

    tags_produtos = []

    tags_sustentabilidade = []


    for palavra in termos_microorganismos:

        if contem_termo(
            texto_completo,
            palavra
        ):

            tags_microorganismos.append(
                palavra
            )


    for palavra in termos_produtos:

        if contem_termo(
            texto_completo,
            palavra
        ):

            tags_produtos.append(
                palavra
            )


    for palavra in termos_sustentabilidade:

        if contem_termo(
            texto_completo,
            palavra
        ):

            tags_sustentabilidade.append(
                palavra
            )


    tags_microorganismos = list(
        dict.fromkeys(
            tags_microorganismos
        )
    )


    tags_produtos = list(
        dict.fromkeys(
            tags_produtos
        )
    )


    tags_sustentabilidade = list(
        dict.fromkeys(
            tags_sustentabilidade
        )
    )


    return (

        pontuacao_total,

        categoria_dominante,

        pontos_por_categoria,

        termos_detectados,

        tags_microorganismos,

        tags_produtos,

        tags_sustentabilidade
    )


# =====================================================================
# 6. LOAD EPO CREDENTIALS
# =====================================================================

load_dotenv()


consumer_key = os.getenv(
    "EPO_CONSUMER_KEY"
)


consumer_secret = os.getenv(
    "EPO_CONSUMER_SECRET"
)


if not consumer_key or not consumer_secret:

    raise ValueError(
        "EPO credentials were not found in the .env file."
    )


# =====================================================================
# 7. EPO AUTHENTICATION
# =====================================================================

token_url = (
    "https://ops.epo.org/"
    "3.2/auth/accesstoken"
)


resposta_token = requests.post(

    token_url,

    auth=(
        consumer_key,
        consumer_secret
    ),

    data={
        "grant_type":
            "client_credentials"
    },

    timeout=30
)


print(
    "Status da autenticação:",
    resposta_token.status_code
)


resposta_token.raise_for_status()


token = (
    resposta_token
    .json()[
        "access_token"
    ]
)


print(
    "Autenticação OK!"
)


# =====================================================================
# 8. EPO PATENT SEARCH
# =====================================================================

search_url = (

    "https://ops.epo.org/3.2/"
    "rest-services/"
    "published-data/search/biblio"
)


headers = {

    "Authorization":
        f"Bearer {token}",

    "Accept":
        "application/exchange+xml"
}


# =====================================================================
# 9. BIOPATENT RADAR SEARCH MATRIX
# =====================================================================
#
# The search matrix intentionally covers multiple technological
# dimensions instead of searching only "fermentation".
#
# =====================================================================

queries = [


    # -------------------------------------------------------------
    # FERMENTATION
    # -------------------------------------------------------------

    "ta=fermentation",

    'ta="microbial fermentation"',

    'ta="continuous fermentation"',

    'ta="solid state fermentation"',


    # -------------------------------------------------------------
    # FED-BATCH & FEEDING STRATEGY
    # -------------------------------------------------------------

    'ta="fed batch"',

    'ta="fed batch fermentation"',

    'ta="feeding strategy"',

    'ta="substrate feeding"',

    'ta="nutrient feeding"',

    'ta="high cell density"',

    'ta="high cell density fermentation"',

    'ta="exponential feeding"',


    # -------------------------------------------------------------
    # BIOREACTOR & MASS TRANSFER
    # -------------------------------------------------------------

    "ta=bioreactor",

    'ta="oxygen transfer"',

    'ta="mass transfer"',

    'ta="dissolved oxygen"',


    # -------------------------------------------------------------
    # STRAIN & METABOLIC ENGINEERING
    # -------------------------------------------------------------

    'ta="metabolic engineering"',

    'ta="strain engineering"',

    'ta="engineered microorganism"',

    'ta="synthetic biology"',


    # -------------------------------------------------------------
    # DOWNSTREAM PROCESSING
    # -------------------------------------------------------------

    'ta="downstream processing"',

    'ta="product recovery"',

    'ta="membrane separation"',

    'ta="ultrafiltration"',


    # -------------------------------------------------------------
    # PROCESS MONITORING & CONTROL
    # -------------------------------------------------------------

    'ta="process monitoring"',

    'ta="process control"',

    'ta="real time monitoring"',

    'ta="model predictive control"',


    # -------------------------------------------------------------
    # SCALE-UP & INDUSTRIALIZATION
    # -------------------------------------------------------------

    'ta="scale up"',

    'ta="pilot scale"',

    'ta="industrial scale"',

    'ta="industrial fermentation"',


    # -------------------------------------------------------------
    # PRECISION FERMENTATION
    # -------------------------------------------------------------

    'ta="precision fermentation"',

    'ta="microbial protein production"',

    'ta="heterologous protein production"'
]


# =====================================================================
# 10. EXECUTE SEARCHES
# =====================================================================

todas_publicacoes = []


print()

print(
    "=========================================="
)

print(
    "BIOPATENT RADAR - EPO SEARCH"
)

print(
    "=========================================="
)

print()

print(
    "Número de consultas:",
    len(queries)
)

print()


for numero_query, query in enumerate(
    queries,
    start=1
):

    print(
        f"[{numero_query}/{len(queries)}]"
    )

    print(
        "Buscando:",
        query
    )


    params = {

        "q":
            query
    }


    try:

        resposta_busca = requests.get(

            search_url,

            headers=headers,

            params=params,

            timeout=30
        )


        print(

            "Status da busca:",

            resposta_busca.status_code
        )


        if resposta_busca.status_code != 200:

            print(
                "Busca ignorada por erro."
            )

            print()

            time.sleep(0.5)

            continue


        dados = (
            resposta_busca.text
        )


        print(

            "Caracteres recebidos:",

            len(dados)
        )


        try:

            raiz = ET.fromstring(
                dados
            )

        except ET.ParseError:

            print(
                "Resposta XML inválida."
            )

            print()

            time.sleep(0.5)

            continue


        publicacoes = raiz.findall(
            ".//{*}exchange-document"
        )


        print(

            "Patentes encontradas:",

            len(publicacoes)
        )


        for patente in publicacoes:

            todas_publicacoes.append(
                (
                    patente,
                    query
                )
            )


    except requests.RequestException as erro:

        print(
            "Erro na requisição:",
            erro
        )


    print()


    # Small pause between EPO requests.
    time.sleep(0.5)


# =====================================================================
# 11. ACCUMULATED RESULTS
# =====================================================================

print()

print(
    "=========================================="
)

print(
    "RESULTADOS BRUTOS"
)

print(
    "=========================================="
)

print()

print(

    "Total de resultados acumulados:",

    len(todas_publicacoes)
)


# =====================================================================
# 12. REMOVE DUPLICATES
# =====================================================================

publicacoes_unicas = []

numeros_vistos = set()


for patente, query in todas_publicacoes:


    numero = patente.find(

        ".//{*}publication-reference/"
        "{*}document-id/{*}doc-number"
    )


    pais = patente.find(

        ".//{*}publication-reference/"
        "{*}document-id/{*}country"
    )


    tipo = patente.find(

        ".//{*}publication-reference/"
        "{*}document-id/{*}kind"
    )


    numero_texto = (

        numero.text

        if numero is not None

        else ""
    )


    pais_texto = (

        pais.text

        if pais is not None

        else ""
    )


    tipo_texto = (

        tipo.text

        if tipo is not None

        else ""
    )


    identificador = (

        pais_texto,

        numero_texto,

        tipo_texto
    )


    if identificador not in numeros_vistos:

        numeros_vistos.add(
            identificador
        )


        publicacoes_unicas.append(
            (
                patente,
                query
            )
        )


print()

print(

    "Patentes únicas:",

    len(publicacoes_unicas)
)


# =====================================================================
# 13. CLASSIFICATION SUMMARY
# =====================================================================

resumo_categorias = {

    categoria: 0

    for categoria
    in CATEGORIAS_SCORE
}


sem_classificacao = 0


print()

print(
    "=========================================="
)

print(
    "CLASSIFICANDO PATENTES"
)

print(
    "=========================================="
)

print()


for patente, query in publicacoes_unicas:


    titulo = patente.find(
        ".//{*}invention-title"
    )


    abstract = patente.find(
        ".//{*}abstract"
    )


    texto_titulo = (

        titulo.text

        if titulo is not None
        and titulo.text

        else ""
    )


    if abstract is not None:

        texto_abstract = " ".join(
            abstract.itertext()
        )

    else:

        texto_abstract = ""


    (

        pontuacao,

        categoria_dominante,

        pontos_por_categoria,

        termos_detectados,

        tags_microorganismos,

        tags_produtos,

        tags_sustentabilidade

    ) = classificar_relevancia(

        texto_titulo,

        texto_abstract
    )


    if categoria_dominante:

        resumo_categorias[
            categoria_dominante
        ] += 1

    else:

        sem_classificacao += 1


# =====================================================================
# 14. CATEGORY DISTRIBUTION
# =====================================================================

print()

print(
    "=========================================="
)

print(
    "DISTRIBUIÇÃO DAS CATEGORIAS"
)

print(
    "=========================================="
)

print()


for categoria, quantidade in (
    resumo_categorias.items()
):

    print(
        "-",
        categoria,
        ":",
        quantidade
    )


print(
    "- Unclassified:",
    sem_classificacao
)


# =====================================================================
# 15. CREATE CSV
# =====================================================================

with open(

    "patentes.csv",

    "w",

    newline="",

    encoding="utf-8-sig"

) as arquivo:


    escritor = csv.writer(
        arquivo
    )


    # -------------------------------------------------------------
    # SAME CSV COLUMNS AS BEFORE
    # -------------------------------------------------------------

    escritor.writerow([

        "numero",

        "pais",

        "tipo",

        "applicante",

        "data",

        "titulo",

        "abstract",

        "query",

        "relevancia",

        "categoria_dominante",

        "scores_por_categoria",

        "termos_detectados",

        "microorganismos",

        "produtos",

        "sustentabilidade"

    ])


    # -------------------------------------------------------------
    # PROCESS EACH PATENT
    # -------------------------------------------------------------

    for patente, query in publicacoes_unicas:


        numero = patente.find(

            ".//{*}publication-reference/"
            "{*}document-id/{*}doc-number"
        )


        pais = patente.find(

            ".//{*}publication-reference/"
            "{*}document-id/{*}country"
        )


        tipo = patente.find(

            ".//{*}publication-reference/"
            "{*}document-id/{*}kind"
        )


        applicante = patente.find(

            ".//{*}parties/{*}applicants/"
            "{*}applicant/{*}applicant-name/"
            "{*}name"
        )


        data = patente.find(

            ".//{*}publication-reference/"
            "{*}document-id/{*}date"
        )


        titulo = patente.find(
            ".//{*}invention-title"
        )


        abstract = patente.find(
            ".//{*}abstract"
        )


        # ---------------------------------------------------------
        # ABSTRACT
        # ---------------------------------------------------------

        if abstract is not None:

            texto_abstract = " ".join(
                abstract.itertext()
            )

        else:

            texto_abstract = ""


        # ---------------------------------------------------------
        # TITLE
        # ---------------------------------------------------------

        texto_titulo = (

            titulo.text

            if titulo is not None
            and titulo.text

            else ""
        )


        # ---------------------------------------------------------
        # CLASSIFICATION
        # ---------------------------------------------------------

        (

            pontuacao,

            categoria_dominante,

            pontos_por_categoria,

            termos_detectados,

            tags_microorganismos,

            tags_produtos,

            tags_sustentabilidade

        ) = classificar_relevancia(

            texto_titulo,

            texto_abstract
        )


        # ---------------------------------------------------------
        # CATEGORY SCORES
        # ---------------------------------------------------------

        scores_texto = " | ".join(

            f"{categoria}:{pontos}"

            for categoria, pontos
            in pontos_por_categoria.items()

            if pontos > 0
        )


        # ---------------------------------------------------------
        # TAGS
        # ---------------------------------------------------------

        microorganismos_texto = ", ".join(
            tags_microorganismos
        )


        produtos_texto = ", ".join(
            tags_produtos
        )


        sustentabilidade_texto = ", ".join(
            tags_sustentabilidade
        )


        termos_texto = ", ".join(
            termos_detectados
        )


        # ---------------------------------------------------------
        # WRITE CSV
        # ---------------------------------------------------------

        escritor.writerow([


            numero.text
            if numero is not None
            else "",


            pais.text
            if pais is not None
            else "",


            tipo.text
            if tipo is not None
            else "",


            applicante.text
            if applicante is not None
            else "",


            data.text
            if data is not None
            else "",


            texto_titulo,


            texto_abstract,


            query,


            pontuacao,


            categoria_dominante,


            scores_texto,


            termos_texto,


            microorganismos_texto,


            produtos_texto,


            sustentabilidade_texto
        ])


# =====================================================================
# 16. FINAL REPORT
# =====================================================================

print()

print(
    "=========================================="
)

print(
    "BIOPATENT RADAR - FINALIZADO"
)

print(
    "=========================================="
)

print()

print(
    "Número de consultas:",
    len(queries)
)

print(

    "Resultados brutos:",

    len(todas_publicacoes)
)

print(

    "Patentes únicas:",

    len(publicacoes_unicas)
)

print()

print(
    "Distribuição final:"
)

print()


for categoria, quantidade in (
    resumo_categorias.items()
):

    print(
        "-",
        categoria,
        ":",
        quantidade
    )


print(
    "- Unclassified:",
    sem_classificacao
)

print()

print(
    "Arquivo patentes.csv criado!"
)

print()