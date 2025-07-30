# Personal Knowledge Management (PKM) Extension Guide

🎉 **The PKM Extension is now active!** This extension transforms JupyterLab into a powerful note-taking and knowledge management system.

## 🚀 Quick Start

1. Create a new markdown file (e.g., `start.md`)
2. Start linking notes with wikilinks: `[[Note Name]]`
3. Use keyboard shortcuts for quick navigation
4. Embed notebooks and code blocks in your notes

## ✨ Key Features

### 📝 Wikilinks
- `[[Note Name]]` - Create links between notes
- `[[note|display text]]` - Link with custom display text  
- **Shift + Click** to follow links in editing mode
- **Ctrl/Cmd + Click** to follow links in preview mode
- Auto-completion for existing notes when typing `[[`

### 🔍 Search & Navigation
- **Alt + F** - Global search across all files
- **Alt + B** - Show backlinks (what links to current note)
- Full-text search across markdown files and notebooks
- Quick navigation between connected notes

### 📊 Content Embedding
- `![[notebook.ipynb#cell-id]]` - Embed specific cells from ipynb files 
- `![[file.md#heading]]` - Embed sections from markdown files
- Live preview of embedded content

In ipynb files, you can use the Cell Overview Tool to quickly see the cell id for embedding. Use `PKM: Show Notebook Cell Overview` from the command palette to see all cells with their IDs, types, and previews.

### 📋 Code Features
- **Copy code blocks** from markdown with click-to-copy buttons
- Syntax highlighting in embedded code
- **Alt + M** - Toggle markdown preview mode

### 🔗 Backlinks Panel
- See all files that link to the current note
- Automatic backlink detection
- Navigate between related notes easily

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| **Alt + F** | Open global search |
| **Alt + B** | Show backlinks for current file |
| **Alt + M** | Toggle markdown preview |
| **Shift + Click** | Follow wikilink in editor |
| **Click** | Follow wikilink in preview/create new file from link if it doesn't already exist |

## 📁 File Organization Tips

### Recommended Structure
```
your-workspace/
├── start.md              # Your main index/homepage
├── projects/
│   ├── project-a.md
│   └── project-b.md
├── notes/
│   ├── meeting-notes.md
│   └── research-ideas.md
├── notebooks/
│   ├── analysis.ipynb
│   └── data-processing.ipynb
└── PKM-Extension-Guide.md # This guide
```

### Best Practices
- Use `start.md` as your main hub/homepage
- Create meaningful note titles for better wikilink suggestions
- Link liberally - connections emerge over time
- Use headings to create linkable sections
- Embed relevant notebook outputs in your notes

## 🔧 Advanced Usage

### Block Embedding
You can embed specific sections of files, and use a custom title if you want:
```markdown
![[research-notes.md#methodology]]
![[analysis.ipynb#results-cell]]
![[summary#results|Key Results]]
```

You can also indicate 

### Cross-referencing Notebooks and Notes
```markdown
In my analysis [[data-analysis.ipynb]], I found that...

The methodology described in [[research-methods.md]] was applied...
```

### Creating a Personal Wiki
- Start with broad topic pages
- Link to specific project notes
- Create index pages for different areas
- Use consistent naming conventions

## 🎯 Workflow Examples

### Research Workflow
1. Create project overview in `project-overview.md`
2. Link to relevant notebooks: `[[data-collection.ipynb]]`
3. Reference methodology: `[[research-methods.md]]`
4. Track progress with linked daily notes

### Learning Workflow  
1. Create topic index: `[[machine-learning.md]]`
2. Link to specific concepts: `[[neural-networks.md]]`
3. Embed code examples: `![[ml-examples.ipynb]]`
4. Build concept maps with wikilinks

## 🆘 Troubleshooting

### Links Not Working?
- Ensure file exists in workspace
- Check file extension (.md for markdown, .ipynb for notebooks)
- Use exact filename in wikilinks

### Search Not Finding Files?
- Make sure files are saved
- Check that content is in markdown or notebook format
- Try alternative search terms

### Backlinks Missing?
- Save files to update backlink index
- Ensure wikilinks use correct syntax: `[[filename]]`

## 📚 Getting Help

- Access this guide anytime via Command Palette: "PKM: Open Documentation"
- All PKM commands available in Command Palette (Cmd/Ctrl + Shift + P)
- Look for "PKM:" prefix in command palette

---

**Happy note-taking!** 🎉

*This file was automatically created by the PKM Extension. You can edit or delete it as needed.*
