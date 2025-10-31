# askPhysics - Semantic Search for Plasma Physics Literature

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![React 18](https://img.shields.io/badge/react-18-blue.svg)](https://reactjs.org/)

A semantic search system for plasma physics literature that combines **natural language processing** with **knowledge graphs** to enable intuitive queries like "Show me papers about electron density between 10^17 and 10^18 m^-3".

## 🌟 Features

### Natural Language Queries
- **Plain English input**: "Find research on plasma temperature in tokamaks"
- **Unit-aware search**: Automatically normalizes eV, keV, m^-3, cm^-3
- **Range queries**: "temperature between 1 and 10 keV"
- **Temporal filters**: "recent papers on electron density"

### Semantic Knowledge Graph
- **RDF-based ontology** for plasma physics concepts
- **SPARQL backend** for complex queries
- **Apache Jena Fuseki** triple store
- **547 triples** covering 100 research papers

### LLM Integration
- **Current**: GPT-4o-mini for parameter extraction
- **Roadmap**: Migration to QLoRA fine-tuned open-source model for complete platform independence
- Translates natural language → structured parameters
- **Fallback regex parsing** when LLM unavailable
- Dynamic SPARQL query generation

### Full-Stack Application
- **React + TypeScript** frontend with modern UI
- **FastAPI** backend with auto-generated API docs
- **RESTful API** for easy integration
- **Firebase Analytics** support (optional)

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- Java 11+ (for Fuseki)
- OpenAI API key (optional, for NLP features)

### Installation

```bash
# Clone the repository
git clone https://github.com/subodhkhanger/askPhysics.git
cd askPhysics

# Install backend dependencies
cd backend
pip install -r requirements.txt

# Install frontend dependencies
cd ../frontend
npm install

# Start the system
cd ..
./start_demo.sh
```

See [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md) for detailed instructions.

## 📖 Usage

### Via Web Interface

1. Start the application: `./start_demo.sh`
2. Open browser: `http://localhost:3000`
3. Try these example queries:
   - "Show me papers about electron density"
   - "plasma temperature between 1 and 10 keV"
   - "recent research on low-temperature plasmas"

### Via API

```bash
# Natural language query
curl -X POST http://localhost:8000/query/natural-language \
  -H "Content-Type: application/json" \
  -d '{"query": "electron density 10^17 m^-3", "limit": 10}'

# Direct SPARQL
curl "http://localhost:8000/papers?limit=20"

# Temperature range
curl "http://localhost:8000/temperatures?min_temp=1.0&max_temp=10.0"
```

API documentation: `http://localhost:8000/docs`

## 🏗 Architecture

### Current Architecture
```
┌─────────────────┐
│   Frontend      │  React + TypeScript
│   (Port 3000)   │  Natural language input
└────────┬────────┘
         │
         v
┌─────────────────┐
│   Backend       │  FastAPI + Python
│   (Port 8000)   │  NLP + SPARQL generation
└────────┬────────┘
         │
         ├─> OpenAI GPT-4o-mini (parameter extraction)
         │
         v
┌─────────────────┐
│   Fuseki        │  Apache Jena Fuseki
│   (Port 3030)   │  RDF triple store
└─────────────────┘
         │
         v
   Knowledge Graph
   (547 triples)
```

### Future Architecture (Platform Independent)
```
┌─────────────────┐
│   Frontend      │  React + TypeScript
│   (Port 3000)   │  Natural language input
└────────┬────────┘
         │
         v
┌─────────────────┐
│   Backend       │  FastAPI + Python
│   (Port 8000)   │  NLP + SPARQL generation
└────────┬────────┘
         │
         ├─> QLoRA Fine-tuned OSS Model (Local)
         │   • Llama 3 / Mistral / Phi-3
         │   • 4-bit quantization
         │   • Physics domain specialized
         │   • No external API dependencies
         │
         v
┌─────────────────┐
│   Fuseki        │  Apache Jena Fuseki
│   (Port 3030)   │  RDF triple store
└─────────────────┘
         │
         v
   Knowledge Graph
   (547 triples)
```

**Platform Independence Benefits**:
- ✅ No external API costs or rate limits
- ✅ Complete data privacy and control
- ✅ Customizable for domain-specific physics terminology
- ✅ Deployable in air-gapped or restricted environments
- ✅ Lower latency with local inference

## 🔬 Example Queries

### Simple Keyword Search
```
"papers about electron density"
→ Returns papers containing "electron density"
```

### Unit-Aware Range Query
```
"temperature between 1 and 10 keV"
→ Finds papers with temp measurements in that range
→ Automatically normalizes eV → keV
```

### Scientific Notation
```
"density 10^17 m^-3"
→ Handles scientific notation
→ Normalizes cm^-3 → m^-3
```

### Combined Constraints
```
"recent papers on plasma temperature 1-5 keV in tokamaks"
→ Temporal: last 2 years
→ Parameter: temperature 1-5 keV
→ Keywords: plasma, tokamaks
```

See [QUERY_EXAMPLES.md](QUERY_EXAMPLES.md) for more examples.

## 📊 Knowledge Graph

The system includes:

- **100 plasma physics papers** from arXiv
- **Temperature measurements** (keV normalized)
- **Density measurements** (m^-3 normalized)
- **Paper metadata** (title, authors, abstract, DOI)
- **Custom ontology** for plasma physics concepts

### Ontology Classes

- `Paper` - Scientific publications
- `Measurement` - Experimental measurements
- `Temperature` - Temperature parameters
- `Density` - Density parameters

See [KNOWLEDGE_GRAPH_PIPELINE.md](KNOWLEDGE_GRAPH_PIPELINE.md) for details.

## 🛠 Technology Stack

| Component | Technology |
|-----------|-----------|
| **Frontend** | React 18, TypeScript, Tailwind CSS |
| **Backend** | FastAPI, Python 3.9+, Pydantic |
| **Knowledge Graph** | Apache Jena Fuseki, RDF/Turtle |
| **NLP (Current)** | OpenAI GPT-4o-mini, Regex fallback |
| **NLP (Roadmap)** | QLoRA fine-tuned OSS model (Llama/Mistral/Phi-3) |
| **API** | REST, OpenAPI/Swagger |
| **Deployment** | Docker, Railway.app |

## 📚 Documentation

- **[INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md)** - Setup instructions
- **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - Production deployment
- **[UNIFIED_QUERY_GUIDE.md](UNIFIED_QUERY_GUIDE.md)** - Technical architecture
- **[KNOWLEDGE_GRAPH_PIPELINE.md](KNOWLEDGE_GRAPH_PIPELINE.md)** - Data processing
- **[FIREBASE_SETUP.md](FIREBASE_SETUP.md)** - Analytics configuration
- **[QUERY_EXAMPLES.md](QUERY_EXAMPLES.md)** - Query patterns
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Contribution guidelines

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Areas for Contribution

- 🔍 **Search improvements** - Better NLP, more query types
- 🤖 **QLoRA Model Development** - Help build and fine-tune the open-source NLP model
- 📊 **Knowledge graph expansion** - More papers, more parameters
- 🎨 **UI/UX** - Design improvements, visualizations
- 🧪 **Testing** - Unit tests, integration tests
- 📖 **Documentation** - Examples, tutorials, translations

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **ArXiv** for plasma physics papers
- **Apache Jena** for Fuseki triple store
- **OpenAI** for GPT models
- **FastAPI** and **React** communities

## 🔗 Links

- **Live Demo**: [https://frontend-production-585a.up.railway.app](https://frontend-production-585a.up.railway.app)
- **API Docs**: [https://askphysics-production.up.railway.app/docs](https://askphysics-production.up.railway.app/docs)
- **GitHub**: [https://github.com/subodhkhanger/askPhysics](https://github.com/subodhkhanger/askPhysics)

## 📧 Contact

For questions or suggestions, please [open an issue](https://github.com/subodhkhanger/askPhysics/issues).

---

