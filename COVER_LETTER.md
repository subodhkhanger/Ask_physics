# Cover Letter - Physics Ask Position at TIB FID Physik

Dear Hiring Manager,

I am writing to express my strong interest in the **Physics Ask** position at TIB FID Physik. To demonstrate my capability to deliver on the requirements outlined in your job posting, I have built a **working prototype** that directly addresses the core technical challenges of this role. The prototype is deployed and accessible at:

**Live Demo:** https://frontend-production-585a.up.railway.app
**Backend API:** https://askphysics-production.up.railway.app
**Source Code:** https://github.com/subodhkhanger/askPhysics

## Alignment with Your Requirements

### 1. Natural Language to SPARQL Translation (Your Task #2)

**What you asked for:** *"Leveraging the LLM to translate user input into SPARQL queries, facilitating the retrieval of results from pre-existing knowledge graphs such as the ORKG."*

**What I built:** I implemented a complete natural language query system that:
- Uses GPT-4o-mini to parse natural language queries into structured parameters
- Dynamically generates SPARQL queries based on parsed intent
- Successfully retrieves results from an Apache Jena Fuseki knowledge graph
- Handles complex queries like: *"Show me recent research on electron density in low-temperature plasmas between 10^16 and 10^18 m^-3"*

**Technical implementation:**
```python
# backend/nlp_query_processor.py - Extracts parameters from natural language
# backend/query_builder.py - Dynamically builds SPARQL queries
# backend/main.py - REST API endpoint: /query/natural-language
```

The system successfully translates natural language → structured parameters → SPARQL → knowledge graph results, demonstrating the exact workflow you described.

### 2. Full-Text Search for Physical Quantities (Your Task #3)

**What you asked for:** *"Implementing a full text search for ranges in physical (unit-carrying) quantities, by adapting a modelling paradigm for semantic metadata templates."*

**What I built:** I implemented comprehensive support for:
- **Temperature ranges** with unit normalization (eV, keV → normalized to keV)
- **Density ranges** with scientific notation handling (10^16 - 10^18 m^-3 → normalized to m^-3)
- **Temporal constraints** ("recent" papers = last 2 years)
- **Unit-aware filtering** in SPARQL queries with normalized values

**Example queries handled:**
- Temperature: 1-10 keV, 5 eV, 0.5-2 keV
- Density: 1e16 m^-3, 10^17-10^19 m^-3
- Combined: "plasma temperature 1-5 keV AND density 10^17 m^-3"

**Technical approach:**
```python
# Unit normalization pipeline
def _normalize_parameter(self, param: ParameterRange):
    if param.unit in ['eV', 'keV']:
        # Convert to keV
    if param.unit in ['m^-3', 'cm^-3']:
        # Convert to m^-3
```

This demonstrates my understanding of semantic metadata templates and unit-aware search, which is central to physics literature discovery.

### 3. Semantic Web Technologies & Knowledge Graphs

**What you asked for:** *"Good command of Semantic Web technologies (e.g. RDF and SPARQL), conceptual modelling with ontologies..."*

**What I built:**
- **RDF Ontology** (`ontology/plasma_physics.ttl`): Custom plasma physics vocabulary with classes for Temperature, Density, Measurement, Paper
- **Knowledge Graph** with 547 triples: 100 papers with 193 ontology triples + 354 data triples
- **SPARQL Queries**: Complex queries with FILTER, OPTIONAL, ORDER BY, aggregations
- **Apache Jena Fuseki**: Production deployment with proper dataset configuration
- **REST API** exposing SPARQL results as JSON

**Example SPARQL query from the system:**
```sparql
PREFIX : <http://example.org/plasma#>
SELECT ?arxivId ?title ?value ?unit ?normTemp
WHERE {
  ?paper a :Paper ;
         :arxivId ?arxivId ;
         :title ?title ;
         :reports ?measurement .
  ?measurement :measuresParameter ?param .
  ?param a :Temperature ;
         :value ?value ;
         :unitString ?unit ;
         :normalizedValue ?normTemp .
  FILTER(?normTemp >= 1.0 && ?normTemp <= 10.0)
}
```

### 4. User-Facing Application Integration (Your Task #5)

**What you asked for:** *"Integrating these three strands of innovation into a user-facing application as part of the search and service portal."*

**What I built:** A complete full-stack application with:
- **Frontend**: React + TypeScript with modern UI (https://frontend-production-585a.up.railway.app)
- **Backend**: FastAPI with RESTful API (https://askphysics-production.up.railway.app)
- **Knowledge Graph**: Apache Jena Fuseki triple store
- **Natural Language Interface**: Unified search component for physicist end-users
- **API Documentation**: Auto-generated Swagger UI at /docs
- **Analytics**: Firebase integration for usage tracking (optional)

**User Experience:**
1. Physicist types: *"Show me papers about electron density in tokamaks"*
2. System parses query using LLM
3. Generates SPARQL with appropriate filters
4. Retrieves papers from knowledge graph
5. Displays results with metadata (title, authors, publication date, parameters)

### 5. Quality Assurance (Your Task #4)

**What I implemented:**
- **Comprehensive API testing** with health checks and connection monitoring
- **Error handling** with graceful fallbacks (LLM unavailable → regex parsing)
- **Logging and monitoring** for query performance and success rates
- **Data validation** using Pydantic models
- **CORS configuration** for secure cross-origin requests
- **Unit normalization validation** to ensure consistent results

## Technical Stack Demonstrating Your Required Skills

### Semantic Web Technologies:
- **RDF/Turtle**: Custom ontology modeling plasma physics domain
- **SPARQL**: Dynamic query generation with filters and aggregations
- **Apache Jena Fuseki**: Production knowledge graph deployment
- **Ontology Design**: Classes, properties, namespaces following best practices

### Natural Language Processing:
- **LLM Integration**: GPT-4o-mini for parameter extraction
- **Prompt Engineering**: Structured prompts for reliable parsing
- **Fallback Strategies**: Regex-based parsing when LLM unavailable
- **Intent Recognition**: Keywords, temporal, numerical, unit extraction

### Software Engineering:
- **Python**: FastAPI, Pydantic, asyncio, type hints
- **TypeScript/React**: Modern frontend with hooks, React Query, routing
- **REST API Design**: RESTful endpoints with OpenAPI documentation
- **DevOps**: Docker, Railway deployment, environment configuration
- **Version Control**: Git with structured commits and documentation

### Data Modeling:
- **Unit Normalization**: Converting between eV/keV, cm^-3/m^-3
- **Scientific Notation**: Handling 1e16, 10^17, powers of 10
- **Range Queries**: Min/max filtering with proper SPARQL syntax
- **Temporal Reasoning**: "Recent" → date calculations

## Why This Prototype Matters

This prototype demonstrates that I can:

1. **Build bridges between LLMs and Knowledge Graphs** - The core of your third task
2. **Work with semantic metadata** - Temperature/density as typed, unit-carrying entities
3. **Deploy production systems** - Not just code, but live, accessible applications
4. **Think like a physicist** - Understanding domain-specific needs (units, ranges, precision)
5. **Deliver quickly** - This was built as a demonstration of capability for this specific position

## What I Would Bring to TIB FID Physik

**Domain Knowledge:**
- Understanding of plasma physics parameters and typical research queries
- Appreciation for unit systems and measurement precision in physics
- Experience with scientific literature metadata (arXiv, DOIs, citations)

**Technical Expertise:**
- Proven ability to work with RDF, SPARQL, and knowledge graphs
- Experience integrating LLMs with structured semantic data
- Full-stack development skills for user-facing applications
- Quality assurance mindset with error handling and monitoring

**Research Orientation:**
- Documented implementation with comprehensive README files
- Clean, maintainable code with proper separation of concerns
- Willingness to explore new techniques (LoRA fine-tuning for Task #1)
- Open to contributing to the academic community through publications

## Specific Contributions I Can Make

### For Task #1 (LLM Adaptation):
While my prototype uses GPT-4o-mini via API, I have experience with:
- Fine-tuning transformers (familiar with LoRA, QLoRA techniques)
- Extended context windows for long-form physics papers
- Model evaluation and quality metrics
- I would be excited to adapt this to a custom-trained model for Physics Ask

### For Task #2 (Already Demonstrated):
My NL→SPARQL pipeline is production-ready and can be directly adapted for ORKG integration.

### For Task #3 (Already Demonstrated):
The unit-aware search with normalization is a working solution that handles the exact use case you described.

### For Task #4 (Quality Assurance):
I implemented logging, health checks, error handling, and monitoring - this mindset would carry into your quality assurance processes.

### For Task #5 (Integration):
The full-stack application demonstrates my ability to integrate backend services into a polished user experience.

## Closing

I built this prototype specifically to demonstrate my readiness for the Physics Ask position. Every feature directly maps to a requirement in your job posting. I didn't just read about these technologies - I implemented them in a working, deployed system.

I am eager to bring this experience to TIB FID Physik and contribute to making physics literature more accessible through semantic search and natural language interfaces. I would be thrilled to discuss how my prototype aligns with your vision for Physics Ask and how I can contribute to its success.

The live prototype is available for your review at any time. I'm happy to provide a demonstration or discuss any technical aspects in detail.

Thank you for considering my application. I look forward to the opportunity to contribute to this important project.

---

## Quick Links

- **Live Frontend:** https://frontend-production-585a.up.railway.app
- **API Docs:** https://askphysics-production.up.railway.app/docs
- **Source Code:** https://github.com/subodhkhanger/askPhysics
- **Demo Query:** Try "Show me papers about electron density between 1e17 and 1e18 m^-3"

---

**Technical Documentation:**
- `UNIFIED_QUERY_GUIDE.md` - Complete system architecture
- `FIREBASE_SETUP.md` - Analytics integration guide
- `DEPLOYMENT_GUIDE.md` - Production deployment instructions
- `KNOWLEDGE_GRAPH_PIPELINE.md` - Data flow and processing

**Contact:**
[Your Name]
[Your Email]
[Your Phone]
[LinkedIn Profile]
