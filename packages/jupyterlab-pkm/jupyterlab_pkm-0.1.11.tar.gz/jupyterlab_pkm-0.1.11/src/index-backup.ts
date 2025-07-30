import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import { IEditorTracker } from '@jupyterlab/fileeditor';
import { IMarkdownViewerTracker } from '@jupyterlab/markdownviewer';
import { INotebookTracker } from '@jupyterlab/notebook';

import { markdownPreviewPlugin } from './markdown-preview';
import { wikilinkPlugin } from './wikilinks';
import { searchPlugin } from './search';
import { backlinksPlugin } from './backlinks';
import { notebookEmbedPlugin } from './notebook-embed';
import { blockEmbeddingPlugin } from './block-embedding';
import { codeCopyPlugin } from './code-copy';
import { welcomePlugin } from './welcome';

/**
 * The main extension that combines all PKM features
 */
const extension: JupyterFrontEndPlugin<void> = {
  id: '@jupyterlab/pkm-extension:plugin',
  description: 'Personal Knowledge Management extension for JupyterLab Desktop',
  autoStart: true,
  requires: [IEditorTracker, IMarkdownViewerTracker, INotebookTracker],
  activate: (
    app: JupyterFrontEnd,
    editorTracker: IEditorTracker,
    markdownTracker: IMarkdownViewerTracker,
    notebookTracker: INotebookTracker
  ) => {
    console.log('JupyterLab PKM extension activated');
  }
};

/**
 * Export all plugins
 */
export default [
  extension,
  welcomePlugin,
  markdownPreviewPlugin,
  wikilinkPlugin,
  blockEmbeddingPlugin,
  codeCopyPlugin,
  searchPlugin,
  backlinksPlugin,
  notebookEmbedPlugin
];