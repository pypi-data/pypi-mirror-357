# Known Issues & Future Development

## 🐛 Current Issues (Post-PyPI Publication)

### Workspace Loading Issues
**Status**: Identified, needs investigation  
**Severity**: High  
**Description**: After publishing to PyPI and installing in JupyterLab Desktop, there are issues with:
- Opening workspace properly
- Source view/preview focus management
- Extension initialization in production environment

**Potential Causes**:
- Development vs production environment differences
- Extension loading order in JupyterLab Desktop
- File watcher/focus detection conflicts
- State management during startup

**Next Steps**:
- Test in isolated environment with clean JupyterLab installation
- Debug extension loading sequence
- Review markdown preview toggle logic for production builds
- Check for console errors during workspace initialization

### Backlinks Index Not Built on Startup ✅ **FIXED**
**Status**: **FIXED** - Index built when backlinks panel opens  
**Severity**: High  
**Description**: The wikilink index (`wikilink-index.json`) was only built when:
1. A new markdown file was created
2. The backlinks panel was explicitly opened
3. Manual index rebuild was triggered

This meant that existing wikilinks in a folder weren't detected on first open.

**Root Cause**: Index building was moved to main extension startup, but this caused timing issues.

**Fix Applied**: 
- Reverted to JupyterLite approach: index is built when backlinks panel is first opened
- Index building happens automatically when panel loads if index doesn't exist
- All existing files are properly indexed when panel opens for the first time
- File watching updates index when files are saved


### Preview/Source Toggle Focus Issues
**Status**: Intermittent, needs refinement  
**Severity**: Medium  
**Description**: The source/preview toggle sometimes gets out of sync when multiple markdown files are open
- Button state doesn't always reflect current file mode
- Toggle affects wrong file in some scenarios

**Investigation Areas**:
- `app.shell.currentWidget` reliability
- Widget focus detection timing
- Multiple file tracking logic

## 🔄 Development Environment vs Production

### Differences Observed
- **Development**: Extension works reliably with `jupyter labextension develop`
- **Production**: Issues appear after `pip install` from PyPI
- **Possible Factor**: Build process differences or packaging issues

### Debug Strategy
1. Compare development vs production builds
2. Test installation from local wheel file
3. Check extension loading logs
4. Verify all assets are properly bundled

## 📋 Future Improvements

### High Priority
- [ ] Fix workspace loading issues
- [ ] Improve source/preview toggle reliability
- [ ] Add error handling for startup failures
- [ ] Create diagnostic tools for troubleshooting

### Low Priority
- [ ] Performance optimization for large workspaces
- [ ] Better wikilink auto-completion
- [ ] Enhanced search functionality
- [ ] Mobile/responsive design improvements
- [ ] Themes and customization
- [ ] Advanced PKM features (tags, graph view)
- [ ] Integration with external tools
- [ ] Export/import functionality

## 🔧 Debugging Tools Needed

### Extension Diagnostics
- Add console logging for extension lifecycle
- Create health check command
- Monitor widget focus changes
- Track file opening/closing events

### User Reporting
- Standardized issue template
- System info collection
- Extension version verification
- Conflict detection with other extensions

## 📝 Version History & Issues

### v0.1.0 (Current)
- ✅ Core PKM features working in development
- ❌ Workspace loading issues in production
- ❌ Focus management needs improvement

### v0.1.1 (Planned)
- 🎯 Fix production environment issues
- 🎯 Improve focus detection reliability
- 🎯 Add better error handling

