# Tools Reference

## Available Tools

The LLM has access to these tools for task execution:

### file_read
Read file contents.
```json
{"path": "D:/sl/projects/sllm/run.py"}
```

### file_write
Create or modify files.
```json
{"path": "test.py", "content": "print('hello')"}
```

### list_directory
List folder contents.
```json
{"path": "D:/sl/projects/sllm"}
```

### execute_code
Run Python code in sandbox.
```json
{"code": "print(1+1)", "timeout": 30}
```

### search_code
Search patterns in code files.
```json
{"pattern": "def fibonacci", "path": ".", "file_type": ".py"}
```

### get_system_info
Query system information.
```json
{}```