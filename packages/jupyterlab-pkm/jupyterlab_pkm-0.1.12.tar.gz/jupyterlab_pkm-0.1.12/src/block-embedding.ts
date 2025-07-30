import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import { ICommandPalette, MainAreaWidget } from '@jupyterlab/apputils';
import { IEditorTracker } from '@jupyterlab/fileeditor';
import { IMarkdownViewerTracker } from '@jupyterlab/markdownviewer';
import { IRenderMimeRegistry, IRenderMime } from '@jupyterlab/rendermime';
import { IDocumentManager } from '@jupyterlab/docmanager';
import { Contents } from '@jupyterlab/services';
import { Widget } from '@lumino/widgets';

/**
 * Regular expression for block embedding syntax
 */
const BLOCK_EMBED_REGEX = /!\[\[([^#\]]+)#([^\]|]+)(?:\|([^\]]+))?\]\]/g;

/**
 * Interface for parsed block embed
 */
interface BlockEmbed {
  fullMatch: string;
  sourceFile: string;
  blockRef: string;
  displayTitle?: string;
  startIndex: number;
  endIndex: number;
  isNotebookCell?: boolean;
  cellIndex?: number;
  cellType?: 'code' | 'output' | 'markdown' | 'full';
}

/**
 * Interface for extracted block content
 */
interface ExtractedBlock {
  content: string;
  title: string;
  sourceFile: string;
  blockRef: string;
  extractedAt: Date;
  found: boolean;
  isNotebookCell?: boolean;
  cellIndex?: number;
  cellType?: 'code' | 'output' | 'markdown' | 'full';
  executionCount?: number;
}

/**
 * Find file by name across all directories, supporting multiple extensions
 */
async function findFile(
  docManager: IDocumentManager,
  filename: string
): Promise<string | null> {
  const contents = docManager.services.contents;
  
  // Determine target filename with proper extension
  const targetName = filename.includes('.') ? filename : `${filename}.md`;
  console.log('Block embedding - searching for file:', filename, '-> target:', targetName);

  async function searchDirectory(path: string): Promise<string | null> {
    try {
      const listing = await contents.get(path, { content: true });
      
      if (listing.type !== 'directory' || !listing.content) {
        return null;
      }

      console.log(`Block embedding - searching in directory: ${path || 'root'}, found ${listing.content.length} items`);
      
      for (const item of listing.content as Contents.IModel[]) {
        console.log(`  - ${item.name} (${item.type})`);
        if ((item.type === 'file' || item.type === 'notebook') && item.name === targetName) {
          console.log(`Block embedding - found match: ${item.path}`);
          return item.path;
        } else if (item.type === 'directory') {
          const found = await searchDirectory(item.path);
          if (found) {
            return found;
          }
        }
      }
    } catch (error) {
      console.error(`Block embedding - error searching directory ${path}:`, error);
    }
    
    return null;
  }

  return searchDirectory('');
}

/**
 * Extract content from markdown file by heading
 */
async function extractByHeading(
  docManager: IDocumentManager,
  filePath: string,
  heading: string
): Promise<string | null> {
  try {
    console.log(`Attempting to extract heading "${heading}" from file: ${filePath}`);
    
    const fileModel = await docManager.services.contents.get(filePath, { content: true });
    if (fileModel.type !== 'file') {
      console.warn(`File ${filePath} is not a file type, got: ${fileModel.type}`);
      return null;
    }

    // Handle different content formats
    let content: string;
    if (typeof fileModel.content === 'string') {
      content = fileModel.content;
    } else if (fileModel.content && typeof fileModel.content === 'object') {
      // If content is an object, it might be the parsed JSON - we need the raw content
      console.warn(`File ${filePath} content is not a string:`, typeof fileModel.content);
      return null;
    } else {
      console.warn(`File ${filePath} has no content`);
      return null;
    }

    const lines = content.split('\n');
    
    console.log(`File has ${lines.length} lines`);
    console.log('Looking for headings in file:', lines.slice(0, 10).map((line, i) => `${i}: ${line}`));
    
    // Find the heading line - be more flexible with whitespace and matching
    const normalizedHeading = heading.trim().toLowerCase();
    let startIndex = -1;
    let headingLevel = 0;
    
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i].trim();
      const match = line.match(/^(#{1,6})\s+(.+)$/);
      
      if (match) {
        const lineHeading = match[2].trim().toLowerCase();
        console.log(`Found heading at line ${i}: "${match[2]}" (level ${match[1].length})`);
        
        if (lineHeading === normalizedHeading) {
          startIndex = i;
          headingLevel = match[1].length;
          console.log(`Matched heading "${heading}" at line ${i}`);
          break;
        }
      }
    }
    
    if (startIndex === -1) {
      console.warn(`Heading "${heading}" not found in ${filePath}`);
      console.log('Available headings:');
      lines.forEach((line, i) => {
        const match = line.match(/^(#{1,6})\s+(.+)$/);
        if (match) {
          console.log(`  Line ${i}: ${match[1]} ${match[2]}`);
        }
      });
      return null;
    }
    
    // Find the end of this section (next heading of same or higher level)
    let endIndex = lines.length;
    for (let i = startIndex + 1; i < lines.length; i++) {
      const line = lines[i].trim();
      const match = line.match(/^(#{1,6})\s/);
      
      if (match && match[1].length <= headingLevel) {
        endIndex = i;
        break;
      }
    }
    
    // Extract the content (excluding the heading itself)
    const sectionLines = lines.slice(startIndex + 1, endIndex);
    const extractedContent = sectionLines.join('\n').trim();
    
    console.log(`Extracted ${sectionLines.length} lines of content`);
    console.log('First 200 chars:', extractedContent.substring(0, 200));
    
    return extractedContent;
    
  } catch (error) {
    console.error(`Error extracting heading "${heading}" from ${filePath}:`, error);
    if (error instanceof SyntaxError && error.message.includes('JSON.parse')) {
      console.warn(`File ${filePath} may not exist or be accessible`);
    }
    return null;
  }
}

/**
 * Extract content from markdown file by block ID
 */
async function extractByBlockId(
  docManager: IDocumentManager,
  filePath: string,
  blockId: string
): Promise<string | null> {
  try {
    console.log(`Attempting to extract block ID "${blockId}" from file: ${filePath}`);
    
    const fileModel = await docManager.services.contents.get(filePath, { content: true });
    if (fileModel.type !== 'file') {
      console.warn(`File ${filePath} is not a file type, got: ${fileModel.type}`);
      return null;
    }

    // Handle different content formats
    let content: string;
    if (typeof fileModel.content === 'string') {
      content = fileModel.content;
    } else if (fileModel.content && typeof fileModel.content === 'object') {
      console.warn(`File ${filePath} content is not a string:`, typeof fileModel.content);
      return null;
    } else {
      console.warn(`File ${filePath} has no content`);
      return null;
    }

    const lines = content.split('\n');
    
    // Look for block ID marker: ^block-id at end of line or paragraph
    const blockIdPattern = new RegExp(`\\^${blockId.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\s*$`);
    let blockLineIndex = -1;
    
    console.log(`Looking for block ID pattern: ${blockIdPattern}`);
    
    for (let i = 0; i < lines.length; i++) {
      if (blockIdPattern.test(lines[i])) {
        blockLineIndex = i;
        console.log(`Found block ID "${blockId}" at line ${i}: "${lines[i]}"`);
        break;
      }
    }
    
    if (blockLineIndex === -1) {
      console.warn(`Block ID "${blockId}" not found in ${filePath}`);
      console.log('Available block IDs:');
      lines.forEach((line, i) => {
        const blockMatch = line.match(/\^([a-zA-Z0-9-_]+)\s*$/);
        if (blockMatch) {
          console.log(`  Line ${i}: ^${blockMatch[1]}`);
        }
      });
      return null;
    }
    
    // Extract the paragraph containing the block ID
    // Go backwards to find the start of the paragraph
    let startIndex = blockLineIndex;
    for (let i = blockLineIndex - 1; i >= 0; i--) {
      if (lines[i].trim() === '') {
        startIndex = i + 1;
        break;
      }
      if (i === 0) {
        startIndex = 0;
      }
    }
    
    // Go forwards to find the end of the paragraph
    let endIndex = blockLineIndex;
    for (let i = blockLineIndex + 1; i < lines.length; i++) {
      if (lines[i].trim() === '') {
        endIndex = i - 1;
        break;
      }
      if (i === lines.length - 1) {
        endIndex = i;
      }
    }
    
    // Extract the block content and remove the block ID marker
    const blockLines = lines.slice(startIndex, endIndex + 1);
    const blockContent = blockLines
      .map(line => line.replace(blockIdPattern, '').trimEnd())
      .join('\n')
      .trim();
    
    console.log(`Extracted block content (${blockLines.length} lines):`, blockContent.substring(0, 200));
    
    return blockContent;
    
  } catch (error) {
    console.error(`Error extracting block ID "${blockId}" from ${filePath}:`, error);
    if (error instanceof SyntaxError && error.message.includes('JSON.parse')) {
      console.warn(`File ${filePath} may not exist or be accessible`);
    }
    return null;
  }
}

/**
 * Extract a specific cell from a Jupyter notebook
 */
async function extractNotebookCell(
  docManager: IDocumentManager,
  filePath: string,
  cellIndex: number,
  cellType: 'code' | 'output' | 'markdown' | 'full' = 'full'
): Promise<{content: string, executionCount?: number} | null> {
  try {
    console.log(`Extracting cell ${cellIndex} (${cellType}) from notebook: ${filePath}`);
    
    const fileModel = await docManager.services.contents.get(filePath, { content: true });
    if (fileModel.type !== 'notebook') {
      console.warn(`File ${filePath} is not a notebook type, got: ${fileModel.type}`);
      return null;
    }

    // Parse notebook content
    let notebookData: any;
    if (typeof fileModel.content === 'string') {
      notebookData = JSON.parse(fileModel.content);
    } else {
      notebookData = fileModel.content;
    }

    if (!notebookData || !notebookData.cells || !Array.isArray(notebookData.cells)) {
      console.warn(`Invalid notebook structure in ${filePath}`);
      return null;
    }

    const cells = notebookData.cells;
    if (cellIndex < 0 || cellIndex >= cells.length) {
      console.warn(`Cell index ${cellIndex} out of range (0-${cells.length - 1}) in ${filePath}`);
      return null;
    }

    const cell = cells[cellIndex];
    const executionCount = cell.execution_count || undefined;
    
    console.log(`Found cell ${cellIndex}: type=${cell.cell_type}, execution_count=${executionCount}`);
    
    let content = '';
    
    if (cellType === 'code' || (cellType === 'full' && cell.cell_type === 'code')) {
      // Extract source code
      let source = '';
      if (typeof cell.source === 'string') {
        source = cell.source;
      } else if (Array.isArray(cell.source)) {
        source = cell.source.join('');
      }
      
      if (cellType === 'code') {
        content = source;
      } else {
        // Full cell - include both code and output
        content = source;
        if (cell.outputs && cell.outputs.length > 0) {
          content += '\n\n<!-- Output -->\n';
          content += extractCellOutputs(cell.outputs);
        }
      }
    } else if (cellType === 'output' && cell.cell_type === 'code') {
      // Extract only outputs
      if (cell.outputs && cell.outputs.length > 0) {
        content = extractCellOutputs(cell.outputs);
      } else {
        content = '(No output)';
      }
    } else if (cellType === 'markdown' || cell.cell_type === 'markdown') {
      // Extract markdown source
      if (typeof cell.source === 'string') {
        content = cell.source;
      } else if (Array.isArray(cell.source)) {
        content = cell.source.join('');
      }
    } else {
      console.warn(`Unsupported cell type or extraction type: cell_type=${cell.cell_type}, cellType=${cellType}`);
      return null;
    }
    
    console.log(`Extracted cell content (${content.length} chars):`, content.substring(0, 100));
    
    return { content: content.trim(), executionCount };
    
  } catch (error) {
    console.error(`Error extracting cell ${cellIndex} from ${filePath}:`, error);
    return null;
  }
}

/**
 * Extract text content from notebook cell outputs
 */
function extractCellOutputs(outputs: any[]): string {
  const outputTexts: string[] = [];
  
  for (const output of outputs) {
    if (output.output_type === 'stream') {
      // Stream output (print statements, etc.)
      let text = '';
      if (typeof output.text === 'string') {
        text = output.text;
      } else if (Array.isArray(output.text)) {
        text = output.text.join('');
      }
      if (text.trim()) {
        outputTexts.push(`[${output.name || 'stream'}]\n${text.trim()}`);
      }
    } else if (output.output_type === 'execute_result' || output.output_type === 'display_data') {
      // Execution results or display data
      if (output.data) {
        if (output.data['text/plain']) {
          let text = output.data['text/plain'];
          if (Array.isArray(text)) {
            text = text.join('');
          }
          outputTexts.push(`[result]\n${text.trim()}`);
        } else if (output.data['text/html']) {
          outputTexts.push(`[html]\n${output.data['text/html']}`);
        } else if (output.data['image/png']) {
          outputTexts.push(`[image: base64 PNG data]`);
        } else if (output.data['image/jpeg']) {
          outputTexts.push(`[image: base64 JPEG data]`);
        } else {
          outputTexts.push(`[data: ${Object.keys(output.data).join(', ')}]`);
        }
      }
    } else if (output.output_type === 'error') {
      // Error output
      const errorName = output.ename || 'Error';
      const errorValue = output.evalue || '';
      outputTexts.push(`[error: ${errorName}]\n${errorValue}`);
    }
  }
  
  return outputTexts.join('\n\n');
}

/**
 * Extract block content based on reference type
 */
async function extractBlockContent(
  docManager: IDocumentManager,
  sourceFile: string,
  blockRef: string
): Promise<ExtractedBlock> {
  const extractedAt = new Date();
  
  console.log(`Block embedding - extracting from "${sourceFile}" block/heading "${blockRef}"`);
  
  // First, resolve the file path
  const resolvedPath = await findFile(docManager, sourceFile);
  if (!resolvedPath) {
    console.warn(`Block embedding - could not find file: ${sourceFile}`);
    return {
      content: '',
      title: blockRef,
      sourceFile,
      blockRef,
      extractedAt,
      found: false
    };
  }
  
  console.log(`Block embedding - resolved "${sourceFile}" to "${resolvedPath}"`);
  
  // Check if this is a notebook cell reference: cell:N or cell:N:type
  const cellMatch = blockRef.match(/^cell:(\d+)(?::(code|output|markdown|full))?$/);
  if (cellMatch && resolvedPath.endsWith('.ipynb')) {
    const cellIndex = parseInt(cellMatch[1], 10);
    const cellType = (cellMatch[2] as 'code' | 'output' | 'markdown' | 'full') || 'full';
    
    console.log(`Notebook cell reference detected: cell ${cellIndex}, type ${cellType}`);
    
    const cellResult = await extractNotebookCell(docManager, resolvedPath, cellIndex, cellType);
    if (cellResult) {
      return {
        content: cellResult.content,
        title: `Cell ${cellIndex}${cellType !== 'full' ? `:${cellType}` : ''}`,
        sourceFile,
        blockRef,
        extractedAt,
        found: true,
        isNotebookCell: true,
        cellIndex,
        cellType,
        executionCount: cellResult.executionCount
      };
    } else {
      return {
        content: '',
        title: `Cell ${cellIndex}`,
        sourceFile,
        blockRef,
        extractedAt,
        found: false,
        isNotebookCell: true,
        cellIndex,
        cellType
      };
    }
  }
  
  // For non-notebook files or non-cell references, use existing logic
  // Determine if it's likely a block ID based on naming patterns
  // Block IDs typically use kebab-case, headings use normal text
  const isLikelyBlockId = /^[a-z0-9-_]+$/.test(blockRef) && blockRef.includes('-');
  
  let content: string | null = null;
  let title = blockRef;
  
  if (isLikelyBlockId) {
    // Try as block ID first
    console.log(`"${blockRef}" looks like a block ID, trying block extraction first`);
    content = await extractByBlockId(docManager, resolvedPath, blockRef);
    if (content === null) {
      console.log(`Block ID extraction failed, trying as heading`);
      content = await extractByHeading(docManager, resolvedPath, blockRef);
    }
    title = content !== null ? `Block: ${blockRef}` : blockRef;
  } else {
    // Try as heading first
    console.log(`"${blockRef}" looks like a heading, trying heading extraction first`);
    content = await extractByHeading(docManager, resolvedPath, blockRef);
    if (content === null) {
      console.log(`Heading extraction failed, trying as block ID`);
      content = await extractByBlockId(docManager, resolvedPath, blockRef);
      title = content !== null ? `Block: ${blockRef}` : blockRef;
    }
  }
  
  return {
    content: content || '',
    title,
    sourceFile,
    blockRef,
    extractedAt,
    found: content !== null
  };
}

/**
 * Parse block embeds from text, excluding those inside code blocks
 */
function parseBlockEmbeds(text: string): BlockEmbed[] {
  const embeds: BlockEmbed[] = [];
  
  // Find all code blocks (both ``` and ` inline code)
  const codeBlocks: Array<{start: number, end: number}> = [];
  
  // Find fenced code blocks (```)
  const fencedCodeRegex = /```[\s\S]*?```/g;
  let codeMatch;
  while ((codeMatch = fencedCodeRegex.exec(text)) !== null) {
    codeBlocks.push({
      start: codeMatch.index,
      end: codeMatch.index + codeMatch[0].length
    });
  }
  
  // Find inline code blocks (`)
  const inlineCodeRegex = /`[^`]+`/g;
  while ((codeMatch = inlineCodeRegex.exec(text)) !== null) {
    codeBlocks.push({
      start: codeMatch.index,
      end: codeMatch.index + codeMatch[0].length
    });
  }
  
  // Helper function to check if a position is inside a code block
  const isInCodeBlock = (position: number): boolean => {
    return codeBlocks.some(block => position >= block.start && position < block.end);
  };

  let match;
  BLOCK_EMBED_REGEX.lastIndex = 0;
  while ((match = BLOCK_EMBED_REGEX.exec(text)) !== null) {
    // Skip if this match is inside a code block
    if (isInCodeBlock(match.index)) {
      continue;
    }
    
    embeds.push({
      fullMatch: match[0],
      sourceFile: match[1].trim(),
      blockRef: match[2].trim(),
      displayTitle: match[3]?.trim(),
      startIndex: match.index,
      endIndex: match.index + match[0].length
    });
  }

  return embeds;
}

/**
 * Render an embedded block as markdown with a visual container
 */
function renderEmbedBlock(extractedBlock: ExtractedBlock, displayTitle?: string): string {
  const timestamp = extractedBlock.extractedAt.toLocaleString();
  const title = displayTitle || extractedBlock.title;
  
  if (!extractedBlock.found) {
    const statusIcon = extractedBlock.isNotebookCell ? '📓❌' : '❌';
    return `
> **${statusIcon} ${extractedBlock.sourceFile}#${extractedBlock.blockRef}**
> 
> *${extractedBlock.isNotebookCell ? 'Notebook cell' : 'Block'} not found*
`;
  }
  
  // Handle notebook cells with special formatting
  if (extractedBlock.isNotebookCell) {
    const cellTypeIcon = getCellTypeIcon(extractedBlock.cellType);
    const executionInfo = extractedBlock.executionCount !== undefined 
      ? ` *[${extractedBlock.executionCount}]*` 
      : '';
    
    const headerLine = `**${cellTypeIcon} ${extractedBlock.sourceFile}#${title}**${executionInfo} *(🕒 ${timestamp})*`;
    
    // Format notebook cell content with appropriate syntax highlighting
    let formattedContent = '';
    if (extractedBlock.cellType === 'code' || extractedBlock.cellType === 'full') {
      // Determine language from notebook metadata or default to python
      const language = 'python'; // Could be enhanced to detect from notebook metadata
      
      if (extractedBlock.cellType === 'full' && extractedBlock.content.includes('<!-- Output -->')) {
        // Split code and output for full cells
        const parts = extractedBlock.content.split('<!-- Output -->');
        formattedContent = `\`\`\`${language}\n${parts[0].trim()}\n\`\`\`\n\n**Output:**\n\`\`\`\n${parts[1].trim()}\n\`\`\``;
      } else {
        formattedContent = `\`\`\`${language}\n${extractedBlock.content.trim()}\n\`\`\``;
      }
    } else if (extractedBlock.cellType === 'output') {
      formattedContent = `\`\`\`\n${extractedBlock.content.trim()}\n\`\`\``;
    } else {
      // Markdown cell - render as-is
      formattedContent = extractedBlock.content.trim();
    }
    
    return `
---

${headerLine}

${formattedContent}

---
`;
  }
  
  // Original formatting for non-notebook blocks
  const statusIcon = '📄';
  const headerLine = `**${statusIcon} ${extractedBlock.sourceFile}#${title}** *(🕒 ${timestamp})*`;
  const contentLines = extractedBlock.content.split('\n').map(line => line.trim()).filter(line => line.length > 0);
  
  return `
---

${headerLine}

${contentLines.join('\n\n')}

---
`;
}

/**
 * Get appropriate icon for notebook cell type
 */
function getCellTypeIcon(cellType?: string): string {
  switch (cellType) {
    case 'code': return '📓💻';
    case 'output': return '📓📊';
    case 'markdown': return '📓📝';
    case 'full': return '📓';
    default: return '📓';
  }
}

/**
 * Generate a cell overview for a notebook file
 */
async function generateNotebookCellOverview(
  docManager: IDocumentManager,
  filePath: string
): Promise<string> {
  try {
    console.log(`Generating cell overview for notebook: ${filePath}`);
    
    const fileModel = await docManager.services.contents.get(filePath, { content: true });
    if (fileModel.type !== 'notebook') {
      return `Error: ${filePath} is not a notebook file.`;
    }

    // Parse notebook content
    let notebookData: any;
    if (typeof fileModel.content === 'string') {
      notebookData = JSON.parse(fileModel.content);
    } else {
      notebookData = fileModel.content;
    }

    if (!notebookData || !notebookData.cells || !Array.isArray(notebookData.cells)) {
      return `Error: Invalid notebook structure in ${filePath}`;
    }

    const cells = notebookData.cells;
    const overview: string[] = [];
    
    overview.push(`# 📓 Notebook Cell Overview: ${filePath}`);
    overview.push(`Total cells: ${cells.length}\n`);
    overview.push('| Index | Type | ID | Tags | Execution | Preview |');
    overview.push('|-------|------|----|----- |-----------|---------|');
    
    cells.forEach((cell: any, index: number) => {
      const cellType = cell.cell_type || 'unknown';
      const cellIcon = cellType === 'code' ? '💻' : cellType === 'markdown' ? '📝' : '❓';
      
      // Extract cell ID
      const cellId = cell.id || cell.metadata?.id || '-';
      
      // Extract tags
      const tags = cell.metadata?.tags || [];
      const tagString = tags.length > 0 ? tags.join(', ') : '-';
      
      // Execution count for code cells
      const executionCount = cell.execution_count !== null && cell.execution_count !== undefined 
        ? `[${cell.execution_count}]` 
        : '-';
      
      // Generate preview (first line of source)
      let preview = '';
      if (cell.source) {
        let sourceText = '';
        if (typeof cell.source === 'string') {
          sourceText = cell.source;
        } else if (Array.isArray(cell.source)) {
          sourceText = cell.source.join('');
        }
        
        const firstLine = sourceText.split('\n')[0]?.trim() || '';
        preview = firstLine.length > 40 ? firstLine.substring(0, 37) + '...' : firstLine;
        
        // Clean up markdown syntax for preview
        if (cellType === 'markdown') {
          preview = preview.replace(/^#+\s*/, '').replace(/\*\*/g, '');
        }
      }
      
      overview.push(`| ${index} | ${cellIcon} ${cellType} | \`${cellId}\` | ${tagString} | ${executionCount} | ${preview} |`);
    });
    
    overview.push('\n## 🔗 Embedding Examples:');
    overview.push('```');
    const fileName = filePath.split('/').pop() || filePath;
    overview.push(`![[${fileName}#cell:0]]        <!-- Full cell 0 -->`);
    overview.push(`![[${fileName}#cell:0:code]]   <!-- Code only from cell 0 -->`);
    overview.push(`![[${fileName}#cell:0:output]] <!-- Output only from cell 0 -->`);
    if (cells.some((cell: any) => cell.metadata?.tags?.length > 0)) {
      const taggedCell = cells.find((cell: any) => cell.metadata?.tags?.length > 0);
      const firstTag = taggedCell.metadata.tags[0];
      overview.push(`![[${fileName}#tag:${firstTag}]]   <!-- Cell with tag "${firstTag}" (future feature) -->`);
    }
    overview.push('```');
    
    return overview.join('\n');
    
  } catch (error) {
    console.error(`Error generating cell overview for ${filePath}:`, error);
    return `Error: Could not read notebook file ${filePath}`;
  }
}

/**
 * Plugin to handle block embedding in markdown files
 */
export const blockEmbeddingPlugin: JupyterFrontEndPlugin<void> = {
  id: '@jupyterlab/pkm-extension:block-embedding',
  description: 'Handle block embedding in markdown files',
  autoStart: true,
  requires: [
    IEditorTracker,
    IMarkdownViewerTracker,
    IDocumentManager,
    IRenderMimeRegistry
  ],
  optional: [ICommandPalette],
  activate: (
    app: JupyterFrontEnd,
    editorTracker: IEditorTracker,
    markdownTracker: IMarkdownViewerTracker,
    docManager: IDocumentManager,
    rendermime: IRenderMimeRegistry,
    palette: ICommandPalette | null
  ) => {
    console.log('Block embedding plugin activated');

    // Add print styles to the document
    const printStyles = document.createElement('style');
    printStyles.textContent = `
      /* Print-specific styles */
      @media print {
        /* Ensure embedded blocks don't break across pages */
        .pkm-embedded-block,
        hr + p + hr {
          page-break-inside: avoid;
          border: 1px solid #000 !important;
          margin: 0.5cm 0;
          padding: 0.3cm;
        }
        
        /* Style embedded block headers for print */
        .pkm-embedded-block-header {
          background-color: #f5f5f5 !important;
          -webkit-print-color-adjust: exact;
          color-adjust: exact;
        }
        
        /* Hide JupyterLab UI elements */
        .jp-Toolbar,
        .jp-SideBar,
        .jp-MenuBar,
        .jp-StatusBar {
          display: none !important;
        }
        
        /* Optimize spacing for print */
        body {
          margin: 0;
          padding: 1cm;
          font-size: 12pt;
          line-height: 1.4;
        }
        
        /* Code blocks styling for print */
        pre, code {
          font-size: 10pt;
          border: 1px solid #ccc;
          background-color: #f9f9f9 !important;
          -webkit-print-color-adjust: exact;
        }
        
        /* Ensure good contrast for print */
        * {
          color: #000 !important;
        }
        
        /* Headers styling */
        h1, h2, h3, h4, h5, h6 {
          page-break-after: avoid;
          margin-top: 0.8cm;
          margin-bottom: 0.4cm;
        }
        
        /* Prevent orphaned content */
        p, blockquote {
          orphans: 3;
          widows: 3;
        }
      }
      
      /* Screen styles for embedded blocks */
      @media screen {
        .pkm-embedded-block {
          border: 1px solid var(--jp-border-color2);
          border-radius: 4px;
          margin: 1rem 0;
          background: var(--jp-layout-color0);
        }
      }
    `;
    document.head.appendChild(printStyles);

    // Override the default markdown renderer to process block embeds
    const defaultFactory = rendermime.getFactory('text/markdown');
    if (defaultFactory) {
      rendermime.removeMimeType('text/markdown');
      rendermime.addFactory({
        safe: true,
        mimeTypes: ['text/markdown'],
        createRenderer: (options: IRenderMime.IRendererOptions) => {
          const renderer = defaultFactory.createRenderer(options);
          const originalRenderModel = renderer.renderModel.bind(renderer);
          
          renderer.renderModel = async (model: IRenderMime.IMimeModel) => {
            // Get the markdown source
            let source: string;
            if (typeof model.data === 'string') {
              source = model.data;
            } else if (model.data['text/markdown']) {
              source = model.data['text/markdown'] as string;
            } else if (model.data['text/plain']) {
              source = model.data['text/plain'] as string;
            } else {
              return originalRenderModel(model);
            }
            
            // Parse block embeds
            const embeds = parseBlockEmbeds(source);
            
            if (embeds.length === 0) {
              return originalRenderModel(model);
            }
            
            console.log(`Found ${embeds.length} block embeds`);
            
            // Process embeds
            let processedSource = source;
            let offset = 0;
            
            for (const embed of embeds) {
              console.log('Processing embed:', embed.sourceFile, '#', embed.blockRef);
              
              const extractedBlock = await extractBlockContent(
                docManager,
                embed.sourceFile,
                embed.blockRef
              );
              
              const embedHtml = renderEmbedBlock(extractedBlock, embed.displayTitle);
              
              const adjustedStart = embed.startIndex + offset;
              const adjustedEnd = embed.endIndex + offset;
              
              processedSource = 
                processedSource.slice(0, adjustedStart) +
                embedHtml +
                processedSource.slice(adjustedEnd);
              
              offset += embedHtml.length - embed.fullMatch.length;
            }
            
            // Update the model with processed source
            const processedModel = {
              ...model,
              data: typeof model.data === 'string' ? { 'text/markdown': processedSource } : {
                ...model.data,
                'text/markdown': processedSource
              },
              metadata: model.metadata || {},
              trusted: model.trusted !== undefined ? model.trusted : true
            };
            
            return originalRenderModel(processedModel);
          };
          
          return renderer;
        }
      }, 0);
    }

    // Add command to print markdown with embedded blocks
    app.commands.addCommand('pkm:print-markdown-with-embeds', {
      label: 'PKM: Print Markdown Preview',
      caption: 'Print the current markdown document with all embedded blocks rendered',
      isEnabled: () => {
        return markdownTracker.currentWidget !== null;
      },
      execute: async () => {
        const currentWidget = markdownTracker.currentWidget;
        if (!currentWidget) {
          console.warn('No markdown document is currently active');
          return;
        }

        try {
          // Get the rendered content from the markdown viewer
          const renderedContent = currentWidget.content.node;
          const documentTitle = currentWidget.title.label || 'Markdown Document';
          
          // Create a new window for printing
          const printWindow = window.open('', '_blank', 'width=800,height=600');
          if (!printWindow) {
            alert('Pop-up blocked. Please allow pop-ups and try again.');
            return;
          }

          // Get the current page's stylesheets to maintain formatting
          const stylesheets = Array.from(document.styleSheets)
            .map(sheet => {
              try {
                if (sheet.href) {
                  return `<link rel="stylesheet" href="${sheet.href}">`;
                } else if (sheet.ownerNode) {
                  return `<style>${Array.from(sheet.cssRules).map(rule => rule.cssText).join('\n')}</style>`;
                }
                return '';
              } catch (e) {
                // Cross-origin stylesheets might not be accessible
                return sheet.href ? `<link rel="stylesheet" href="${sheet.href}">` : '';
              }
            })
            .join('\n');

          // Write the print document
          printWindow.document.write(`
            <!DOCTYPE html>
            <html>
            <head>
              <meta charset="utf-8">
              <title>Print: ${documentTitle}</title>
              ${stylesheets}
              <style>
                /* Additional print-specific styles */
                @media print {
                  @page {
                    margin: 2cm;
                    size: A4;
                  }
                  
                  body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    line-height: 1.6;
                    color: #000;
                    background: #fff;
                  }
                  
                  /* Embedded block styling */
                  hr + p + hr,
                  .pkm-embedded-block {
                    page-break-inside: avoid;
                    border: 2px solid #333 !important;
                    margin: 1cm 0;
                    padding: 0.5cm;
                    background: #f9f9f9 !important;
                    -webkit-print-color-adjust: exact;
                  }
                  
                  /* Code styling */
                  pre {
                    background: #f5f5f5 !important;
                    border: 1px solid #ccc !important;
                    padding: 0.5cm;
                    font-size: 9pt;
                    overflow-wrap: break-word;
                    white-space: pre-wrap;
                  }
                  
                  code {
                    background: #f0f0f0 !important;
                    padding: 0.1cm 0.2cm;
                    border-radius: 2px;
                    font-size: 10pt;
                  }
                  
                  /* Typography */
                  h1 { font-size: 20pt; margin-top: 1cm; }
                  h2 { font-size: 16pt; margin-top: 0.8cm; }
                  h3 { font-size: 14pt; margin-top: 0.6cm; }
                  h4, h5, h6 { font-size: 12pt; margin-top: 0.4cm; }
                  
                  p { margin: 0.3cm 0; }
                  
                  /* Table styling */
                  table {
                    border-collapse: collapse;
                    width: 100%;
                    margin: 0.5cm 0;
                  }
                  
                  th, td {
                    border: 1px solid #333;
                    padding: 0.2cm;
                    text-align: left;
                  }
                  
                  th {
                    background: #e0e0e0 !important;
                    font-weight: bold;
                  }
                }
                
                /* Hide elements that shouldn't be printed */
                .jp-Toolbar,
                .jp-SideBar,
                .jp-MenuBar,
                .jp-StatusBar,
                .jp-Activity,
                .jp-MainAreaWidget-toolbar {
                  display: none !important;
                }
              </style>
            </head>
            <body>
              <div class="print-content">
                ${renderedContent.innerHTML}
              </div>
              <script>
                // Auto-print when loaded and close after printing
                window.onload = function() {
                  setTimeout(function() {
                    window.print();
                    window.onafterprint = function() {
                      window.close();
                    };
                  }, 1000);
                };
              </script>
            </body>
            </html>
          `);

          printWindow.document.close();

        } catch (error) {
          console.error('Error printing markdown document:', error);
          alert('Error occurred while preparing document for printing. Check the console for details.');
        }
      }
    });

    // Add command to show notebook cell overview
    app.commands.addCommand('pkm:show-notebook-cell-overview', {
      label: 'PKM: Show Notebook Cell Overview',
      caption: 'Show an overview of all cells in the current notebook',
      execute: async () => {
        // Get the currently active notebook file
        const currentWidget = app.shell.currentWidget;
        let notebookPath = '';
        
        if (currentWidget && (currentWidget as any).context?.path) {
          const path = (currentWidget as any).context.path;
          if (path.endsWith('.ipynb')) {
            notebookPath = path;
          }
        }
        
        if (!notebookPath) {
          // If no notebook is currently open, prompt user for a path
          const result = prompt('Enter notebook path:', '');
          if (result) {
            notebookPath = result;
          } else {
            return;
          }
        }
        
        try {
          const overview = await generateNotebookCellOverview(docManager, notebookPath);
          
          // Create a widget to display the overview
          const widget = new Widget();
          widget.addClass('pkm-notebook-overview');
          widget.title.label = `Cell Overview: ${notebookPath.split('/').pop()}`;
          widget.title.closable = true;
          
          // Create markdown content area
          const content = document.createElement('div');
          content.style.cssText = `
            padding: 16px;
            font-family: var(--jp-content-font-family);
            overflow-y: auto;
            height: 100%;
          `;
          
          // Render the overview as markdown
          const markdownRenderer = rendermime.createRenderer('text/markdown');
          
          // Create a simple model object with required properties
          const modelData = { 'text/markdown': overview };
          const modelMetadata = {};
          let modelTrusted = true;
          
          const model: IRenderMime.IMimeModel = {
            data: modelData,
            metadata: modelMetadata,
            trusted: modelTrusted,
            setData: (options: any) => {
              // Implementation for setData method (required by interface)
              Object.assign(modelData, options.data || {});
              Object.assign(modelMetadata, options.metadata || {});
              if (options.trusted !== undefined) {
                modelTrusted = options.trusted;
              }
            }
          };
          
          markdownRenderer.renderModel(model).then(() => {
            content.appendChild(markdownRenderer.node);
          });
          
          widget.node.appendChild(content);
          
          // Show the widget
          const main = new MainAreaWidget({ content: widget });
          main.title.label = widget.title.label;
          main.title.closable = true;
          
          app.shell.add(main, 'main');
          app.shell.activateById(main.id);
          
        } catch (error) {
          console.error('Error showing notebook cell overview:', error);
          alert(`Error: Could not read notebook file ${notebookPath}`);
        }
      }
    });
    
    // Option 1: Enhanced HTML with Word-specific formatting
// Add this as a new command alongside your existing print command

app.commands.addCommand('pkm:export-to-word', {
  label: 'PKM: Export to Word (.docx)',
  caption: 'Export the current markdown document with embedded blocks to Word format',
  isEnabled: () => {
    return markdownTracker.currentWidget !== null;
  },
  execute: async () => {
    const currentWidget = markdownTracker.currentWidget;
    if (!currentWidget) {
      console.warn('No markdown document is currently active');
      return;
    }

    try {
      // Get the rendered content
      const renderedContent = currentWidget.content.node;
      const documentTitle = currentWidget.title.label || 'Markdown Document';
      
      // Generate Word-compatible HTML
      const wordHtml = generateWordCompatibleHtml(renderedContent, documentTitle);
      
      // Create and download the file
      const blob = new Blob([wordHtml], { 
        type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' 
      });
      
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${documentTitle.replace(/[^a-z0-9]/gi, '_')}.doc`; // .doc extension for better Word compatibility
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      
    } catch (error) {
      console.error('Error exporting to Word:', error);
      alert('Error occurred while exporting to Word format. Check the console for details.');
    }
  }
});

// Helper function to generate Word-compatible HTML
function generateWordCompatibleHtml(contentNode: HTMLElement, title: string): string {
  // Clone the content to avoid modifying the original
  const clonedContent = contentNode.cloneNode(true) as HTMLElement;
  
  // Clean up JupyterLab-specific elements
  const elementsToRemove = clonedContent.querySelectorAll(
    '.jp-Toolbar, .jp-SideBar, .jp-MenuBar, .jp-StatusBar, .jp-Activity'
  );
  elementsToRemove.forEach(el => el.remove());
  
  // Convert embedded blocks to Word-friendly format
  const embeddedBlocks = clonedContent.querySelectorAll('hr + p + hr');
  embeddedBlocks.forEach(block => {
    const container = document.createElement('div');
    container.style.cssText = `
      border: 2px solid #333;
      margin: 20px 0;
      padding: 15px;
      background-color: #f9f9f9;
      page-break-inside: avoid;
    `;
    
    // Move content into the container
    const parent = block.parentNode;
    if (parent) {
      parent.insertBefore(container, block);
      container.appendChild(block);
    }
  });
  
  return `
    <html xmlns:o="urn:schemas-microsoft-com:office:office"
          xmlns:w="urn:schemas-microsoft-com:office:word"
          xmlns="http://www.w3.org/TR/REC-html40">
    <head>
      <meta charset="utf-8">
      <title>${title}</title>
      <!--[if gte mso 9]>
      <xml>
        <w:WordDocument>
          <w:View>Print</w:View>
          <w:Zoom>90</w:Zoom>
          <w:DoNotPromptForConvert/>
          <w:DoNotShowInsertionsAndDeletions/>
        </w:WordDocument>
      </xml>
      <![endif]-->
      <style>
        /* Word-compatible styles */
        body {
          font-family: 'Times New Roman', serif;
          font-size: 12pt;
          line-height: 1.5;
          margin: 1in;
        }
        
        h1 { font-size: 18pt; font-weight: bold; margin-top: 24pt; margin-bottom: 12pt; }
        h2 { font-size: 16pt; font-weight: bold; margin-top: 18pt; margin-bottom: 6pt; }
        h3 { font-size: 14pt; font-weight: bold; margin-top: 12pt; margin-bottom: 6pt; }
        h4, h5, h6 { font-size: 12pt; font-weight: bold; margin-top: 12pt; margin-bottom: 3pt; }
        
        p { margin-top: 6pt; margin-bottom: 6pt; }
        
        /* Code blocks */
        pre {
          font-family: 'Courier New', monospace;
          font-size: 10pt;
          background-color: #f5f5f5;
          border: 1px solid #ccc;
          padding: 12pt;
          margin: 12pt 0;
          white-space: pre-wrap;
        }
        
        code {
          font-family: 'Courier New', monospace;
          font-size: 10pt;
          background-color: #f0f0f0;
          padding: 2pt 4pt;
        }
        
        /* Embedded blocks */
        .embedded-block {
          border: 2px solid #333;
          margin: 20px 0;
          padding: 15px;
          background-color: #f9f9f9;
          page-break-inside: avoid;
        }
        
        /* Tables */
        table {
          border-collapse: collapse;
          width: 100%;
          margin: 12pt 0;
        }
        
        th, td {
          border: 1px solid #333;
          padding: 6pt;
          text-align: left;
        }
        
        th {
          background-color: #e0e0e0;
          font-weight: bold;
        }
        
        /* Lists */
        ul, ol {
          margin: 6pt 0;
          padding-left: 24pt;
        }
        
        li {
          margin: 3pt 0;
        }
        
        /* Blockquotes */
        blockquote {
          margin: 12pt 24pt;
          padding-left: 12pt;
          border-left: 3pt solid #ccc;
          font-style: italic;
        }
      </style>
    </head>
    <body>
      ${clonedContent.innerHTML}
    </body>
    </html>
  `;
}

    // Add commands to command palette
    if (palette) {
      palette.addItem({
        command: 'pkm:print-markdown-with-embeds',
        category: 'PKM'
      });
      
      palette.addItem({
        command: 'pkm:show-notebook-cell-overview',
        category: 'PKM'
      });

      palette.addItem({
        command: 'pkm:export-to-word',
        category: 'PKM'
      });
    }
    // Add context menu item for print command
    app.contextMenu.addItem({
      command: 'pkm:print-markdown-with-embeds',
      selector: '.jp-MarkdownViewer',
      rank: 500 // Controls position in context menu
    });

    app.contextMenu.addItem({
      command: 'pkm:export-to-word',
      selector: '.jp-MarkdownViewer',
      rank: 501
    });
  }
};