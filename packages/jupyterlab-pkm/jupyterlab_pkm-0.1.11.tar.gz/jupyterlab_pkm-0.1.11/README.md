# JupyterLab PKM Extension

**we developed this for our own internal use, and we used Claude to scaffold some parts. We're not likely to develop it any further with any more features, so if there's something you want, fork and develop as you will.**

[![PyPI version](https://badge.fury.io/py/jupyterlab-pkm.svg)](https://badge.fury.io/py/jupyterlab-pkm)
[![License](https://img.shields.io/badge/License-BSD_3--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)

Transform your JupyterLab into a Personal Knowledge Management (PKM) system with wikilinks, backlinks, search, and notebook cell embedding capabilities.

## 🌟 Overview

This extension bridges the gap between computational notebooks and knowledge management, combining:
- **Jupyter's computational power** for data analysis and code development
- **Markdown's simplicity** for note-taking and documentation  
- **PKM features** for connecting and organizing knowledge

Perfect for researchers, students, and educators who want to build connected knowledge graphs while maintaining full computational capabilities in JupyterLab Desktop.

## ✨ Key Features

### 🔗 **Wikilinks & Navigation**
- **Link syntax**: `[[Note Name]]` or `[[file|Display Text]]`
- **Multi-format support**: Link to `.md`, `.ipynb`, `.csv`, `.json`, `.geojson` files
- **Auto-completion**: Type `[[` for smart file suggestions
- **Click navigation**: Ctrl/Cmd+click to follow links
- **Broken link creation**: Click red links to create new files

### 📊 **Notebook Cell Embedding**
Embed specific cells from Jupyter notebooks:
```markdown
![[analysis.ipynb#cell:5]]        <!-- Full cell (code + output) -->
![[analysis.ipynb#cell:5:code]]   <!-- Code only -->
![[analysis.ipynb#cell:5:output]] <!-- Output only -->
```

**Cell Overview Tool**: Use `PKM: Show Notebook Cell Overview` to see all cells with their IDs, types, and previews.

### 📄 **Block Embedding**
Reference and embed content from other markdown files:
```markdown
![[research-notes#methodology]]     <!-- Embed by heading -->
![[findings#key-insight]]          <!-- Embed by block ID -->
![[summary#results|Key Results]]   <!-- With custom title -->
```

### 🔍 **Search & Discovery**
- **Global search** (`Alt+F`): Search across all markdown files and notebooks
- **Backlinks panel** (`Alt+B`): See which files link to the current file
- **Real-time results**: Live search with context previews

### 📝 **Editing**
- **Mode toggle** (`Alt+M`): Switch between edit and preview modes
- **Auto-preview startup**: Files open in preview mode by default
- **Floating toggle button**: Visual mode indicator

## 📦 Installation

### Using pip (Recommended)

```bash
pip install jupyterlab-pkm
```

### Using conda

```bash
conda install -c conda-forge jupyterlab-pkm
```

### Prerequisites
- JupyterLab 4.0+
- Python 3.8+

### Install from Source

1. **Clone the repository**:
   ```bash
   git clone https://github.com/XLabCU/jupyterlab-desktop-pkm.git
   cd jupyterlab-pkm
   ```

2. **Install frontend dependencies and build**:
   ```bash
   jlpm install
   jlpm build
   ```

3. **Install the Python package**:
   ```bash
   pip install -e .
   ```

4. **Restart JupyterLab Desktop**

### Development Installation

For development work:

```bash
# Clone and install in development mode
git clone https://github.com/XLabCU/jupyterlab-desktop-pkm.git
cd jupyterlab-pkm

# Install dependencies and build
jlpm install
jlpm build

# Install Python package in development mode
pip install -e .

# Install extension in development mode
jupyter labextension develop . --overwrite

# Start JupyterLab Desktop in watch mode
jlpm watch
```

## 📁 Content Organization

Structure your workspace for optimal PKM experience:

```
workspace/
├── start.md                 # Landing page (auto-opens)
├── projects/
│   ├── project-alpha.md
│   ├── analysis.ipynb
│   └── data.csv
├── notes/
│   ├── daily-notes/
│   ├── research/
│   └── ideas/
└── resources/
    ├── methodologies.md
    └── references.md
```

## 🎯 Use Cases

### 📚 **Academic Research**
- Link literature reviews to data analysis notebooks
- Embed key findings across multiple papers
- Track research progression with connected notes

### 👩‍🏫 **Teaching & Learning**
- Create interconnected lesson materials
- Embed live code examples in documentation
- Build concept maps with executable content

### 💼 **Project Documentation**
- Connect project plans to implementation notebooks
- Embed analysis results in reports
- Maintain living documentation with computational backing

### 🧠 **Personal Knowledge Management**
- Build a second brain with computational capabilities
- Connect ideas across disciplines
- Maintain reproducible research notes

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Alt+M` | Toggle edit/preview mode |
| `Alt+F` | Open global search |
| `Alt+B` | Toggle backlinks panel |
| `Ctrl/Cmd+Click` | Follow wikilink |

## 🛠️ Configuration

### Startup Behavior
The extension automatically opens `start.md` in preview mode. Create this file in your workspace root to customize the landing experience.

### Auto-save
Files are automatically saved according to JupyterLab's auto-save settings.

### Search Indexing
Search indexes all `.md` and `.ipynb` files in your workspace directory and subdirectories.

## 📖 Usage Examples

### Basic Note Linking
```markdown
# Research Project Alpha

## Overview
This project builds on [[previous-research]] and explores [[new-methodology]].

## Data Analysis
See the full analysis in [[analysis.ipynb]] and key findings in [[results-summary]].

## Next Steps
- Review [[literature-review#recent-papers]]
- Update [[methodology#data-collection]]
- Prepare [[presentation-draft]]
```

### Embedding Computational Results

```markdown
# Monthly Report

## Key Metrics
![[metrics-analysis.ipynb#cell:3:output]]

## Methodology
![[analysis-methods#statistical-approach]]

## Code Implementation
![[implementation.ipynb#cell:5:code]]
```

Use the command palette command `PKM: Show Notebook Cell Overview` when viewing a notebook to see cell IDs for embedding.

## 🔧 Development

### Building
```bash
jlpm build
```

### Testing
```bash
jlpm test
```

### Linting
```bash
jlpm lint
```

### Watching for changes
```bash
jlpm watch
```

## 📄 License

This project is licensed under the BSD 3-Clause License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built on [JupyterLab](https://github.com/jupyterlab/jupyterlab)
- Inspired by [Obsidian](https://obsidian.md/), [Logseq](https://logseq.com/), and [Roam Research](https://roamresearch.com/)
- Adapted from the original JupyterLite PKM extension
- Designed for digital humanities education and computational research workflows

## 📚 Related Projects

- [JupyterLite PKM Extension](https://github.com/XLabCU/jupyterlite-pkm) - The original browser-based version
- [Obsidian](https://obsidian.md/) - Dedicated PKM application
- [Logseq](https://logseq.com/) - Local-first knowledge base
- [Tangent Notes](https://www.tangentnotes.com/) - Note-taking with wikilinks

## Future?

Jun 3, 2025: Everything we need, we think.