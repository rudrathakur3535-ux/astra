/**
 * Preload Script for Astra OS Electron Desktop App.
 * Securely exposes window.astraAPI to the React frontend process using contextBridge.
 */

const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('astraAPI', {
  getVersion: () => ipcRenderer.invoke('astra:get-version'),
  pingBackend: () => ipcRenderer.invoke('astra:ping-backend'),
  sendIPCMessage: (channel, data) => ipcRenderer.send(channel, data),
  onIPCMessage: (channel, callback) => {
    ipcRenderer.on(channel, (event, ...args) => callback(...args));
  }
});
