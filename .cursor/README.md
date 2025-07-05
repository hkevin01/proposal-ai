# .cursor Configuration

This folder contains configuration files that enforce coding standards and rules for the Cursor AI assistant.

## Files

- **`rules.md`** - Comprehensive documentation of all coding rules and operational features
- **`settings.json`** - Cursor-specific settings for AI assistance and coding standards
- **`tsconfig-strict.json`** - Strict TypeScript configuration that enforces type safety
- **`eslint-config.json`** - ESLint rules for code quality and consistency

## Usage

### For Cursor AI
The AI assistant will reference these files to ensure all generated code follows the established standards.

### For Development
1. Use `tsconfig-strict.json` as your TypeScript configuration
2. Apply the ESLint rules from `eslint-config.json`
3. Reference `rules.md` for manual code reviews

## Key Standards Enforced

1. **Completeness** - No placeholders, complete implementations
2. **Comments** - Comprehensive documentation and inline comments
3. **Error Checking** - Full validation and error handling
4. **TypeScript Types** - Strict typing, no `any`, no `!` assertions
5. **String Standards** - Double quotes, template literals, no concatenation

## Operational Features

- Context window warnings
- Missing content requests
- Error correction and education

These configurations ensure consistent, high-quality code generation and maintenance. 