# ScholarGraph AI

ScholarGraph AI is an AI-powered research paper assistant designed to help students and researchers analyze, understand, and explore scientific literature efficiently.

The platform processes research papers in PDF format, extracts structured scientific knowledge, and combines Retrieval-Augmented Generation (RAG) with Knowledge-Augmented Generation (KAG) techniques to provide intelligent question answering, semantic search, paper comparison, literature review generation, and citation-aware reasoning.

Unlike traditional “chat with PDF” systems, the platform transforms scientific papers into interconnected knowledge representations using embeddings, metadata extraction, and knowledge graphs.

The system aims to reduce the time required for literature review and improve research accessibility through AI-powered scientific understanding.

### Project Architecture

#### Design system Architecture
```
ScholarGraph AI
│
├── Frontend
│   ├── PDF upload page
│   ├── Paper dashboard
│   ├── Chat with paper
│   ├── Summary viewer
│   └── Knowledge graph viewer
│
├── Backend API
│   ├── Upload API
│   ├── Paper analysis API
│   ├── Chat API
│   ├── Search API
│   └── Graph API
│
├── Paper Processing Pipeline
│   ├── PDF extraction
│   ├── Text cleaning
│   ├── Section detection
│   ├── Metadata extraction
│   ├── Chunking
│   └── Citation extraction
│
├── RAG Engine
│   ├── Embeddings
│   ├── Vector search
│   ├── Chunk retrieval
│   └── Answer generation
│
├── KAG Engine
│   ├── Entity extraction
│   ├── Relationship extraction
│   ├── Knowledge graph construction
│   └── Graph reasoning
│
└── Databases
    ├── PostgreSQL
    ├── Vector DB
    └── Neo4j
```

#### Data flow

1. User uploads PDF
2. Backend saves PDF
3. PDF text is extracted
4. Text is cleaned
5. Sections are detected
6. Paper metadata is extracted
7. Text is split into chunks
8. Chunks are embedded
9. Vectors are stored in Vector DB
10. Entities and relationships are extracted
11. Knowledge graph is stored in Neo4j
12. User asks question
13. System retrieves chunks + graph facts
14. LLM generates grounded answer

