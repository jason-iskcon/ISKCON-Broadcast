
# ISKCON-Broadcast Development Tasks Summary

## **Core Objectives**
1. **Low Hanging Fruit Improvements** - Infrastructure & code quality fixes
2. **Camera Stubbing** - Work without hardware (no changes to `camera.py`)
3. **Testing Framework** - Match ISKCON-Translate standards
4. **Plugin Architecture** - Support multiple camera types

---

## **Task Breakdown**

### **Phase 1: Camera Plugin Architecture** 
- [ ] Create `camera_interface.py` - Abstract base class
- [ ] Create `camera_registry.py` - Plugin registry system  
- [ ] Create `cameras/ip_camera.py` - Wrapper for existing `camera.py` (no changes to original)
- [ ] Create `cameras/mock_camera.py` - Development stub (video files, static images, generated frames)
- [ ] Update `video_stream.py` - Minimal changes to use registry
- [ ] Extend `mode_config.yaml` - Add camera `type` field

### **Phase 2: Testing Framework**
- [ ] Create `tests/` directory structure (unit, sys, perf)
- [ ] Create `conftest.py` - Shared fixtures  
- [ ] Unit tests: Camera interface, display helpers, config loading
- [ ] System tests: End-to-end orchestration workflows
- [ ] Performance tests: Frame rate, memory usage, timing accuracy
- [ ] Add `codecov.yml` for coverage reporting

### **Phase 3: Infrastructure Improvements**
- [ ] Create `requirements.txt` - Dependency management
- [ ] Add configuration validation (YAML schema)
- [ ] Improve error handling in main loops
- [ ] Replace magic numbers with constants
- [ ] Fix global state issues (`display_frame`)
- [ ] Add thread safety for camera frame access
- [ ] Standardize logging patterns

---

## **Key Constraints**
✅ **Never touch `camera.py`** - Ensures easy hardware switching  
✅ **Plugin-based** - Support multiple camera types via config  
✅ **Match ISKCON-Translate standards** - Same test structure & quality  

## **Immediate Benefits**
- Work without camera hardware
- Easy camera type switching via config
- Comprehensive test coverage
- Better code maintainability
- CI/CD ready codebase

**Which phase would you like to start with?**
