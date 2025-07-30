import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

/**
 * Minimal PKM extension for testing
 */
const extension: JupyterFrontEndPlugin<void> = {
  id: '@jupyterlab/pkm-extension:minimal',
  description: 'Minimal PKM extension for testing',
  autoStart: true,
  activate: (app: JupyterFrontEnd) => {
    console.log('🎉 PKM Extension Loaded Successfully!');
    
    // Add a simple command to test
    app.commands.addCommand('pkm:test', {
      label: 'PKM Test Command',
      execute: () => {
        console.log('PKM Test Command executed!');
        alert('PKM Extension is working!');
      }
    });
  }
};

export default extension;