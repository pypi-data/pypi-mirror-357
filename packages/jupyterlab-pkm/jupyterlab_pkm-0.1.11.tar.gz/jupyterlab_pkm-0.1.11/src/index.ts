import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';
import { ICommandPalette, IThemeManager } from '@jupyterlab/apputils';
import { IEditorTracker } from '@jupyterlab/fileeditor';
import { IMarkdownViewerTracker } from '@jupyterlab/markdownviewer';
import { INotebookTracker } from '@jupyterlab/notebook';

// Import CSS directly - this ensures it's loaded with the extension
import '../style/index.css';

// Adding plugins back one by one
import { markdownPreviewPlugin } from './markdown-preview';
import { wikilinkPlugin } from './wikilinks';
import { searchPlugin } from './search';
import { backlinksPlugin } from './backlinks';
import { blockEmbeddingPlugin } from './block-embedding';
import { notebookEmbedPlugin } from './notebook-embed';
import { codeCopyPlugin } from './code-copy';
import { welcomePlugin } from './welcome'; // Still causes issues

/**
 * Theme plugin that registers and automatically applies the PKM theme
 */
// in your index.ts

const themePlugin: JupyterFrontEndPlugin<void> = {
  id: '@jupyterlab/pkm-extension:theme',
  // Change the description to reflect it's a light theme
  description: 'PKM Solarized Light Theme - Inspired by the Solarized Light color palette.',
  autoStart: true,
  requires: [IThemeManager],
  activate: (app: JupyterFrontEnd, manager: IThemeManager) => {
    console.log('🎨 PKM Theme plugin activated');
    
    // Use a name that reflects the theme
    const themeName = 'PKM Solarized Light'; // <-- CHANGE THIS
    
    // Register the theme correctly
    manager.register({
      name: themeName,
      displayName: 'PKM Solarized Light', // <-- CHANGE THIS
      isLight: true, // <-- SET THIS TO TRUE
      themeScrollbars: true,
      load: () => {
        // CSS is already loaded via import at the top of this file
        return Promise.resolve();
      },
      unload: () => {
        return Promise.resolve(undefined);
      }
    });

    // Make sure this logic uses the new name
    if (manager.theme !== themeName) {
      manager.setTheme(themeName).catch(error => {
        console.warn('Failed to set PKM theme:', error);
      });
    }

    console.log(`🎨 PKM Theme "${themeName}" registered and activated`);
  }
};

/**
 * The main extension that combines all PKM features
 */
const extension: JupyterFrontEndPlugin<void> = {
  id: '@jupyterlab/pkm-extension:plugin',
  description: 'Personal Knowledge Management extension for JupyterLab Desktop',
  autoStart: true,
  requires: [ICommandPalette, IEditorTracker, IMarkdownViewerTracker, INotebookTracker],
  activate: (
    app: JupyterFrontEnd,
    palette: ICommandPalette,
    editorTracker: IEditorTracker,
    markdownTracker: IMarkdownViewerTracker,
    notebookTracker: INotebookTracker
  ) => {
    console.log('🎉 JupyterLab PKM extension activated');
    
    // Add a test command to verify it's working
    const testCommand = 'pkm:test-full';
    app.commands.addCommand(testCommand, {
      label: 'PKM: Test Full Extension',
      execute: () => {
        console.log('Full PKM Extension is working!');
        alert('Full PKM Extension loaded successfully!');
      }
    });
    palette.addItem({
      command: testCommand,
      category: 'PKM'
    });

    // Add command to manually switch to PKM theme
    const themeCommand = 'pkm:apply-theme';
    app.commands.addCommand(themeCommand, {
      label: 'PKM: Apply PKM Theme',
      execute: () => {
        console.log('Manually applying PKM theme...');
        // The theme is automatically applied by the theme plugin
        alert('PKM Theme should already be active! Check Settings → Theme if you need to switch themes.');
      }
    });
    palette.addItem({
      command: themeCommand,
      category: 'PKM'
    });
  }
};

/**
 * Export all plugins
 */
export default [
  themePlugin,      // Load theme first
  extension,
  welcomePlugin,
  markdownPreviewPlugin,
  wikilinkPlugin,
  searchPlugin,
  backlinksPlugin,
  blockEmbeddingPlugin,
  notebookEmbedPlugin,
  codeCopyPlugin
];