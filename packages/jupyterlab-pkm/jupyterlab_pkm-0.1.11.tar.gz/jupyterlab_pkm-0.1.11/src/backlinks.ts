import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import { ICommandPalette, MainAreaWidget } from '@jupyterlab/apputils';
import { IEditorTracker } from '@jupyterlab/fileeditor';
import { IMarkdownViewerTracker } from '@jupyterlab/markdownviewer';
import { INotebookTracker } from '@jupyterlab/notebook';
import { IDocumentManager } from '@jupyterlab/docmanager';
import { Widget } from '@lumino/widgets';

const COMMAND_TOGGLE_BACKLINKS = 'pkm:toggle-backlinks-panel';
const COMMAND_BUILD_INDEX = 'pkm:build-wikilink-index'; 
const WIKILINK_INDEX_FILE = 'wikilink-index.json';

/**
 * Interface for backlink information
 */
interface Backlink {
  sourceFile: string;
  targetFile: string;
  context: string;
  lineNumber: number;
}

/**
 * Interface for the wikilink index structure
 */
interface WikilinkIndex {
  links: { [sourceFile: string]: string[] };
  backlinks: { [targetFile: string]: string[] };
  contexts: { [key: string]: { context: string; lineNumber: number } }; // key: "sourceFile->targetFile"
  lastUpdated: string;
}

/**
 * Widget to display backlinks in a side panel
 */
class BacklinksPanelWidget extends Widget {
  private _backlinks: Backlink[] = [];
  private _currentPath: string = '';
  private _container!: HTMLDivElement;
  public _wikilinkIndex: WikilinkIndex | null = null;
  private _isIndexing: boolean = false;
  private _indexingPromise: Promise<void> | null = null;

  constructor(
    private app: JupyterFrontEnd,
    private docManager: IDocumentManager,
    private editorTracker: IEditorTracker,
    private markdownTracker: IMarkdownViewerTracker,
    private notebookTracker: INotebookTracker
  ) {
    super();
    this.addClass('jp-pkm-backlinks-panel');
    this.title.label = 'Backlinks';
    this.title.closable = true;
    this.title.iconClass = 'jp-MaterialIcon jp-LinkIcon';

    this.createUI();
    this.initializeIndex(); // This will attempt to load or set up for building
    this.setupTracking();
    this.setupFileWatching();
  }

  private createUI(): void {
    this._container = document.createElement('div');
    this._container.className = 'jp-pkm-backlinks-content';
    this._container.style.cssText = `
      padding: 16px;
      height: 100%;
      overflow-y: auto;
      font-family: var(--jp-ui-font-family);
    `;
    this.node.appendChild(this._container);

    this.showLoadingState(); // Initial state before index status is known
  }

  private showLoadingState(): void {
    this._container.innerHTML = `
      <div class="jp-pkm-backlinks-loading" style="text-align: center; color: var(--jp-ui-font-color2); margin-top: 40px;">
        <div style="font-size: 24px; margin-bottom: 16px;">⏳</div>
        <div style="margin-bottom: 8px;">Loading backlinks data...</div>
        <div style="font-size: 12px;">Checking for existing index.</div>
      </div>
    `;
  }

  
  private showIndexNotBuiltState(): void {
    this._container.innerHTML = `
      <div class="jp-pkm-backlinks-empty" style="text-align: center; color: var(--jp-ui-font-color2); margin-top: 40px;">
        <div style="font-size: 24px; margin-bottom: 16px;">🗂️</div>
        <div style="margin-bottom: 8px;">Wikilink index not found or not built yet.</div>
        <div style="font-size: 12px;">Use 'PKM: Build/Rebuild Wikilink Index' from the command palette.</div>
      </div>
    `;
  }


  public async initializeIndex(): Promise<void> {
    if (this._isIndexing) {
      await this._indexingPromise;
      return;
    }

    this._isIndexing = true;
    this._indexingPromise = this._initializeIndexInternal();

    try {
      await this._indexingPromise;
    } finally {
      this._isIndexing = false;
      this._indexingPromise = null;
    }
  }

  private async _initializeIndexInternal(): Promise<void> {
    try {
      console.log('Backlinks: Initializing wikilink index...');
      this.showLoadingState(); // Show loading while attempting to load

      await this.loadWikilinkIndex();

      if (!this._wikilinkIndex) {
        // MODIFIED: Log message and call to new state
        console.log('Backlinks: No existing index found. Index can be built manually or will be built on first relevant file update.');
        this.showIndexNotBuiltState();
      } else {
        console.log('Backlinks: Existing index loaded');
        // Trigger initial update for the currently open file
        setTimeout(() => {
          this.handleCurrentChanged();
        }, 100);
      }

    } catch (error) {
      console.error('Backlinks: Error initializing index:', error);
      this.showErrorState();
    }
  }

  private async loadWikilinkIndex(): Promise<void> {
    try {
      console.log('Backlinks: Loading wikilink index from', WIKILINK_INDEX_FILE);
      const indexContent = await this.docManager.services.contents.get(WIKILINK_INDEX_FILE, { content: true });
      if (typeof indexContent.content === 'string' && indexContent.content.trim() !== '') {
        this._wikilinkIndex = JSON.parse(indexContent.content);
        console.log('Backlinks: Wikilink index loaded successfully. Last updated:', this._wikilinkIndex?.lastUpdated);
      } else {
        console.log('Backlinks: Wikilink index file is empty or content is not a string.');
        this._wikilinkIndex = null;
      }
    } catch (error) {
      // Error typically means file not found, which is fine on first run
      if ((error as any).response && (error as any).response.status === 404) {
        console.log('Backlinks: Wikilink index file not found. This is normal on first run.');
      } else {
        console.warn('Backlinks: Could not load wikilink index:', error);
      }
      this._wikilinkIndex = null;
    }
  }

  public async buildWikilinkIndex(): Promise<void> { // Made public for easier call from temp widget
    console.log('Backlinks: Building wikilink index from scratch...');

    const index: WikilinkIndex = {
      links: {},
      backlinks: {},
      contexts: {},
      lastUpdated: new Date().toISOString()
    };

    try {
      // FIXED: Simplified file discovery to prevent infinite loops
      const allFiles = await this.getAllMarkdownAndNotebookFiles();
      console.log(`Backlinks: Found ${allFiles.length} files to index`);

      for (const filePath of allFiles) {
        try {
          const fileName = filePath.split('/').pop() || '';
          console.log(`Backlinks: Indexing ${filePath}`);

          const content = await this.docManager.services.contents.get(filePath, { content: true });
          let textContent = '';

          if (fileName.endsWith('.md')) {
            textContent = typeof content.content === 'string' ? content.content : '';
          } else if (fileName.endsWith('.ipynb')) {
            textContent = this.extractNotebookText(content.content);
          }

          const wikilinks = this.extractWikilinks(textContent);

          if (wikilinks.length > 0) {
            index.links[filePath] = wikilinks.map(link => link.target);
            for (const wikilink of wikilinks) {
              const normalizedTarget = this.normalizeTarget(wikilink.target);
              if (!index.backlinks[normalizedTarget]) {
                index.backlinks[normalizedTarget] = [];
              }
              if (!index.backlinks[normalizedTarget].includes(filePath)) {
                 index.backlinks[normalizedTarget].push(filePath);
              }
              const contextKey = `${filePath}->${normalizedTarget}`;
              index.contexts[contextKey] = {
                context: wikilink.context,
                lineNumber: wikilink.lineNumber
              };
            }
          }
        } catch (error) {
          console.warn(`Backlinks: Error indexing ${filePath}:`, error);
        }
      }

      this._wikilinkIndex = index;
      await this.saveWikilinkIndex();
      console.log('Backlinks: Index built and saved successfully. Last updated:', this._wikilinkIndex.lastUpdated);

    } catch (error) {
      console.error('Backlinks: Error building wikilink index:', error);
      this._wikilinkIndex = null; // Ensure index is null on build failure
      throw error; // Re-throw to be caught by caller if necessary
    }
  }

  private normalizeTarget(target: string): string {
    const cleanTarget = target.trim();
    const pipeSplit = cleanTarget.split('|')[0].trim();
    return pipeSplit.replace(/\.(md|ipynb)$/i, '');
  }

  private async saveWikilinkIndex(): Promise<void> {
    if (!this._wikilinkIndex) {
        console.log('Backlinks: Attempted to save index, but index is null. Skipping.');
        return;
    }
    try {
      await this.docManager.services.contents.save(WIKILINK_INDEX_FILE, {
        type: 'file',
        format: 'text',
        content: JSON.stringify(this._wikilinkIndex, null, 2)
      });
      console.log('Backlinks: Wikilink index saved successfully to', WIKILINK_INDEX_FILE);
    } catch (error) {
      console.error('Backlinks: Error saving wikilink index:', error);
    }
  }

  private extractWikilinks(textContent: string): Array<{target: string, context: string, lineNumber: number}> {
    const wikilinks: Array<{target: string, context: string, lineNumber: number}> = [];
    const wikilinkRegex = /\[\[([^\]]+)\]\]/g;
    let match;

    console.log(`Backlinks: Extracting wikilinks from text (${textContent.length} chars)`);
    console.log(`Backlinks: Text content preview: "${textContent.substring(0, 200)}"`);

    while ((match = wikilinkRegex.exec(textContent)) !== null) {
      const linkText = match[1];
      const [targetFile] = linkText.split('|');
      const target = this.normalizeTarget(targetFile);
      const lineNumber = textContent.substring(0, match.index).split('\n').length;
      const context = this.extractContext(textContent, match.index);

      console.log(`Backlinks: Found wikilink: [[${linkText}]] -> normalized target: "${target}"`);
      wikilinks.push({ target, context, lineNumber });
    }

    console.log(`Backlinks: Total wikilinks extracted: ${wikilinks.length}`);
    return wikilinks;
  }

  // FIXED: Completely rewritten file discovery method to prevent infinite loops
  private async getAllMarkdownAndNotebookFiles(): Promise<string[]> {
    const files: string[] = [];
    const maxDepth = 5; // Prevent infinite recursion
    
    try {
      await this.scanDirectory('', files, new Set(), 0, maxDepth);
    } catch (error) {
      console.warn('Backlinks: Error scanning files:', error);
    }
    
    console.log(`Backlinks: Total files found: ${files.length}`, files);
    return files;
  }

  // FIXED: New recursive method with proper depth limiting and cycle detection
  private async scanDirectory(
    dirPath: string, 
    files: string[], 
    visited: Set<string>, 
    currentDepth: number, 
    maxDepth: number
  ): Promise<void> {
    // Prevent infinite recursion
    if (currentDepth >= maxDepth) {
      console.log(`Backlinks: Max depth ${maxDepth} reached for ${dirPath}`);
      return;
    }

    // Normalize the path and check for cycles
    const normalizedPath = dirPath.replace(/\/+$/, '') || '.';
    if (visited.has(normalizedPath)) {
      console.log(`Backlinks: Already visited ${normalizedPath}, skipping`);
      return;
    }
    visited.add(normalizedPath);

    try {
      console.log(`Backlinks: Scanning directory "${dirPath}" at depth ${currentDepth}`);
      
      const listing = await this.docManager.services.contents.get(dirPath, { 
        type: 'directory',
        content: true 
      });
      
      if (!listing.content || !Array.isArray(listing.content)) {
        console.log(`Backlinks: No content found in ${dirPath}`);
        return;
      }

      console.log(`Backlinks: Found ${listing.content.length} items in "${dirPath}"`);
      
      for (const item of listing.content) {
        // Skip hidden files and system directories
        if (item.name.startsWith('.') || item.name === '__pycache__' || item.name === 'node_modules') {
          continue;
        }

        if (item.type === 'file' && (item.name.endsWith('.md') || item.name.endsWith('.ipynb'))) {
          console.log(`Backlinks: Found target file: ${item.path}`);
          files.push(item.path);
        } else if (item.type === 'directory') {
          // Recursively scan subdirectory with increased depth
          await this.scanDirectory(item.path, files, visited, currentDepth + 1, maxDepth);
        }
      }
      
    } catch (error) {
      console.log(`Backlinks: Error scanning directory "${dirPath}":`, (error as any)?.message || error);
    }
  }

  private setupTracking(): void {
    this.editorTracker.currentChanged.connect(this.handleCurrentChanged, this);
    this.markdownTracker.currentChanged.connect(this.handleCurrentChanged, this);
    this.notebookTracker.currentChanged.connect(this.handleCurrentChanged, this);
  }

  private setupFileWatching(): void {
    this.docManager.services.contents.fileChanged.connect(this.handleFileChanged, this);
    this.editorTracker.widgetAdded.connect((sender, widget) => {
      if (widget.context.model) {
        widget.context.model.contentChanged.connect(() => {
          this.debounceFileUpdate(widget.context.path);
        });
      }
    });
    this.notebookTracker.widgetAdded.connect((sender, widget) => {
      if (widget.context.model) {
        widget.context.model.contentChanged.connect(() => {
          this.debounceFileUpdate(widget.context.path);
        });
      }
    });
  }

  private _updateTimeouts: Map<string, NodeJS.Timeout> = new Map();

  private debounceFileUpdate(filePath: string): void {
    const existingTimeout = this._updateTimeouts.get(filePath);
    if (existingTimeout) {
      clearTimeout(existingTimeout);
    }
    const timeout = setTimeout(() => {
      this.updateFileInIndex(filePath);
      this._updateTimeouts.delete(filePath);
    }, 2000);
    this._updateTimeouts.set(filePath, timeout);
  }

  private async handleFileChanged(sender: any, change: any): Promise<void> {
    if (!change || !change.newValue || !change.newValue.path) return;
    const filePath = change.newValue.path;
    const fileName = filePath.split('/').pop() || '';
    if (!fileName.endsWith('.md') && !fileName.endsWith('.ipynb')) return;

    console.log(`Backlinks: File changed (saved): ${filePath}, updating index...`);
    await this.updateFileInIndex(filePath);
  }

  private async updateFileInIndex(filePath: string): Promise<void> {
    if (!this._wikilinkIndex) {
      console.log('Backlinks: No index available during file update, building fresh index...');
      // Show loading in the panel if it's this instance that's active
      if (this.isVisible) this.showLoadingState();
      try {
        await this.buildWikilinkIndex();
        this.updateBacklinks(); // Refresh view after building
      } catch (error) {
        this.showErrorState();
      }
      return;
    }

    try {
      console.log(`Backlinks: Updating file in index: ${filePath}`);
      // Efficiently remove old entries for this file
      // Links from this file
      delete this._wikilinkIndex.links[filePath];
      // Backlinks where this file was the source
      for (const targetFile in this._wikilinkIndex.backlinks) {
        this._wikilinkIndex.backlinks[targetFile] = this._wikilinkIndex.backlinks[targetFile].filter(
          source => source !== filePath
        );
        if (this._wikilinkIndex.backlinks[targetFile].length === 0) {
          delete this._wikilinkIndex.backlinks[targetFile];
        }
      }
      // Contexts from this file
      for (const contextKey in this._wikilinkIndex.contexts) {
        if (contextKey.startsWith(`${filePath}->`)) {
          delete this._wikilinkIndex.contexts[contextKey];
        }
      }

      // Re-index this file if it still exists
      try {
        const content = await this.docManager.services.contents.get(filePath, { content: true });
        const fileName = filePath.split('/').pop() || '';
        let textContent = '';
        if (fileName.endsWith('.md')) {
          textContent = typeof content.content === 'string' ? content.content : '';
        } else if (fileName.endsWith('.ipynb')) {
          textContent = this.extractNotebookText(content.content);
        }
        const wikilinks = this.extractWikilinks(textContent);
        if (wikilinks.length > 0) {
          this._wikilinkIndex.links[filePath] = wikilinks.map(link => link.target);
          for (const wikilink of wikilinks) {
            const normalizedTarget = this.normalizeTarget(wikilink.target);
            if (!this._wikilinkIndex.backlinks[normalizedTarget]) {
              this._wikilinkIndex.backlinks[normalizedTarget] = [];
            }
            if (!this._wikilinkIndex.backlinks[normalizedTarget].includes(filePath)) {
                this._wikilinkIndex.backlinks[normalizedTarget].push(filePath);
            }
            const contextKey = `${filePath}->${normalizedTarget}`;
            this._wikilinkIndex.contexts[contextKey] = {
              context: wikilink.context,
              lineNumber: wikilink.lineNumber
            };
          }
        }
      } catch (fileError: any) {
        if (fileError.response && fileError.response.status === 404) {
            console.log(`Backlinks: File ${filePath} no longer exists (deleted), removed from index.`);
        } else {
            console.warn(`Backlinks: Error re-indexing ${filePath} (might be deleted or unreadable):`, fileError);
        }
      }

      this._wikilinkIndex.lastUpdated = new Date().toISOString();
      await this.saveWikilinkIndex();
      if (this._currentPath === filePath || (this._wikilinkIndex.backlinks[this.normalizeTarget(this._currentPath.split('/').pop() || '')] || []).includes(filePath)) {
        this.updateBacklinks();
      } else if (this._currentPath) {
        // Check if the updated file links TO the current file
        const normalizedCurrentFile = this.normalizeTarget(this._currentPath.split('/').pop() || '');
        if (this._wikilinkIndex.links[filePath]?.includes(normalizedCurrentFile)) {
            this.updateBacklinks();
        }
      }
    } catch (error) {
      console.error(`Backlinks: Error updating index for ${filePath}:`, error);
    }
  }

  private async handleCurrentChanged(): Promise<void> {
    console.log('Backlinks: handleCurrentChanged called');
    if (this._isIndexing) {
      await this._indexingPromise; // Wait for any ongoing initialization
    }

    const currentWidget = this.app.shell.currentWidget;
    let newPath = '';
    if (currentWidget) {
      const context = (currentWidget as any).context;
      if (context && context.path && (context.path.endsWith('.md') || context.path.endsWith('.ipynb'))) {
        newPath = context.path;
      }
    }

    console.log(`Backlinks: Active widget path: "${newPath}" (previous: "${this._currentPath}")`);
    if (newPath !== this._currentPath) {
      this._currentPath = newPath;
      console.log('Backlinks: Path changed, updating backlinks for:', newPath);
      this.updateBacklinks();
    } else {
      // Even if path is the same, refresh if the panel is showing but has no backlinks displayed
      if (!this._container.innerHTML.includes('jp-pkm-backlinks-item') && this._wikilinkIndex) {
        console.log('Backlinks: Path unchanged but no backlinks shown, refreshing...');
        this.updateBacklinks();
      }
    }
  }

  private showEmptyState(): void {
    this._container.innerHTML = `
      <div class="jp-pkm-backlinks-empty" style="text-align: center; color: var(--jp-ui-font-color2); margin-top: 40px;">
        <div style="font-size: 24px; margin-bottom: 16px;">🔗</div>
        <div style="margin-bottom: 8px;">No backlinks found for this file.</div>
        <div style="font-size: 12px;">Create [[wikilinks]] to it from other Markdown or Notebook files.</div>
      </div>
    `;
  }

  private showErrorState(): void {
    this._container.innerHTML = `
      <div class="jp-pkm-backlinks-error" style="text-align: center; color: var(--jp-error-color0); margin-top: 40px;">
        <div style="font-size: 24px; margin-bottom: 16px;">⚠️</div>
        <div style="margin-bottom: 8px;">Error loading or building backlinks.</div>
        <div style="font-size: 12px;">Check console for details. Try rebuilding the index.</div>
      </div>
    `;
  }

  private updateBacklinks(): void {
    // console.log('Backlinks: updateBacklinks called for path:', this._currentPath);
    this._backlinks = [];

    if (!this._currentPath) {
      // If no file is active, show the generic empty/not_built state
      if (!this._wikilinkIndex) {
        this.showIndexNotBuiltState();
      } else {
        this.showEmptyState(); // Or a "select a file" message
      }
      return;
    }

    // MODIFIED: Check for null index and call appropriate state
    if (!this._wikilinkIndex) {
      this.showIndexNotBuiltState();
      return;
    }

    const currentFileName = this._currentPath.split('/').pop() || '';
    const possibleTargets = [
      currentFileName,
      currentFileName.replace(/\.[^/.]+$/, ''),
      currentFileName.endsWith('.ipynb') ? currentFileName.replace('.ipynb', '') : null
    ].filter(Boolean) as string[];

    const allSourceFiles = new Set<string>();
    const sourceFileContexts = new Map<string, {context: string, lineNumber: number}>();

    for (const target of possibleTargets) {
      const sourceFiles = this._wikilinkIndex.backlinks[this.normalizeTarget(target)] || []; // Normalize target here too
      for (const sourceFile of sourceFiles) {
        allSourceFiles.add(sourceFile);
        const contextKey = `${sourceFile}->${this.normalizeTarget(target)}`;
        const contextData = this._wikilinkIndex.contexts[contextKey];
        if (contextData && !sourceFileContexts.has(sourceFile)) {
          sourceFileContexts.set(sourceFile, contextData);
        }
      }
    }

    this._backlinks = Array.from(allSourceFiles).map(sourceFile => {
      const contextData = sourceFileContexts.get(sourceFile);
      return {
        sourceFile,
        targetFile: this._currentPath,
        context: contextData?.context || 'Context not available.',
        lineNumber: contextData?.lineNumber || 1
      };
    });

    // console.log('Backlinks: Found', this._backlinks.length, 'backlinks.');
    this.renderBacklinks();
  }

  private extractNotebookText(notebookContent: any): string {
    if (!notebookContent || !notebookContent.cells || !Array.isArray(notebookContent.cells)) {
      return '';
    }
    const markdownCells = notebookContent.cells.filter((cell: any) => cell.cell_type === 'markdown');
    const textParts: string[] = [];
    for (const cell of markdownCells) {
      let cellText = '';
      if (typeof cell.source === 'string') {
        cellText = cell.source;
      } else if (Array.isArray(cell.source)) {
        cellText = cell.source.join('');
      } else if (cell.source) {
        cellText = String(cell.source);
      }
      if (cellText.trim()) {
        textParts.push(cellText);
      }
    }
    return textParts.join('\n\n---\n\n'); // Add separator between cells for context
  }

  private extractContext(content: string, matchIndex: number): string {
    const lines = content.split('\n');
    const position = content.substring(0, matchIndex).split('\n').length - 1;
    const contextRadius = 1; // Number of lines above and below
    const startLine = Math.max(0, position - contextRadius);
    const endLine = Math.min(lines.length - 1, position + contextRadius);
    return lines.slice(startLine, endLine + 1).join('\n').trim();
  }

  private renderBacklinks(): void {
    this._container.innerHTML = '';
    if (this._backlinks.length === 0) {
        // This will be called if currentPath is set, index is loaded, but no backlinks for this file.
        this.showEmptyState();
        return;
    }
    const header = document.createElement('div'); /* ... same as before ... */
    header.className = 'jp-pkm-backlinks-header';
    header.textContent = `Backlinks (${this._backlinks.length})`;
    header.style.cssText = `
      font-size: 1.1rem;
      font-weight: 600;
      margin-bottom: 1rem;
      color: var(--jp-ui-font-color0);
      border-bottom: 1px solid var(--jp-border-color1);
      padding-bottom: 0.5rem;
    `;
    this._container.appendChild(header);

    this._backlinks.forEach(backlink => {
      const item = document.createElement('div'); /* ... same as before ... */
      item.className = 'jp-pkm-backlinks-item';
      item.style.cssText = `
        margin-bottom: 1rem;
        padding: 0.75rem;
        border: 1px solid var(--jp-border-color1);
        border-radius: 4px;
        background: var(--jp-layout-color1);
        cursor: pointer;
        transition: background-color 0.2s;
      `;

      const fileName = document.createElement('div'); /* ... same as before ... */
      fileName.className = 'jp-pkm-backlinks-filename';
      fileName.textContent = backlink.sourceFile;
      fileName.style.cssText = `
        font-weight: 600;
        color: var(--jp-content-link-color);
        margin-bottom: 0.5rem;
        font-size: 0.9rem;
      `;

      const context = document.createElement('div'); /* ... same as before ... */
      context.className = 'jp-pkm-backlinks-context';
      context.textContent = backlink.context;
      context.style.cssText = `
        color: var(--jp-ui-font-color1);
        font-size: 0.85rem;
        line-height: 1.4;
        white-space: pre-wrap;
        max-height: 100px; /* Limit context height */
        overflow-y: auto; /* Allow scrolling for long contexts */
      `;

      item.addEventListener('click', () => {
        this.docManager.openOrReveal(backlink.sourceFile);
      });
      item.addEventListener('mouseenter', () => { item.style.backgroundColor = 'var(--jp-layout-color2)'; });
      item.addEventListener('mouseleave', () => { item.style.backgroundColor = 'var(--jp-layout-color1)'; });
      item.appendChild(fileName);
      item.appendChild(context);
      this._container.appendChild(item);
    });
  }

  public refresh(): void {
    console.log('Backlinks: Manual refresh called via panel method');
    // Force refresh by clearing current path and calling handleCurrentChanged
    const oldPath = this._currentPath;
    this._currentPath = '';
    this.handleCurrentChanged().then(() => {
      // If no file was detected, restore the old path and try to update anyway
      if (!this._currentPath && oldPath) {
        this._currentPath = oldPath;
        this.updateBacklinks();
      }
    });
  }

  public async rebuildIndex(): Promise<void> {
    console.log('Backlinks: Panel widget rebuildIndex called.');
    // This method is called on an existing panel instance.
    // So, it should show its own loading state.
    this.showLoadingState(); // Show loading in this panel
    try {
        await this.buildWikilinkIndex(); // Build and save
        this.updateBacklinks(); // Refresh the view of this panel
    } catch (error) {
        this.showErrorState();
    }
  }

  dispose(): void {
    for (const timeout of this._updateTimeouts.values()) {
      clearTimeout(timeout);
    }
    this._updateTimeouts.clear();
    super.dispose();
  }
}

/**
 * Plugin to display backlinks in a side panel
 */
export const backlinksPlugin: JupyterFrontEndPlugin<void> = {
  id: '@jupyterlab/pkm-extension:backlinks',
  description: 'Display backlinks for markdown and notebook files in a side panel',
  autoStart: true,
  requires: [IEditorTracker, IMarkdownViewerTracker, INotebookTracker, IDocumentManager],
  optional: [ICommandPalette], // Remove notification for now
  activate: (
    app: JupyterFrontEnd,
    editorTracker: IEditorTracker,
    markdownTracker: IMarkdownViewerTracker,
    notebookTracker: INotebookTracker,
    docManager: IDocumentManager,
    palette: ICommandPalette | null
  ) => {
    console.log('Backlinks plugin activated');

    let backlinksPanelWidgetInstance: MainAreaWidget<BacklinksPanelWidget> | null = null;

    app.commands.addCommand(COMMAND_TOGGLE_BACKLINKS, {
      label: 'PKM: Toggle Backlinks Panel',
      caption: 'Show or hide the backlinks panel',
      execute: () => {
        if (backlinksPanelWidgetInstance && !backlinksPanelWidgetInstance.isDisposed) {
          if (backlinksPanelWidgetInstance.isVisible) {
            // If visible, close it
            backlinksPanelWidgetInstance.close();
          } else {
            // If not visible, add it and make sure it's properly activated
            app.shell.add(backlinksPanelWidgetInstance, 'right');
            app.shell.activateById(backlinksPanelWidgetInstance.id);
            // Trigger a refresh to show current file's backlinks
            backlinksPanelWidgetInstance.content.refresh();
          }
        } else {
          // Create new panel
          const widgetContent = new BacklinksPanelWidget(app, docManager, editorTracker, markdownTracker, notebookTracker);
          backlinksPanelWidgetInstance = new MainAreaWidget({ content: widgetContent });
          backlinksPanelWidgetInstance.id = 'pkm-backlinks-panel';
          backlinksPanelWidgetInstance.title.label = 'Backlinks';
          backlinksPanelWidgetInstance.title.closable = true;
          
          // Add to shell and make sure it's visible and active
          app.shell.add(backlinksPanelWidgetInstance, 'right');
          app.shell.activateById(backlinksPanelWidgetInstance.id);
          
          // Trigger a refresh to show current file's backlinks
          setTimeout(() => {
            if (backlinksPanelWidgetInstance && !backlinksPanelWidgetInstance.isDisposed) {
              backlinksPanelWidgetInstance.content.refresh();
            }
          }, 100);
        }
      }
    });

    app.commands.addCommand(COMMAND_BUILD_INDEX, {
      label: 'PKM: Build/Rebuild Wikilink Index',
      caption: 'Scan all files and (re)build the wikilink index.',
      execute: async () => {
        console.log(`Backlinks: Command '${COMMAND_BUILD_INDEX}' triggered.`);
        if (backlinksPanelWidgetInstance && !backlinksPanelWidgetInstance.isDisposed && backlinksPanelWidgetInstance.isVisible) {
          console.log('Backlinks: Panel is visible, calling rebuildIndex on existing panel widget.');
          await backlinksPanelWidgetInstance.content.rebuildIndex();
        } else {
          console.log('Backlinks: Panel not visible/open or not yet created. Building index in background.');
          const tempBuilder = new BacklinksPanelWidget(app, docManager, editorTracker, markdownTracker, notebookTracker);
          try {
            await tempBuilder.buildWikilinkIndex();
            console.log('Backlinks: Background index build completed and saved.');
          } catch (error) {
            console.error('Backlinks: Error during background index build:', error);
            console.error('Failed to build wikilink index in background.');
          } finally {
            tempBuilder.dispose();
          }

          if (backlinksPanelWidgetInstance && !backlinksPanelWidgetInstance.isDisposed) {
            console.log('Backlinks: Refreshing existing (possibly hidden) panel to load new index.');
            await backlinksPanelWidgetInstance.content.initializeIndex();
          }
        }
        console.log('Wikilink index build/rebuild initiated.');
      }
    });

    if (palette) {
      palette.addItem({
        command: COMMAND_TOGGLE_BACKLINKS,
        category: 'PKM'
      });
      palette.addItem({
        command: COMMAND_BUILD_INDEX,
        category: 'PKM'
      });
    }

    app.commands.addKeyBinding({
      command: COMMAND_TOGGLE_BACKLINKS,
      keys: ['Alt B'],
      selector: 'body'
    });

    const style = document.createElement('style');
    style.textContent = `
      .jp-pkm-backlinks-panel { min-width: 250px; }
      .jp-pkm-backlinks-content { font-family: var(--jp-ui-font-family); }
      .jp-pkm-backlinks-header {
        font-size: 1.1rem; font-weight: 600; margin-bottom: 1rem;
        color: var(--jp-ui-font-color0); border-bottom: 1px solid var(--jp-border-color1);
        padding-bottom: 0.5rem;
      }
      .jp-pkm-backlinks-empty, .jp-pkm-backlinks-loading, .jp-pkm-backlinks-error {
        text-align: center; padding: 2rem 1rem; font-style: italic;
      }
      .jp-pkm-backlinks-empty, .jp-pkm-backlinks-loading { color: var(--jp-ui-font-color2); }
      .jp-pkm-backlinks-error { color: var(--jp-error-color0); }
      .jp-pkm-backlinks-item {
        margin-bottom: 1rem; padding: 0.75rem; border: 1px solid var(--jp-border-color1);
        border-radius: 4px; background: var(--jp-layout-color1);
        cursor: pointer; transition: background-color 0.2s;
      }
      .jp-pkm-backlinks-item:hover { background: var(--jp-layout-color2); }
      .jp-pkm-backlinks-filename {
        font-weight: 600; color: var(--jp-content-link-color);
        margin-bottom: 0.5rem; font-size: 0.9rem;
      }
      .jp-pkm-backlinks-context {
        color: var(--jp-ui-font-color1); font-size: 0.85rem;
        line-height: 1.4; white-space: pre-wrap;
        max-height: 100px; overflow-y: auto;
      }
    `;
    document.head.appendChild(style);
  }
};