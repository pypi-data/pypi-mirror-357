import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import { ICommandPalette } from '@jupyterlab/apputils';
import { IFileBrowserFactory } from '@jupyterlab/filebrowser';

/**
 * The command IDs used by the welcome plugin
 */
namespace CommandIDs {
  export const showWelcome = 'pkm:show-welcome';
}

/**
 * Welcome plugin that creates documentation file
 */
export const welcomePlugin: JupyterFrontEndPlugin<void> = {
  id: '@jupyterlab/pkm-extension:welcome',
  description: 'Creates PKM documentation and adds help command',
  autoStart: true,
  requires: [ICommandPalette, IFileBrowserFactory],
  activate: async (app: JupyterFrontEnd, palette: ICommandPalette, factory: IFileBrowserFactory) => {
    console.log('PKM Welcome plugin activated');
    
    // Create documentation file on activation
    await createPKMDocumentation(app);
    
    // Create start.md file on activation
    await createStartFile(app);
    
    // Add command to open documentation
    app.commands.addCommand(CommandIDs.showWelcome, {
      label: 'PKM: Open Documentation',
      execute: async () => {
        try {
          await app.commands.execute('docmanager:open', {
            path: 'PKM-Extension-Guide.md'
          });
        } catch (error) {
          console.warn('Could not open PKM documentation:', error);
          alert('PKM Documentation should be available as "PKM-Extension-Guide.md" in your file browser');
        }
      }
    });
    
    palette.addItem({
      command: CommandIDs.showWelcome,
      category: 'PKM'
    });
  }
};

/**
 * Create PKM documentation file
 */
async function createPKMDocumentation(app: JupyterFrontEnd): Promise<void> {
  const docContent = `# Personal Knowledge Management (PKM) Extension Guide

🎉 **The PKM Extension is now active!** This extension transforms JupyterLab into a powerful note-taking and knowledge management system.

## 🚀 Quick Start

1. Create a new markdown file (e.g., \`start.md\`)
2. Start linking notes with wikilinks: \`[[Note Name]]\`
3. Use keyboard shortcuts for quick navigation
4. Embed notebooks and code blocks in your notes

## ✨ Key Features

### 📝 Wikilinks
- \`[[Note Name]]\` - Create links between notes
- \`[[note|display text]]\` - Link with custom display text  
- **Shift + Click** to follow links in editing mode
- **Ctrl/Cmd + Click** to follow links in preview mode
- Auto-completion for existing notes when typing \`[[\`

### 🔍 Search & Navigation
- **Alt + F** - Global search across all files
- **Alt + B** - Show backlinks (what links to current note)
- Full-text search across markdown files and notebooks
- Quick navigation between connected notes

### 📊 Content Embedding
- \`![[notebook.ipynb#cell-id]]\` - Embed specific cells from ipynb files 
- \`![[file.md#heading]]\` - Embed sections from markdown files
- Live preview of embedded content

In ipynb files, you can use the Cell Overview Tool to quickly see the cell id for embedding. Use \`PKM: Show Notebook Cell Overview\` from the command palette to see all cells with their IDs, types, and previews.

### 📋 Code Features
- **Copy code blocks** from markdown with click-to-copy buttons
- Syntax highlighting in embedded code
- **Alt + M** - Toggle markdown preview mode

### 🔗 Backlinks Panel
- See all files that link to the current note
- Automatic backlink detection
- Navigate between related notes easily
- FIRST TIME USE: build the backlinks index with the PKM: Build/Rebuild Wikilink Index command
- Open/close the backlinks panel to refresh the view

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
\`\`\`
your-workspace/
├── start.md              # Your main index/homepage
├── projects/
│   ├── project-a.md
│   └── project-b.md
├── notes/
│   ├── meeting-notes.md
│   └── research-ideas.md
├── biblio/
│   ├── @GrahamS-2022a.md
│   └── @GrahamS-2022b.md
├── analytical_notes/
│   ├── analysis.ipynb
│   └── data-processing.ipynb
└── PKM-Extension-Guide.md # This guide
\`\`\`

### Best Practices
- Use \`start.md\` as your main hub/homepage
- Create meaningful note titles for better wikilink suggestions
- Link liberally - connections emerge over time
- Use headings to create linkable sections
- Embed relevant notebook outputs in your notes

## 🔧 Advanced Usage

### Block Embedding
You can embed specific sections of files, and use a custom title if you want:
\`\`\`markdown
![[research-notes.md#methodology]]
![[analysis.ipynb#results-cell]]
![[summary#results|Key Results]]
\`\`\`

You can also indicate 

### Cross-referencing Notebooks and Notes
\`\`\`markdown
In my analysis [[data-analysis.ipynb]], I found that...

The methodology described in [[research-methods.md]] was applied...
\`\`\`

### Creating a Personal Wiki
- Start with broad topic pages
- Link to specific project notes
- Create index pages for different areas
- Use consistent naming conventions

## 🎯 Workflow Examples

### Research Workflow
1. Create project overview in \`project-overview.md\`
2. Link to relevant notebooks: \`[[data-collection.ipynb]]\`
3. Reference methodology: \`[[research-methods.md]]\`
4. Track progress with linked daily notes

### Learning Workflow  
1. Create topic index: \`[[machine-learning.md]]\`
2. Link to specific concepts: \`[[neural-networks.md]]\`
3. Embed code examples: \`![[ml-examples.ipynb]]\`
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
- Ensure wikilinks use correct syntax: \`[[filename]]\`

## 📚 Getting Help

- Access this guide anytime via Command Palette: "PKM: Open Documentation"
- All PKM commands available in Command Palette (Cmd/Ctrl + Shift + P)
- Look for "PKM:" prefix in command palette

---

**Happy note-taking!** 🎉

*This file was automatically created by the PKM Extension. You can edit or delete it as needed.*
`;

  try {
    // Check if file already exists
    const contents = app.serviceManager.contents;
    const fileName = 'PKM-Extension-Guide.md';
    
    try {
      await contents.get(fileName);
      console.log('PKM documentation already exists');
      return;
    } catch (error) {
      // File doesn't exist, create it
    }
    
    // Create the documentation file
    await contents.save(fileName, {
      type: 'file',
      format: 'text',
      content: docContent
    });
    
    console.log('PKM documentation created: PKM-Extension-Guide.md');
    
  } catch (error) {
    console.warn('Could not create PKM documentation:', error);
  }
}

/**
 * Create start.md file if it doesn't exist
 */
async function createStartFile(app: JupyterFrontEnd): Promise<void> {
  const startContent = `# Welcome to Your PKM System

This is your starting note. Try creating wikilinks:

- [[My First Note]] - Creates a new note
- [[https://example.com|External Link]] - Links to external sites

## Features:
- **Wikilinks**: Use [[Note Name]] syntax
- **Search**: Alt+F to search all notes  
- **Auto-save**: Your changes are saved automatically
- **Mode Toggle**: Use the button above or Alt+M to switch between edit and preview modes

Start building your knowledge graph!

## Quick Start Guide
Check out the [[PKM-Extension-Guide]] for complete documentation and advanced features.

## Getting Started
1. **Create notes**: Simply type \`[[New Note Name]]\` to create a link
2. **Follow links**: Click on any wikilink to navigate or create new notes
3. **Search everything**: Press Alt+F to search across all your notes
4. **View connections**: Press Alt+B to see what links to the current note

---
*This file was automatically created by the PKM Extension. Feel free to edit it as your personal starting point!*
`;

  try {
    // Check if file already exists
    const contents = app.serviceManager.contents;
    const fileName = 'start.md';
    
    try {
      await contents.get(fileName);
      console.log('start.md already exists');
      return;
    } catch (error) {
      // File doesn't exist, create it
    }
    
    // Create the start.md file
    await contents.save(fileName, {
      type: 'file',
      format: 'text',
      content: startContent
    });
    
    console.log('start.md created successfully');
    
  } catch (error) {
    console.warn('Could not create start.md:', error);
  }
}