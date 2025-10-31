# Contributing to askPhysics

Thank you for your interest in contributing to askPhysics! This document provides guidelines for contributing to the project.

## How to Contribute

### Reporting Issues

If you find a bug or have a feature request:

1. Check if the issue already exists in the [Issues](https://github.com/subodhkhanger/askPhysics/issues) section
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce (for bugs)
   - Expected vs actual behavior
   - Your environment (OS, Python version, etc.)

### Submitting Pull Requests

1. **Fork the repository**
   ```bash
   git clone https://github.com/subodhkhanger/askPhysics.git
   cd askPhysics
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Write clean, readable code
   - Follow existing code style
   - Add comments for complex logic
   - Update documentation if needed

4. **Test your changes**
   ```bash
   # Backend tests
   cd backend
   pytest

   # Frontend tests
   cd frontend
   npm test
   ```

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add feature: your feature description"
   ```

6. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request**
   - Go to the original repository
   - Click "New Pull Request"
   - Select your branch
   - Describe your changes

## Development Guidelines

### Code Style

**Python (Backend)**
- Follow PEP 8 style guide
- Use type hints
- Write docstrings for functions/classes
- Maximum line length: 100 characters

**TypeScript (Frontend)**
- Use ESLint and Prettier
- Follow React best practices
- Use functional components with hooks
- Write prop types for components

### Commit Messages

Use clear, descriptive commit messages:

```
Add feature: natural language date parsing
Fix bug: SPARQL query escaping for special characters
Update docs: installation guide for Windows
Refactor: simplify temperature unit conversion
```

### Testing

- Write tests for new features
- Ensure existing tests pass
- Test edge cases and error handling

### Documentation

- Update README.md for major changes
- Add docstrings for new functions
- Update API documentation
- Include examples for new features

## Areas for Contribution

### Backend
- [ ] Add support for more physical quantities (pressure, magnetic field)
- [ ] Implement caching layer (Redis)
- [ ] Add authentication and rate limiting
- [ ] Improve SPARQL query optimization
- [ ] Add more unit conversions

### Frontend
- [ ] Improve UI/UX design
- [ ] Add data visualization charts
- [ ] Implement advanced filtering
- [ ] Add export functionality (CSV, BibTeX)
- [ ] Improve mobile responsiveness

### Knowledge Graph
- [ ] Add more papers to the dataset
- [ ] Improve ontology with more classes
- [ ] Add citation relationships
- [ ] Link to external databases (DOI, ORCID)

### NLP/LLM
- [ ] Fine-tune custom model with LoRA
- [ ] Add support for more query types
- [ ] Improve parameter extraction accuracy
- [ ] Add multi-language support

### DevOps
- [ ] Add CI/CD pipeline
- [ ] Improve Docker setup
- [ ] Add monitoring and logging
- [ ] Create Kubernetes deployment

## Questions?

Feel free to open an issue for:
- Questions about the codebase
- Clarification on contribution process
- Discussion of new features
- Help with setup or development

## Code of Conduct

- Be respectful and constructive
- Welcome newcomers
- Focus on the technical discussion
- Help others learn and improve

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Recognition

Contributors will be acknowledged in the README and release notes.

Thank you for helping make askPhysics better! 🚀
