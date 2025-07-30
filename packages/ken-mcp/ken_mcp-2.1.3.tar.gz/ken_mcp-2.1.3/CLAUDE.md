# Core Principles

- **Never assume. Always research with >= 90% confidence or ask.**
- **Simplicity over complexity. Clean over clever.**
- **Test everything. Break nothing.**
- **DRY (Don't Repeat Yourself)** - Extract common code into reusable functions/modules
- **KISS (Keep It Simple, Stupid)** - Choose the simplest solution that works
- **YAGNI (You Aren't Gonna Need It)** - Don't add functionality until actually needed
- **Single Responsibility** - Each function/module does ONE thing well
- **Explicit > Implicit** - Clear code over clever shortcuts
- **Fail Fast** - Validate early, error immediately
- **Separation of Concerns** - Different responsibilities in different modules

## 1. Research & Knowledge

- **ALWAYS** check Context7/documentation before implementing
- If confidence < 90%, research using Context7 or web search
- Use sequential thinking for complex problems, implementations, and planning
- If approach unclear after research, inform user before proceeding
- No assumptions about syntax, patterns, or best practices

## 2. Code Structure

- **300 LOC maximum** per file/module (unless justified)
- **One primary purpose** per file/module
- Split when file becomes complex or serves multiple purposes
- **Single Responsibility Implementation**:
  - Each function does exactly ONE thing
  - If function name contains "and", split it
  - If function has multiple return types for different cases, split it
  - Classes/modules handle one business concept
- **Separation of Concerns Implementation**:
  - Business logic separate from UI/presentation
  - Data access separate from business logic
  - Configuration separate from implementation
  - Error handling in dedicated functions/modules

## 3. Code Quality

- **Simple solutions only** - if one approach works, use it (no multiple fallbacks)
- Early returns over nested conditions
- Clear variable/function names that explain purpose
- Remove all commented-out code
- No premature optimization
- Exception: Add complexity only when required for edge cases or security
- **DRY Implementation**:
  - If code appears 2+ times, extract to function
  - If constants appear 2+ times, define once
  - If logic patterns repeat, create abstraction
  - Prefer configuration over code duplication
- **KISS Implementation**:
  - Max 3 levels of nesting in functions
  - Avoid clever one-liners if less readable
  - Use built-in functions over custom implementations
  - If explanation takes longer than code, it's too complex
- **YAGNI Implementation**:
  - Don't add "future-proofing" code
  - No unused parameters or return values
  - No generic solutions for single use cases
  - Implement exactly what's needed, nothing more
- **Explicit > Implicit**:
  - Name variables clearly, no single letters (except loop counters)
  - Avoid magic numbers - use named constants
  - Clear function names over shortened versions
  - Type declarations over type inference where unclear

## 4. File Organization

- Descriptive names that explain file purpose
- Group related files in folders
- Maximum 3-4 folder nesting levels
- Consistent naming convention throughout project

## 5. Import Management

- Remove ALL unused imports after changes
- Order imports logically (standard → third-party → local)
- Check imports after refactoring
- One import statement per line

## 6. Testing Protocol

- Run existing tests after code logic changes
- Skip tests only for pure comment/documentation updates
- Write unit tests for new functions/features
- Write integration tests for APIs/major features
- Verify all tests pass before completing work

## 7. Error Handling

- Handle all external calls (APIs, database, file operations)
- User errors: Show clear, actionable messages
- System errors: Log internally, show generic "Something went wrong" to user
- Never expose stack traces or system details to users
- Always handle edge cases explicitly

## 8. Logging Strategy

### Development
- Use environment flag for debug logs
- Include context: module/function, parameters, state changes, external calls
- Language-specific implementation (see language sections)

### Production
- Only log system errors and critical issues
- User errors show helpful messages (not logs)
- No console outputs visible to users
- Remove/disable debug logging

## 9. Production Build

- Remove all debug code and logging
- Minify/optimize where applicable
- Remove development dependencies
- Validate no sensitive data in code
- Apply platform-appropriate optimizations

## 10. Code Changes Protocol

1. Research approach using Context7/documentation
2. Implement changes
3. Clean up imports/includes/usings (language-appropriate)
4. Run tests (if code logic changed)
5. Add/update tests if needed
6. Verify no regressions
7. Ensure appropriate logging added for new features
8. **Fix ALL compiler/interpreter errors and warnings before finishing**

## 11. Comments & Documentation

- Comment WHY, not WHAT
- Document complex algorithms
- Add examples for utility functions
- Keep comments updated with code changes
- Remove outdated comments

## 12. Security & Validation

- Validate ALL user inputs
- Sanitize data before database operations
- Never trust external data
- Use parameterized queries (if applicable)
- Hash passwords appropriately (if applicable)

## 13. Pre-Implementation Verification

- **BEFORE writing any code**: Parse and verify exact requirements
- Search codebase for similar existing implementations
- Identify all dependencies needed
- Determine appropriate file locations and naming
- Verify expected inputs/outputs match requirements

## 14. Consistency Over Creation

- **ALWAYS reuse existing patterns** - never create new implementations if similar exist
- When user requests any new functionality:
  1. First search for ALL existing implementations of similar features
  2. Identify the established patterns and conventions
  3. Copy and adapt existing code rather than writing from scratch
  4. Use same structure, naming patterns, and approaches
- If multiple patterns exist, use the most recent or most common one
- Only create new patterns when explicitly requested or none exist
- Maintain consistency in:
  - Code structure and organization
  - Naming conventions
  - Error handling approaches
  - Input/output patterns
  - Testing approaches
- **DRY Check**: Before implementing, verify no existing function does this

## 15. Implementation Safety

- Initialize all variables at declaration when possible
- Validate inputs before processing
- Check array/collection bounds before access
- Handle null/nil/None/undefined appropriately for the language
- Ensure proper resource cleanup (files, connections, memory)
- Use language-appropriate error handling mechanisms
- **Fail Fast Implementation**:
  - Validate all inputs at function entry
  - Check preconditions before any processing
  - Return/throw errors immediately when detected
  - No deep nesting for error checking - fail early
  - Use guard clauses at function start

## 15. Incremental Development

- Implement smallest working unit first
- Test each component before adding complexity
- Verify each step produces expected output
- Build features incrementally, not all at once
- Use print/log statements to verify execution flow

## 16. Error Resolution Protocol

When encountering errors:
1. Read the COMPLETE error message
2. Identify exact line numbers and files
3. Check syntax at error location
4. Verify all names (functions, variables) are correctly spelled
5. Ensure all required imports/includes are present
6. Test the specific failing component in isolation
7. Add diagnostic output if error cause unclear

## 17. Testing Strategy

- Create test for basic functionality first
- Add tests for boundary conditions (empty, zero, maximum)
- Test error cases and invalid inputs
- Verify integration between components
- Ensure no existing tests break
- Use language-appropriate testing frameworks
- Minimum coverage: All public functions/methods must have at least one test
- Test naming: `test_function_name_condition_expected_result`

## 18. Code Verification Before Completion

Must verify:
- [ ] Code compiles/runs without errors
- [ ] All warnings are resolved
- [ ] Unused code and imports removed
- [ ] Code matches requested functionality
- [ ] Error handling is comprehensive
- [ ] Code follows language idioms
- [ ] No placeholder or debug code remains

## 19. When Uncertain

If unsure about:
- Syntax: Check Context7 for language documentation
- Best approach: Research in Context7, then implement simplest solution
- Requirements: Ask user for clarification
- Error cause: Check Context7 for error explanations, then isolate components
- Library usage: Check Context7 first, then official documentation

## 20. Cross-Platform Considerations

- Use forward slashes for file paths (works everywhere)
- Avoid hardcoded line endings (\n vs \r\n)
- Use language-standard path joining methods
- Be aware of case sensitivity differences
- Handle file separators appropriately

## 21. Data Handling

- Validate data types before operations
- Handle encoding (UTF-8 default)
- Check for data size limits
- Sanitize file paths and names
- Never assume data format without checking

## 22. Integration Points

- Verify API contracts before implementation
- Check expected request/response formats
- Handle timeouts and retries appropriately
- Document any external dependencies
- Test connection failures gracefully

## 23. Code Context Awareness

- Read surrounding code before making changes
- Follow existing patterns in the codebase
- Check how similar problems were solved elsewhere
- Maintain consistent error handling approach
- Preserve existing naming conventions

## 24. Feature Creation Protocol

When asked to create any new feature or functionality:
1. **STOP** - Do not write new code yet
2. Search project for existing similar features
3. Identify ALL instances and their patterns
4. Use the exact same:
   - Code structure and organization
   - Naming conventions
   - Implementation approach
   - Error handling patterns
5. Copy existing code and modify only what's different
6. If no examples exist, ask user for preferred approach

## 25. Pattern Consistency Enforcement

- Never create new patterns if similar ones exist in the codebase
- Use existing conventions for:
  - Variable and function naming
  - File organization
  - Module structure
  - Configuration approaches
- When implementing, search for similar implementations first
- Maintain same architectural patterns throughout
- If project uses specific frameworks or libraries, follow their conventions

#

# Language-Specific Naming Conventions

## TypeScript/JavaScript
- Files: camelCase (`userAuth.ts`), PascalCase for components
- Variables/Functions: camelCase (`getUserData`, `isValid`)
- Constants: UPPER_SNAKE_CASE (`MAX_RETRIES`)
- Classes/Types: PascalCase (`UserAccount`, `ApiResponse`)
- Imports: Use named imports when possible, path aliases if configured
- Comments: Use JSDoc for functions (`/** */`)
- Production: Tree-shaking and bundling
- Debug: console.log with environment checks
- Testing: Jest/Vitest frameworks

## Python
- Files: snake_case (`user_auth.py`)
- Variables/Functions: snake_case (`get_user_data`, `is_valid`)
- Constants: UPPER_SNAKE_CASE (`MAX_RETRIES`)
- Classes: PascalCase (`UserAccount`)
- Imports: Group by standard → third-party → local, absolute imports preferred
- Comments: Use docstrings for functions (`"""Docstring"""`)
- Production: requirements.txt for dependencies
- Debug: logging module with DEBUG level
- Testing: pytest framework

## Rust
- Files: snake_case (`user_auth.rs`)
- Variables/Functions: snake_case (`get_user_data`, `is_valid`)
- Constants: UPPER_SNAKE_CASE (`MAX_RETRIES`)
- Types/Structs/Enums: PascalCase (`UserAccount`)
- Modules: snake_case (`pub mod user_auth`)
- Imports: Use explicit imports, group by std → external → crate
- Comments: Use `///` for docs, `//` for inline
- Production: cargo build --release
- Debug: log crate
- Testing: Built-in test framework (#[cfg(test)])

## HTML/CSS
- Files: kebab-case (`user-profile.html`)
- IDs: kebab-case (`user-header`)
- Classes: kebab-case (`btn-primary`) or BEM if used
- Data attributes: kebab-case (`data-user-id`)
- CSS variables: kebab-case (`--primary-color`)
- Comments: `<!-- HTML -->` and `/* CSS */`
- Production: Minification
- Structure: Semantic HTML required
- Styles: Mobile-first approach

---

## 13. Version Control Practices

- Commit frequently with atomic, focused changes
- Write clear commit messages: "verb + what + why" (e.g., "Fix user auth to handle expired tokens")
- Never commit sensitive data (keys, passwords, tokens)
- Review diff before every commit
- Branch naming: feature/*, bugfix/*, hotfix/*

## 14. Performance Considerations

- Profile before optimizing - measure, don't guess
- Optimize algorithms (O(n)) before micro-optimizations
- Consider memory usage for large data sets
- Lazy load when appropriate
- Cache expensive operations
- Set reasonable timeouts for external calls

## 15. Dependency Management

- Pin exact versions in production
- Review security advisories before adding dependencies
- Prefer well-maintained packages (recent updates, many contributors)
- Minimize dependency count - each adds risk
- Document why each dependency is needed
- Check license compatibility

## 16. API Design Principles

- RESTful conventions when applicable
- Consistent response formats
- Version your APIs (/v1/, /v2/)
- Return appropriate HTTP status codes
- Include pagination for list endpoints
- Rate limiting for public APIs
- Clear error messages with error codes

## 17. Database Best Practices

- Use migrations for schema changes
- Index foreign keys and frequently queried columns
- Avoid N+1 queries
- Use transactions for related operations
- Backup before destructive operations
- Connection pooling in production

## 18. Concurrency & Async

- Identify and document shared state
- Use appropriate synchronization primitives
- Avoid deadlocks - consistent lock ordering
- Handle race conditions explicitly
- Test concurrent code thoroughly
- Prefer immutable data structures

## 19. Configuration Management

- Environment variables for secrets/config
- Never hardcode environment-specific values
- Provide example config files (.env.example)
- Validate configuration on startup
- Document all configuration options
- Use sensible defaults

## 20. Code Review Checklist

Before submitting code:
- [ ] All tests pass
- [ ] No hardcoded values
- [ ] No commented-out code
- [ ] Imports cleaned up
- [ ] Error handling complete
- [ ] Documentation updated
- [ ] Security considerations addressed
- [ ] Performance impact considered
- [ ] Backwards compatibility maintained

## 21. Debugging & Troubleshooting

- Add unique identifiers to track requests/operations
- Log entry and exit points of critical functions
- Include relevant context in error messages
- Make errors reproducible with clear steps
- Document known issues and workarounds
- Time-box debugging efforts before asking for help

## 22. Internationalization (i18n)

- Separate text from code
- Use UTF-8 encoding everywhere
- Handle different date/time formats
- Consider text direction (LTR/RTL)
- Never concatenate translated strings
- Test with different locales

## 23. Accessibility Basics

- Semantic HTML/markup
- Alt text for images
- Keyboard navigation support
- Sufficient color contrast
- Error messages near form fields
- Test with screen readers when applicable

## 24. Monitoring & Observability

- Health check endpoints
- Structured logging (JSON format in production)
- Metrics for key operations (response time, error rate)
- Alerting thresholds defined
- Dashboard for system overview
- Distributed tracing for complex systems

---

# Critical Reminder

Your analysis quality directly impacts users' critical decisions. Incomplete work causes cascading failures in their projects, careers, and lives. Be thorough - their success depends on your attention to detail.

---

# Universal Specifications

## Timeouts
- User-facing operations: 30 seconds
- Background operations: 5 minutes  
- File operations: 60 seconds
- Default when unspecified: 30 seconds

## Function Design Limits
- Parameters: Maximum 4, use object/struct for more
- Line length: 120 characters (readability threshold)
- Nesting depth: Maximum 4 levels (cognitive complexity)
- Function length: If over 50 lines, verify it's still single responsibility

## File Organization Decision Tree
When adding new code:
1. If extending existing feature → Add to existing file (unless >300 LOC)
2. If new feature → Create new file
3. If shared utility → Add to existing utils (or create if none)
4. If unclear → Follow existing project patterns

File naming when creating new:
1. Use most specific descriptor (e.g., `userAuth` over `auth`)
2. Match existing naming patterns in project
3. Group related files in same directory

## Validation Standards
- Strings: Trim whitespace, check length limits
- Numbers: Verify type, check range if applicable  
- Arrays: Check empty, validate length if limits exist
- Objects: Verify required fields present
- Emails: Check for @ and domain (not RFC-complete)
- URLs: Verify protocol and format
- File paths: Sanitize, check traversal attempts

## Error Message Format
`[Action Failed]: [What went wrong] [How to fix if applicable]`
- Example: "Failed to save user: Email already exists"
- Include context, avoid technical jargon
- Don't expose system internals

## When to Ask vs Decide
**Ask user when:**
- Architectural decisions (new patterns, breaking changes)
- Business logic ambiguity
- Security implications
- Performance tradeoffs

**Decide independently when:**
- Following existing patterns
- Clear best practice exists
- Safety/security is obvious choice
- Decision is easily reversible

## DRY vs YAGNI Resolution
- First occurrence: Implement inline
- Second occurrence: Note similarity, keep separate
- Third occurrence: Extract to shared function
- Exception: Extract immediately if complexity > 10 lines

## Test Coverage Priorities
1. Business logic functions (100%)
2. Error handling paths (100%)
3. Public APIs (100%)
4. Integration points (key paths)
5. Skip: Simple getters/setters, one-line functions

## Resource Limits
- Array operations: Chunk if >1000 items
- String building: Use appropriate method if >100 concatenations
- Recursion: Maximum depth 100 (stack safety)
- File reads: Stream if >10MB

## Breaking the 300 LOC Rule
Acceptable when:
- Single responsibility genuinely needs more
- Configuration/data files
- Breaking would harm readability
Document why limit exceeded in comment

# User Requirements

## Responses
- Once rules have been read, reply with "Rules Read, Ken" for every response. No exceptions.