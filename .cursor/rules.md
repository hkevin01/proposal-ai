# Cursor AI Coding Rules & Standards

## OPERATIONAL FEATURES

### Context Window Warnings
- Alert the user when nearing the context window limit
- Provide clear warnings about potential information loss

### Missing Content Requests
- Request the user provide project code, documentation, or definitions necessary for an adequate response
- Be proactive in identifying missing information

### Error Correction
- Indicate all user prompt errors of terminology, convention, or understanding
- Correct errors regardless of their relevance to the user prompt
- Provide educational explanations for corrections

## CRITICALLY IMPORTANT RULES

### 1. Completeness
- Generate full code, no placeholders
- If unable to complete, explain limitations in comments
- Provide complete implementations with all necessary imports and dependencies

### 2. Comments
- Include clear inline comments explaining complex logic
- Add comprehensive Doc headers describing each function/class
- Document each step of code execution
- Use JSDoc/TSDoc format for TypeScript/JavaScript

### 3. Error Checking
- Implement comprehensive error checking and validation
- Add type validation for all inputs
- Handle edge cases and potential failures
- Provide meaningful error messages

### 4. TypeScript Types
- Implement strict TypeScript notation
- Define new types as necessary for clarity
- **CRITICAL RESTRICTIONS:**
  - Do NOT use the 'any' type
  - Do NOT use the non-null assertion operator (`!`)
  - Do NOT cast to unknown (e.g. `as unknown as T`)
- Use proper type guards and validation instead

### 5. String Standards
- Use double quotes (`"`) for all strings
- Use string templates (`` `template ${variable}` ``) instead of concatenation
- Use `.join()` method for array-to-string conversion
- Avoid operational string concatenation with `+`

## IMPLEMENTATION GUIDELINES

### Code Quality
- Follow DRY (Don't Repeat Yourself) principles
- Write self-documenting code
- Use meaningful variable and function names
- Maintain consistent formatting and indentation

### Testing
- Include error handling examples
- Provide usage examples in comments
- Consider edge cases in implementations

### Documentation
- Document all public APIs
- Include parameter descriptions
- Specify return types and values
- Add usage examples where appropriate

## ENFORCEMENT

These rules must be followed in ALL code generation and suggestions. Any deviation must be explicitly justified and documented. 