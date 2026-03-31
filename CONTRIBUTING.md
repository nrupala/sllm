# Contributing to SL-LLM

Thank you for your interest in contributing!

## How to Contribute

### 1. Fork the Repository
Click the "Fork" button on GitHub to create your own copy.

### 2. Clone Your Fork
```bash
git clone https://github.com/YOUR_USERNAME/sllm.git
cd sllm
```

### 3. Create a Branch
```bash
git checkout -b feature/your-feature-name
```

### 4. Make Changes
- Follow existing code style
- Add comments for complex logic
- Keep dependencies minimal

### 5. Test Your Changes
```bash
# Test with mock backend
python run.py --test --prefer=mock
```

### 6. Commit
```bash
git add .
git commit -m "Description of changes"
```

### 7. Push
```bash
git push origin feature/your-feature-name
```

### 8. Submit Pull Request
Open a PR on GitHub with a clear description.

## Coding Standards

- Use Python 3.8+ syntax
- Keep functions under 100 lines
- Add docstrings for public functions
- No external dependencies beyond requirements.txt

## Bug Reports

Use GitHub Issues with:
- Clear title
- Steps to reproduce
- Expected vs actual behavior
- Environment details

## Feature Requests

Open an issue with:
- Description of feature
- Use case
- Suggested implementation (optional)

---

Thank you for contributing!