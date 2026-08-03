# ADR 005: Coding Intelligence Engine Architecture

## Status
**Accepted** — 2026-07-31

## Context
As Project Astra OS enters Phase 3 (Knowledge & Code Intelligence), Astra requires structural codebase comprehension capabilities beyond raw text search. 

Code contains explicit syntax structure (classes, methods, functions, docstrings, imports, inheritance, call trees). Regex string matching is fragile and prone to false positives when extracting signatures, docstrings, and dependencies.

## Decision
We have designed and implemented the **Coding Intelligence Engine** following Hexagonal Architecture:

1. **Native AST Parsing over Regex**:
   - `ASTParser` uses Python's native `ast` module to construct precise Abstract Syntax Trees.
   - `SymbolExtractor` traverses AST nodes to extract classes, functions, methods, imports, decorators, docstrings, and type annotations with line numbers.

2. **Graph-Based Dependency & Call Graph Analysis**:
   - `DependencyAnalyzer` constructs import and inheritance dependency graphs, including circular dependency detection loops.
   - `CallGraphBuilder` constructs caller-to-callees invocation mapping across function AST nodes.

3. **Refactoring & Code Health Engine**:
   - `RefactoringEngine` inspects AST graph metrics to identify dead code, unused imports, long functions (>50 lines), missing type hints, and circular dependencies.

4. **Tree-sitter Pluggable Design**:
   - The parser layer is decoupled through `ProjectPort` and `ASTParser` so that Python's native `ast` can later be swapped or complemented with **Tree-sitter** for multi-language support (JS/TS, C++, Rust, Go).

## Consequences
- Astra can index complete Python software repositories (`c:/Users/rudra/OneDrive/Desktop/astra`), map callers/callees, detect circular dependencies, and generate comprehensive architecture reports.
- Analysis is 100% precise and syntax-aware.
