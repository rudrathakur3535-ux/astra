/**
 * Main Process for Astra OS Electron Desktop App.
 * Controls window management, native OS integrations, and backend communication.
 */

const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');

let mainWindow;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1440,
    height: 900,
    minWidth: 1024,
    minHeight: 700,
    title: 'Astra OS — Personal AI Operating System',
    backgroundColor: '#0f172a',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true,
      sandbox: true
    }
  });

  // Load backend developer dashboard / React desktop application URL
  const backendUrl = process.env.ASTRA_API_URL || 'http://localhost:8000/dashboard';
  mainWindow.loadURL(backendUrl).catch(() => {
    mainWindow.loadFile(path.join(__dirname, 'src', 'index.html'));
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

app.whenReady().then(() => {
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});

// IPC Handler Registrations
ipcMain.handle('astra:get-version', () => '1.0.0-desktop');
ipcMain.handle('astra:ping-backend', async () => {
  return { status: 'healthy', timestamp: Date.now() };
});
