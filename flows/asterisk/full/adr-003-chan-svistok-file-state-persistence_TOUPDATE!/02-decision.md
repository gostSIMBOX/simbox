# Solution

## Directory Structure

```
/var/svistok/
├── imsi/
│   ├── 250000000.balance    # Account balance
│   ├── 250000000.number     # Phone number
│   ├── 250000000.provider   # Provider name
│   ├── 250000000.limit0     # Call limit 1
│   ├── 250000000.limit1     # Call limit 2
│   ├── 250000000.limit2     # Call limit 3
│   └── 250000000.state      # Device state
├── device/
│   └── dongle0.config       # Device config
└── global/
    └── settings             # Global settings
```

## API

### Read Integer
```c
int getfilei(char* devtype, char* fileitem, char* filetype, int *value);
// Returns: 1 on success, 0 on file not found
```

### Write Integer
```c
int putfilei(char* devtype, char* fileitem, char* filetype, int value);
// Returns: 1 on success, 0 on error
```

### Read String
```c
int getfiles(char* devtype, char* fileitem, char* filetype, char *value);
```

### Write String
```c
int putfiles(char* devtype, char* fileitem, char* filetype, char* value);
```

## Implementation

### Read Example
```c
int getfilei(char* devtype, char* fileitem, char* filetype, int *value)
{
    char filename[128];
    
    // Build path: /var/svistok/{devtype}/{fileitem}.{filetype}
    strcpy(filename, "/var/svistok/");
    strcat(filename, devtype);
    strcat(filename, "/");
    strcat(filename, fileitem);
    strcat(filename, ".");
    strcat(filename, filetype);
    
    FILE* pFile = fopen(filename, "r");
    if (pFile != NULL) {
        fscanf(pFile, "%d", value);
        fclose(pFile);
        return 1;
    }
    return 0;  // File not found
}
```

### Write Example
```c
int putfilei(char* devtype, char* fileitem, char* filetype, int value)
{
    char filename[128];
    
    strcpy(filename, "/var/svistok/");
    strcat(filename, devtype);
    strcat(filename, "/");
    strcat(filename, fileitem);
    strcat(filename, ".");
    strcat(filename, filetype);
    
    FILE* pFile = fopen(filename, "w");
    if (pFile != NULL) {
        fprintf(pFile, "%d", value);
        fclose(pFile);
        return 1;
    }
    return 0;
}
```

## Usage Examples

### Store Balance
```c
putfilei("imsi", pvt->imsi, "balance", PVT_STAT(pvt, balance));
// Creates: /var/svistok/imsi/250000000.balance
// Content: "1250"
```

### Read Limits
```c
getfilei("imsi", pvt->imsi, "limit0", &PVT_STAT(pvt, limit[0]));
getfilei("imsi", pvt->imsi, "limit1", &PVT_STAT(pvt, limit[1]));
getfilei("imsi", pvt->imsi, "limit2", &PVT_STAT(pvt, limit[2]));
```

### Store State
```c
char state_str[32];
snprintf(state_str, sizeof(state_str), "%d", pvt->state);
putfiles("imsi", pvt->imsi, "state", state_str);
```

## Mutex Protection

```c
// Lock before read/write
ast_mutex_lock_pvt(pvt);

// Perform file operations
readpvtinfo(pvt);
writepvtlimits(pvt);

// Unlock
ast_mutex_unlock_pvt(pvt);
```

## Error Handling

### File Not Found
```c
if (!getfilei(...)) {
    *value = 0;  // Use default
}
```

### Write Error
```c
if (!putfilei(...)) {
    ast_log(LOG_WARNING, "Failed to write file\n");
}
```
