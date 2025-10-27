# Product Requirements Document: Plasma Physics Literature Search Prototype

## Executive Summary

Build a proof-of-concept system demonstrating parameter-aware literature search for plasma physics research. This prototype implements three key technical approaches: LoRA-adapted LLM for domain understanding, LLM-to-SPARQL translation for structured queries, and unit-aware physical parameter searching.

**Timeline**: 2-3 weeks  
**Primary Goal**: Demonstrate technical feasibility to support job application for TIB FID Physik Research Software Engineer position  
**Success Criteria**: Working demo that handles temperature/density range queries on small corpus

---

## Background & Context

### Problem Statement
Current academic search tools (Google Scholar, Web of Science) cannot handle physics parameter range queries. Researchers cannot search for "experiments with plasma temperature between 1-10 keV" because:
- Keyword search fails to understand numerical constraints
- No unit conversion (eV ↔ K ↔ keV)
- Cannot extract and compare numerical values from papers

### Opportunity
TIB's FID Physik project (starting Jan 2026) aims to solve this for plasma physics. Building a prototype demonstrates:
1. **Technical competence** in the exact technologies they need
2. **Domain understanding** of plasma physics information needs
3. **Initiative and practical skills** beyond theoretical knowledge

### Target Audience
- **Primary**: TIB hiring team (Dr. Holger Israel, Dr. Allard Oelen)
- **Secondary**: Physics research community (for portfolio/blog)

---

## Product Vision

A web application where plasma physicists can query:
- "Find papers about electron temperatures between 1-5 keV"
- "Show experiments with density above 5×10¹⁹ m⁻³"
- "Which tokamaks achieved temperatures over 10 keV?"

The system returns:
- Synthesized natural language answer
- Relevant papers with extracted parameters
- Transparent SPARQL query showing how results were found

---

## Core Features (MVP)

### Feature 1: Parameter Extraction from Papers
**Description**: Extract temperature and density values from arXiv plasma physics papers

**User Story**: As a system, I need to build a knowledge base of papers with their experimental parameters so queries can be executed.

**Acceptance Criteria**:
- [ ] Collect 100-200 papers from arXiv physics.plasm-ph category
- [ ] Extract electron temperature (Te) values and units (eV, keV, K)
- [ ] Extract density (ne) values and units (m⁻³, cm⁻³)
- [ ] Store extracted data in structured format (JSON/CSV)
- [ ] Accuracy: 70%+ correct extraction on manual validation sample

**Technical Notes**:
- Use arXiv API for data collection
- Combine regex patterns + GPT-3.5/4 for extraction
- Focus on abstracts first (faster, cheaper than full text)

---

### Feature 2: Knowledge Graph Construction
**Description**: Build RDF knowledge graph with papers as nodes and parameters as properties

**User Story**: As a system, I need structured data storage to enable SPARQL queries over numerical parameter ranges.

**Acceptance Criteria**:
- [ ] Apache Jena Fuseki running locally (Docker)
- [ ] Custom plasma physics ontology defined (temperature, density properties)
- [ ] All extracted papers loaded as RDF triples
- [ ] Sample SPARQL queries work (e.g., "SELECT papers WHERE temp > 5 keV")
- [ ] Unit metadata included (using QUDT vocabulary)

**Technical Notes**:
```turtle
# Example structure
plasma:Paper_123 a plasma:Experiment ;
    dc:title "High confinement in DIII-D" ;
    plasma:hasTemperature [
        qudt:numericValue 5.2 ;
        qudt:unit unit:KeV
    ] .
```

**Dependencies**: Feature 1 completed

---

### Feature 3: LoRA Fine-tuning for Physics Domain
**Description**: Fine-tune 7B LLM with LoRA on physics-specific tasks

**User Story**: As a system, I need domain-specific language understanding to accurately interpret plasma physics queries and generate SPARQL.

**Acceptance Criteria**:
- [ ] Training dataset created (500+ examples):
  - Parameter extraction: "Extract temperature from: [text]"
  - Unit conversion: "Convert 3 eV to Kelvin"
  - Query understanding: "What parameters does this query need?"
- [ ] LoRA adapters trained (Llama-2-7B or Mistral-7B base)
- [ ] Inference working with merged model
- [ ] Qualitative improvement vs base model on test cases

**Technical Notes**:
- Use HuggingFace PEFT library
- LoRA config: r=16, alpha=32, target modules q_proj/v_proj
- Training: ~6-12 hours on single GPU
- Can skip this feature for 1-week version (use GPT-3.5-turbo API instead)

**Optional for MVP**: Can defer to Phase 2 if time-constrained

---

### Feature 4: LLM-to-SPARQL Translation
**Description**: Convert natural language queries to executable SPARQL

**User Story**: As a user, I want to ask questions in plain English and get results without learning SPARQL syntax.

**Acceptance Criteria**:
- [ ] Prompt engineering: Schema documentation + few-shot examples
- [ ] Handle basic query types:
  - Simple range: "temperature > 5 keV"
  - Bounded range: "density between 1e19 and 1e20 m⁻³"
  - Combined conditions: "temperature > 5 keV AND density < 1e20"
- [ ] Generated SPARQL executes without errors 80%+ of time
- [ ] Validation layer catches syntax errors before execution

**Technical Notes**:
```python
def generate_sparql(query: str, llm) -> str:
    prompt = f"""Convert to SPARQL. Schema: [ontology]
    
Examples:
Query: "Find papers with temperature above 5 keV"
SPARQL: PREFIX plasma: <...>
SELECT ?paper ?temp WHERE {{
  ?paper plasma:hasTemperature ?tempNode .
  ?tempNode qudt:numericValue ?temp .
  FILTER(?temp > 5)
}}

Query: {query}
SPARQL:"""
    return llm.generate(prompt)
```

**Dependencies**: Features 2, 3 completed

---

### Feature 5: Unit Conversion System
**Description**: Normalize all units to canonical form for comparison

**User Story**: As a system, I need to compare temperatures in eV, keV, and Kelvin interchangeably.

**Acceptance Criteria**:
- [ ] Conversion factors defined for common units:
  - Temperature: eV ↔ keV ↔ K (1 eV = 11,604.52 K)
  - Density: m⁻³ ↔ cm⁻³ (1 cm⁻³ = 10⁶ m⁻³)
- [ ] Query preprocessing: "10 keV" → "10000 eV" before SPARQL generation
- [ ] Display formatting: Results shown in user's requested unit
- [ ] Integration with QUDT vocabulary in RDF

**Technical Notes**:
```python
CONVERSIONS = {
    'eV_to_K': 11604.52,
    'keV_to_eV': 1000,
    'cm3_to_m3': 1e6
}

def normalize_temperature(value, unit):
    if unit == 'keV':
        return value * 1000  # to eV
    elif unit == 'K':
        return value / 11604.52  # to eV
    return value
```

**Dependencies**: Feature 4 completed

---

### Feature 6: Web Interface
**Description**: Simple, clean UI for querying and viewing results

**User Story**: As a user, I want to type natural language queries and see matching papers with their parameters.

**Acceptance Criteria**:
- [ ] Search input box with example queries
- [ ] Results display:
  - Synthesized answer (2-3 sentences)
  - List of matching papers (title, authors, parameters)
  - Expandable "Show SPARQL query" section (for transparency)
- [ ] Loading states during query processing
- [ ] Error handling with helpful messages
- [ ] Responsive design (works on mobile)

**UI Wireframe**:
```
┌─────────────────────────────────────────┐
│  Plasma Physics Literature Search       │
├─────────────────────────────────────────┤
│  [Find papers with temperature > 5 keV] │
│                              [Search]    │
├─────────────────────────────────────────┤
│  Results (3 papers found):               │
│                                          │
│  📄 High confinement in DIII-D           │
│     Temperature: 5.2 keV                 │
│     Density: 6.7×10¹⁹ m⁻³               │
│     Authors: Smith et al.                │
│                                          │
│  📄 Plasma heating experiments...        │
│     Temperature: 7.1 keV                 │
│     ...                                  │
│                                          │
│  [▼ Show generated SPARQL query]         │
└─────────────────────────────────────────┘
```

**Technology**:
- **Option A** (Full stack): React frontend + FastAPI backend
- **Option B** (Rapid): Streamlit single-file app
- **Recommendation**: Start with Streamlit, migrate to React if time permits

**Dependencies**: Features 1-5 completed

---

## Technical Architecture

### High-Level Flow
```
User Query 
  ↓
[1] Query Understanding (LoRA LLM)
  ↓
[2] SPARQL Generation (Prompt + LLM)
  ↓
[3] Unit Normalization
  ↓
[4] Query Execution (Fuseki)
  ↓
[5] Result Synthesis (LLM)
  ↓
Display to User
```

### Component Diagram
```
┌──────────────────────────────────────────────┐
│              Frontend (React/Streamlit)       │
└────────────────┬─────────────────────────────┘
                 │ HTTP/REST
┌────────────────▼─────────────────────────────┐
│           FastAPI Backend                     │
│  ┌──────────────────────────────────────┐   │
│  │  Query Processing Module              │   │
│  │  - LoRA Model (Llama-2-7B)           │   │
│  │  - SPARQL Generator                   │   │
│  │  - Unit Converter                     │   │
│  └──────────────────────────────────────┘   │
└────────────────┬─────────────────────────────┘
                 │ SPARQL Protocol
┌────────────────▼─────────────────────────────┐
│     Apache Jena Fuseki (Triple Store)        │
│     - Plasma Physics Ontology                │
│     - Paper Metadata (RDF)                   │
│     - Extracted Parameters                   │
└──────────────────────────────────────────────┘
```

### Data Models

#### Paper Metadata
```json
{
  "id": "arxiv_2401.12345",
  "title": "High confinement plasma experiments",
  "authors": ["Smith, J.", "Doe, A."],
  "abstract": "We report electron temperatures...",
  "published_date": "2024-01-15",
  "arxiv_url": "https://arxiv.org/abs/2401.12345"
}
```

#### Extracted Parameters
```json
{
  "paper_id": "arxiv_2401.12345",
  "parameters": [
    {
      "type": "electron_temperature",
      "value": 5.2,
      "unit": "keV",
      "context": "peak electron temperature of 5.2 keV"
    },
    {
      "type": "density",
      "value": 6.7e19,
      "unit": "m^-3",
      "context": "line-averaged density 6.7×10¹⁹ m⁻³"
    }
  ]
}
```

#### RDF Triple Structure
```turtle
@prefix plasma: <http://plasma-physics.org/ontology#> .
@prefix qudt: <http://qudt.org/schema/qudt#> .

plasma:Paper_2401_12345 
    a plasma:Experiment ;
    dc:title "High confinement plasma experiments" ;
    dc:creator "Smith, J." ;
    plasma:hasTemperature [
        a plasma:ElectronTemperature ;
        qudt:numericValue 5.2 ;
        qudt:unit unit:KeV
    ] ;
    plasma:hasDensity [
        a plasma:ElectronDensity ;
        qudt:numericValue 6.7e19 ;
        qudt:unit unit:PER-M3
    ] .
```

---

## Tech Stack

### Core Technologies
| Component | Technology | Rationale |
|-----------|-----------|-----------|
| **LLM Base** | Llama-2-7B or Mistral-7B | Open source, good performance, 16GB VRAM fits single GPU |
| **Fine-tuning** | HuggingFace PEFT (LoRA) | Industry standard, well-documented, efficient |
| **Triple Store** | Apache Jena Fuseki | Easy setup, good SPARQL support, Docker available |
| **Backend** | FastAPI (Python) | Fast, async, automatic API docs, typed |
| **Frontend** | Streamlit (MVP) → React | Streamlit for speed, React for production polish |
| **LLM Serving** | Transformers or vLLM | Transformers simple, vLLM faster for production |

### Development Tools
- **Version Control**: Git + GitHub
- **Environment**: Python 3.10+, Node.js 18+ (if using React)
- **Package Management**: pip + poetry for Python, npm for JavaScript
- **Containers**: Docker + Docker Compose
- **Testing**: pytest (backend), Jest (frontend)
- **CI/CD**: GitHub Actions (optional for demo)

### External APIs & Services
- **arXiv API**: Paper collection (free, no auth required)
- **OpenAI API**: Backup for LLM if local training fails (requires API key)
- **HuggingFace Hub**: Model download (free)

---

## Development Phases

### Phase 1: Foundation (Days 1-4)
**Goal**: Data pipeline working, parameters extracted

**Tasks**:
1. Setup project structure (repos, Docker configs)
2. Implement arXiv scraper (100-200 papers)
3. Build parameter extraction pipeline (regex + GPT-3.5)
4. Validate extraction accuracy (manual spot-checks)
5. Export to JSON

**Deliverables**:
- `data/papers.json` with 100+ papers
- `data/extracted_params.json` with temperature/density values
- Jupyter notebook showing extraction process

---

### Phase 2: Knowledge Graph (Days 5-7)
**Goal**: SPARQL queries working over structured data

**Tasks**:
1. Setup Jena Fuseki (Docker)
2. Define plasma physics ontology (Turtle format)
3. Write RDF conversion script
4. Load data into triple store
5. Test sample SPARQL queries

**Deliverables**:
- `ontology/plasma_physics.ttl`
- `scripts/load_data.py`
- Docker compose with Fuseki running
- 5 example SPARQL queries that work

---

### Phase 3: LLM Integration (Days 8-12)
**Goal**: Natural language → SPARQL working

**Tasks**:
1. Create training dataset (500 examples)
2. Fine-tune with LoRA (if time) OR use GPT-3.5 API
3. Implement SPARQL generation with prompts
4. Add unit conversion logic
5. Test query accuracy

**Deliverables**:
- `models/lora-adapter/` (if trained)
- `backend/sparql_generator.py`
- `backend/unit_converter.py`
- Test suite: 20 queries with expected outputs

---

### Phase 4: Application Layer (Days 13-17)
**Goal**: Working web interface

**Tasks**:
1. Build FastAPI backend with endpoints
2. Create Streamlit frontend
3. Integrate all components (end-to-end flow)
4. Add error handling and validation
5. Polish UI/UX

**Deliverables**:
- `backend/app.py` (FastAPI server)
- `frontend/app.py` (Streamlit) or `frontend/src/` (React)
- Working demo accessible at localhost

---

### Phase 5: Polish & Documentation (Days 18-21)
**Goal**: Portfolio-ready project

**Tasks**:
1. Write comprehensive README
2. Add architecture diagrams
3. Create demo video (2-3 minutes)
4. Write technical blog post
5. Deploy demo (HuggingFace Spaces or similar)
6. Prepare presentation slides

**Deliverables**:
- README with setup instructions
- `docs/` folder with architecture, API docs
- Demo video on YouTube/Loom
- Blog post draft
- Live demo URL

---

## Success Metrics

### Technical Metrics
- **Parameter Extraction Accuracy**: ≥70% correct on validation set
- **SPARQL Generation Success**: ≥80% queries execute without errors
- **Query Response Time**: <5 seconds end-to-end
- **System Uptime**: Demo runs without crashes for 1 hour continuous use

### Portfolio Metrics
- **GitHub Stars**: Goal 10+ (share in relevant communities)
- **Blog Post Views**: Goal 100+ (share on LinkedIn, Reddit r/MachineLearning)
- **Demo Engagement**: 5+ people try the live demo

### Application Metrics
- **Hiring Team Feedback**: Mentioned positively in interview
- **Differentiator**: Only candidate with working prototype
- **Technical Credibility**: Demonstrates all three required approaches

---

## Risk Management

### Risk 1: LoRA Training Fails / Takes Too Long
**Probability**: Medium  
**Impact**: Medium  
**Mitigation**: 
- Use OpenAI GPT-3.5-turbo API as fallback
- Still demonstrates understanding of approach
- Can discuss what you would do differently with more time

### Risk 2: Parameter Extraction Accuracy Too Low
**Probability**: Medium  
**Impact**: High (breaks everything downstream)  
**Mitigation**:
- Start with manual curation of 50 papers as gold standard
- Use GPT-4 for extraction (higher accuracy than GPT-3.5)
- Focus on papers with clear parameter reporting in abstracts

### Risk 3: SPARQL Generation Complexity Underestimated
**Probability**: Low  
**Impact**: High  
**Mitigation**:
- Start with very simple queries (single parameter, single constraint)
- Gradually add complexity
- Few-shot prompting with 10+ examples handles most cases

### Risk 4: Time Constraints (Only 1 Week Available)
**Probability**: Medium  
**Impact**: Medium  
**Mitigation**:
- **Simplified Version**: Skip LoRA training, use GPT-3.5, only 50 papers, Streamlit UI
- **Core Demo**: Focus on Feature 1, 2, 4, 6 (skip LoRA and advanced unit conversion)
- Still impressive and demonstrates understanding

### Risk 5: Hardware Limitations (No GPU Access)
**Probability**: Low  
**Impact**: High  
**Mitigation**:
- Use Google Colab Pro ($10/month, includes GPU)
- Use Lambda Labs (cloud GPU rental, ~$0.50/hour)
- Worst case: Use API-only approach (no local model)

---

## Out of Scope (Future Enhancements)

These features are explicitly NOT included in MVP but could be mentioned as "future work":

1. **Full-text extraction** (abstract-only for MVP)
2. **Multiple parameter types** (only temperature + density for MVP)
3. **Equation understanding** (would require specialized parsing)
4. **User authentication** (public demo, no login)
5. **Production deployment** (local/demo hosting only)
6. **Multi-language support** (English only)
7. **Historical corpus** (only recent papers, 2020-2025)
8. **Advanced visualizations** (simple table display only)
9. **API rate limiting** (not needed for demo)
10. **Comprehensive testing** (manual QA sufficient for prototype)

---

## Appendix: Example Queries

### Basic Queries (Must Work)
1. "Find papers with electron temperature above 5 keV"
2. "Show experiments with density between 1e19 and 1e20 per cubic meter"
3. "Which papers report temperatures over 10000 electron volts?"

### Stretch Queries (Nice to Have)
4. "Find tokamak experiments with high temperature and high density"
5. "Show me papers about DIII-D with temperature greater than 5 keV"
6. "What's the highest electron temperature reported in the dataset?"

### Example Expected Outputs

**Query**: "Find papers with electron temperature above 5 keV"

**Generated SPARQL**:
```sparql
PREFIX plasma: <http://plasma-physics.org/ontology#>
PREFIX qudt: <http://qudt.org/schema/qudt#>

SELECT ?paper ?title ?temp WHERE {
  ?paper a plasma:Experiment ;
         dc:title ?title ;
         plasma:hasTemperature ?tempNode .
  ?tempNode qudt:numericValue ?temp ;
            qudt:unit unit:KeV .
  FILTER(?temp > 5)
}
```

**Answer**:
"Found 3 papers with electron temperatures above 5 keV. The highest temperature was 7.2 keV reported in experiments on the DIII-D tokamak by Smith et al. (2024)."

**Papers**:
1. "High confinement plasma experiments on DIII-D" - Smith et al. - Te: 5.2 keV
2. "Advanced scenarios in tokamak plasmas" - Jones et al. - Te: 6.8 keV  
3. "Record temperatures in fusion research" - Wilson et al. - Te: 7.2 keV

---

## Appendix: Resource Links

### Technical Documentation
- **SPARQL Tutorial**: https://www.w3.org/TR/sparql11-query/
- **QUDT Ontology**: http://www.qudt.org/
- **LoRA Paper**: https://arxiv.org/abs/2106.09685
- **PEFT Library**: https://huggingface.co/docs/peft/

### Similar Projects (Inspiration)
- **ORKG Ask**: https://ask.orkg.org/
- **INSPIRE-HEP**: https://inspirehep.net/
- **Bio-SODA** (NL to SPARQL): https://chat.expasy.org/

### Development Resources
- **arXiv API**: https://info.arxiv.org/help/api/index.html
- **Jena Fuseki Docker**: https://hub.docker.com/r/stain/jena-fuseki
- **HuggingFace Models**: https://huggingface.co/models

### Deployment Options
- **HuggingFace Spaces**: https://huggingface.co/spaces
- **Streamlit Cloud**: https://streamlit.io/cloud
- **Railway**: https://railway.app/

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2024-10-26 | Subodh Khanger | Initial PRD |

---

## Approval

**Product Owner**: Subodh Khanger  
**Technical Lead**: Subodh Khanger  
**Timeline**: Oct 26 - Nov 15, 2024  
**Status**: ✅ Ready for Development
