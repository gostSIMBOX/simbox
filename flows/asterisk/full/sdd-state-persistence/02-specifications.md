# 02-Specifications

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│               State Persistence Layer                        │
├─────────────────┬─────────────────┬─────────────────────────┤
│  Core Storage   │  Device Info    │   Mutex Management      │
│  (share.c)      │  (share.c)      │   (share.c)             │
│                 │                 │                         │
│  - getfilei     │  - readpvtinfo  │  - ast_mutex_lock_pvt   │
│  - putfilei     │  - writepvtinfo │  - ast_mutex_unlock_pvt │
│  - getfiles     │  - readpvtlimits│  - mutex_trylock_pvt_e  │
│  - putfiles     │  - writepvtlimits│                        │
│                 │  - writepvtstate│                         │
└─────────────────┴─────────────────┴─────────────────────────┘
```

## File Storage Format

### Path Structure
```
/var/svistok/
├── imsi/
│   ├── 250000000.balance
│   ├── 250000000.imsi
│   ├── 250000000.imei
│   └── 250000000.state
├── device/
│   ├── dongle0.balance
│   └── dongle0.limits
└── global/
    ├── settings.conf
    └── version
```

### File Content Format
- **Integer files**: Plain text decimal number
  ```
  12345
  ```
- **String files**: Plain text string
  ```
  MTS-RUS
  ```

## Core Storage Operations

### Read Integer
```c
int getfilei(char* devtype, char* fileitem, char* filetype, int *value)
{
    char filename[128];
    char path[64] = "/var/svistok/";
    
    // Build path: /var/svistok/{devtype}/{fileitem}.{filetype}
    strcpy(filename, path);
    strcat(filename, devtype);
    strcat(filename, "/");
    strcat(filename, fileitem);
    strcat(filename, ".");
    strcat(filename, filetype);
    
    FILE* pFile = fopen(filename, "r");
    if (pFile != NULL) {
        fscanf(pFile, "%d", value);
        fclose(pFile);
        return 1;  // Success
    }
    return 0;  // File not found
}
```

### Write Integer
```c
int putfilei(char* devtype, char* fileitem, char* filetype, int value)
{
    char filename[128];
    char path[64] = "/var/svistok/";
    
    // Build path
    strcpy(filename, path);
    strcat(filename, devtype);
    strcat(filename, "/");
    strcat(filename, fileitem);
    strcat(filename, ".");
    strcat(filename, filetype);
    
    FILE* pFile = fopen(filename, "w");
    if (pFile != NULL) {
        fprintf(pFile, "%d", value);
        fclose(pFile);
        return 1;  // Success
    }
    return 0;  // Error
}
```

### Read String
```c
int getfiles(char* devtype, char* fileitem, char* filetype, char *value)
{
    char filename[128];
    char path[64] = "/var/svistok/";
    
    strcpy(filename, path);
    strcat(filename, devtype);
    strcat(filename, "/");
    strcat(filename, fileitem);
    strcat(filename, ".");
    strcat(filename, filetype);
    
    FILE* pFile = fopen(filename, "r");
    if (pFile != NULL) {
        fgets(value, 256, pFile);
        fclose(pFile);
        return 1;
    }
    return 0;
}
```

### Write String
```c
int putfiles(char* devtype, char* fileitem, char* filetype, char* value)
{
    char filename[128];
    char path[64] = "/var/svistok/";
    
    strcpy(filename, path);
    strcat(filename, devtype);
    strcat(filename, "/");
    strcat(filename, fileitem);
    strcat(filename, ".");
    strcat(filename, filetype);
    
    FILE* pFile = fopen(filename, "w");
    if (pFile != NULL) {
        fprintf(pFile, "%s", value);
        fclose(pFile);
        return 1;
    }
    return 0;
}
```

### Read/Write with CLI Output
```c
int putgetfilei(char putget, char* devtype, char* fileitem, 
                char* filetype, int value, struct ast_cli_args* a)
{
    if (putget == 'g') {
        // Get value
        if (getfilei(devtype, fileitem, filetype, &value)) {
            if (a) ast_cli(a->fd, "%d\n", value);
            return 1;
        }
    } else {
        // Put value
        if (putfilei(devtype, fileitem, filetype, value)) {
            if (a) ast_cli(a->fd, "OK\n");
            return 1;
        }
    }
    return 0;
}
```

## Device Info Persistence

### Read Device Info
```c
void readpvtinfo(struct pvt* pvt)
{
    char imsi[32];
    
    // Read balance
    getfilei("imsi", pvt->imsi, "balance", &PVT_STAT(pvt, balance));
    
    // Read ballast (balance offset)
    getfiles("imsi", pvt->imsi, "ballast", PVT_STAT(pvt, ballast));
    
    // Read phone number
    getfiles("imsi", pvt->imsi, "number", PVT_STAT(pvt, number));
    
    // Read provider
    getfiles("imsi", pvt->imsi, "provider", pvt->provider_name);
}
```

### Write Device Info
```c
void writepvtinfo(struct pvt* pvt)
{
    // Write balance
    putfilei("imsi", pvt->imsi, "balance", PVT_STAT(pvt, balance));
    
    // Write phone number
    putfiles("imsi", pvt->imsi, "number", PVT_STAT(pvt, number));
}
```

## Device Limits Persistence

### Read Limits
```c
void readpvtlimits(struct pvt* pvt)
{
    // Read call limits
    getfilei("imsi", pvt->imsi, "limit0", &PVT_STAT(pvt, limit[0]));
    getfilei("imsi", pvt->imsi, "limit1", &PVT_STAT(pvt, limit[1]));
    getfilei("imsi", pvt->imsi, "limit2", &PVT_STAT(pvt, limit[2]));
    
    // Read rate limit
    getfilei("imsi", pvt->imsi, "ratelimit", &PVT_STAT(pvt, ratelimit));
}
```

### Write Limits
```c
void writepvtlimits(struct pvt* pvt)
{
    putfilei("imsi", pvt->imsi, "limit0", PVT_STAT(pvt, limit[0]));
    putfilei("imsi", pvt->imsi, "limit1", PVT_STAT(pvt, limit[1]));
    putfilei("imsi", pvt->imsi, "limit2", PVT_STAT(pvt, limit[2]));
}
```

## Device State Persistence

### Write State
```c
void writepvtstate(struct pvt* pvt)
{
    char state_str[32];
    
    // Convert state to string
    snprintf(state_str, sizeof(state_str), "%d", pvt->state);
    
    // Write state
    putfiles("imsi", pvt->imsi, "state", state_str);
    
    // Write AT queue state
    putfilei("imsi", pvt->imsi, "at_tasks", PVT_STATE(pvt, at_tasks));
    putfilei("imsi", pvt->imsi, "at_cmds", PVT_STATE(pvt, at_cmds));
}
```

## Device Error Persistence

### Read Errors
```c
void readpvterrors(struct pvt* pvt)
{
    getfilei("imsi", pvt->imsi, "error_count", &pvt->error_count);
    getfilei("imsi", pvt->imsi, "last_error", &pvt->last_error);
}
```

### Write Errors
```c
void writepvterrors(struct pvt* pvt)
{
    putfilei("imsi", pvt->imsi, "error_count", pvt->error_count);
    putfilei("imsi", pvt->imsi, "last_error", pvt->last_error);
}
```

## Mutex Management

### Lock with Debug Info
```c
int mutex_lock_pvt_e(struct pvt* pvt, const char* filename, int lineno)
{
    int ret = ast_mutex_lock(&pvt->lock);
    if (ret == 0) {
        pvt->lock_owner_file = filename;
        pvt->lock_owner_line = lineno;
        pvt->lock_owner_thread = pthread_self();
    }
    return ret;
}

#define ast_mutex_lock_pvt(a)  mutex_lock_pvt_e(a, __FILE__, __LINE__)
```

### Unlock
```c
int mutex_unlock_pvt_e(struct pvt* pvt, const char* filename, int lineno)
{
    pvt->lock_owner_file = NULL;
    pvt->lock_owner_line = 0;
    return ast_mutex_unlock(&pvt->lock);
}
```

### Try Lock
```c
int mutex_trylock_pvt_e(struct pvt* pvt, const char* filename, int lineno)
{
    int ret = ast_mutex_trylock(&pvt->lock);
    if (ret == 0) {
        pvt->lock_owner_file = filename;
        pvt->lock_owner_line = lineno;
    }
    return ret;
}

#define ast_mutex_trylock_pvt(a)  mutex_trylock_pvt_e(a, __FILE__, __LINE__)
```

## Global Settings

### Read Global Settings
```c
void readglsettings()
{
    // Read global configuration
    getfiles("global", "config", "settings", global_settings_buf);
    getfilei("global", "config", "debug", &global_debug);
}
```

## Log Operations

### Write Log Entry
```c
int putfileslog2(char* devtype, char* fileitem, char* filetype, 
                 const char* valueformat, va_list va)
{
    char filename[128];
    char value[1024];
    
    // Build path
    strcpy(filename, "/var/svistok/");
    strcat(filename, devtype);
    strcat(filename, "/");
    strcat(filename, fileitem);
    strcat(filename, ".");
    strcat(filename, filetype);
    
    // Format value
    vsnprintf(value, sizeof(value), valueformat, va);
    
    // Append to file
    FILE* pFile = fopen(filename, "a");
    if (pFile) {
        fprintf(pFile, "%s\n", value);
        fclose(pFile);
        return 1;
    }
    return 0;
}
```

## Error Handling

### File Not Found
```c
if (!getfilei(...)) {
    // File doesn't exist - use default
    *value = 0;
}
```

### Write Error
```c
if (!putfilei(...)) {
    ast_log(LOG_WARNING, "Failed to write %s/%s.%s\n", 
            devtype, fileitem, filetype);
}
```

### Path Too Long
```c
if (strlen(path) >= sizeof(filename)) {
    ast_log(LOG_ERROR, "Path too long: %s\n", path);
    return 0;
}
```

## Status

**Status**: DRAFT  
**Created**: 2026-03-02  
**Source**: Legacy analysis of share.c, share_mysql.c (590 lines), share.h
