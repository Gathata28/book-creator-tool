# Book Creator Tool - Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                     BOOK CREATOR TOOL                               │
│                 AI-Powered Coding Book Platform                     │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                         USER INTERFACES                              │
├─────────────────────────────────────────────────────────────────────┤
│  CLI Commands:                   │  Python API:                     │
│  • book-creator create           │  • from book_creator import *    │
│  • book-creator generate         │  • Programmatic access           │
│  • book-creator export           │  • Custom workflows              │
│  • book-creator check            │                                  │
│  • book-creator improve          │                                  │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          CORE MODELS                                 │
├─────────────────────────────────────────────────────────────────────┤
│  Book                                                               │
│  ├── metadata (title, author, description, etc.)                   │
│  └── Chapters[]                                                     │
│      ├── introduction, summary                                      │
│      └── Sections[]                                                 │
│          ├── content                                                │
│          ├── code_examples[]                                        │
│          └── exercises[]                                            │
│                                                                     │
│  • JSON serialization/deserialization                              │
│  • File save/load capabilities                                     │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
┌──────────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│    GENERATORS        │  │     EDITORS      │  │   FORMATTERS     │
├──────────────────────┤  ├──────────────────┤  ├──────────────────┤
│                      │  │                  │  │                  │
│ OutlineGenerator     │  │ GrammarChecker   │  │ HTMLFormatter    │
│ • AI book outlines   │  │ • Grammar check  │  │ • Responsive     │
│ • Chapter structure  │  │ • Style check    │  │ • Syntax HL      │
│ • Section planning   │  │ • Auto-fix       │  │                  │
│                      │  │ • Tech accuracy  │  │ PDFFormatter     │
│ ContentGenerator     │  │                  │  │ • Professional   │
│ • Chapter content    │  │ ContentImprover  │  │ • Layout         │
│ • Section content    │  │ • Clarity        │  │                  │
│ • Introductions      │  │ • Engagement     │  │ EPUBFormatter    │
│ • Summaries          │  │ • Conciseness    │  │ • E-reader       │
│                      │  │ • Add examples   │  │ • Standards      │
│ CodeGenerator        │  │ • Transitions    │  │                  │
│ • Code examples      │  │                  │  │ MarkdownFormatter│
│ • Explanations       │  │                  │  │ • Portable       │
│ • Exercises          │  │                  │  │ • Editable       │
│ • Multi-language     │  │                  │  │                  │
│                      │  │                  │  │                  │
└──────────────────────┘  └──────────────────┘  └──────────────────┘
            │                      │                      │
            └──────────────────────┼──────────────────────┘
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        UTILITY LAYER                                 │
├─────────────────────────────────────────────────────────────────────┤
│  LLM Client                                                         │
│  ├── OpenAI Integration (GPT-4, GPT-3.5-turbo)                     │
│  ├── Anthropic Integration (Claude 3 models)                       │
│  ├── Unified API interface                                         │
│  └── Configuration management                                       │
│                                                                     │
│  LLM Config                                                         │
│  ├── API key management (from environment)                         │
│  ├── Model selection                                               │
│  ├── Temperature & token settings                                  │
│  └── Provider switching                                            │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    EXTERNAL SERVICES                                 │
├─────────────────────────────────────────────────────────────────────┤
│  OpenAI API              │  Anthropic API                          │
│  • GPT-4                 │  • Claude 3 Opus                        │
│  • GPT-3.5-turbo         │  • Claude 3 Sonnet                      │
│                          │  • Claude 3 Haiku                       │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                        DATA FLOW                                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  1. CREATE OUTLINE                                                  │
│     User Input → OutlineGenerator → LLM → Book Structure           │
│                                                                     │
│  2. GENERATE CONTENT                                                │
│     Book → ContentGenerator → LLM → Populated Chapters             │
│                                                                     │
│  3. ADD CODE EXAMPLES                                               │
│     Sections → CodeGenerator → LLM → Code + Explanations           │
│                                                                     │
│  4. CHECK & IMPROVE                                                 │
│     Content → GrammarChecker/ContentImprover → LLM → Enhanced Text  │
│                                                                     │
│  5. EXPORT                                                          │
│     Book → Formatter → Output File (HTML/PDF/EPUB/MD)              │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                    KEY FEATURES                                      │
├─────────────────────────────────────────────────────────────────────┤
│  ✓ Multi-LLM support (OpenAI & Anthropic)                          │
│  ✓ Automated outline generation                                    │
│  ✓ AI-powered content creation                                     │
│  ✓ Code generation with explanations                               │
│  ✓ Exercise generation with solutions                              │
│  ✓ Grammar & style checking                                        │
│  ✓ Content improvement suggestions                                 │
│  ✓ 4 export formats (HTML, PDF, EPUB, Markdown)                    │
│  ✓ Syntax highlighting                                             │
│  ✓ Customizable templates                                          │
│  ✓ CLI & Python API                                                │
│  ✓ Comprehensive testing                                           │
│  ✓ Security verified (CodeQL)                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Component Responsibilities

### Models Layer
- **Book, Chapter, Section**: Core data structures
- **Serialization**: JSON save/load functionality
- **Validation**: Data integrity

### Generators Layer
- **OutlineGenerator**: Creates book structure using AI
- **ContentGenerator**: Writes chapter and section content
- **CodeGenerator**: Creates code examples and exercises

### Editors Layer
- **GrammarChecker**: Quality assurance for text
- **ContentImprover**: AI-powered content enhancement

### Formatters Layer
- **HTMLFormatter**: Web-ready output with CSS
- **PDFFormatter**: Print-ready documents
- **EPUBFormatter**: E-reader compatible books
- **MarkdownFormatter**: Plain text, version-controllable

### Utilities Layer
- **LLMClient**: Unified interface for AI providers
- **LLMConfig**: Configuration and API key management
