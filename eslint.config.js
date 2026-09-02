const tseslint = require('typescript-eslint');
const jsdoc = require('eslint-plugin-jsdoc');

// Cross-repo tenet 9 ("Document intent — name the question the code answers")
// — TS mirror of qiyas's ruff D101/D103 + D205/D400/D401 gate (qiyas#341,
// #382, #383). The grace list shipped with the gate (sacred-patterns#384)
// drained to zero via #386 — every src/ts/ export now carries a
// hand-authored WHY-style JSDoc block. New code blocks at lint time
// without exception; if a future grace period is needed, restore the
// JSDOC_GRACE_FILES const + the matching `files: JSDOC_GRACE_FILES`
// overrides block, never silence the rule itself (mirrors tenet 16:
// no `Any`/`# type: ignore` to silence the strict gate).

module.exports = tseslint.config(
  {
    files: ['src/ts/**/*.ts'],
    plugins: { jsdoc },
    extends: [
      ...tseslint.configs.recommended,
    ],
    rules: {
      'no-prototype-builtins': 'off',
      // Cross-repo tenet 16 — Any silences the strict-typing gate; derive the
      // real type instead. Mirrors qiyas ANN401 and bikar no-explicit-any.
      '@typescript-eslint/no-explicit-any': 'error',
      // Cross-repo tenet 9 — exported classes/functions must carry a JSDoc
      // block naming WHY the function exists (the question it answers),
      // not WHAT (the type signature already says that). Mirrors qiyas
      // D101/D103. Style sub-rules (D205/D400/D401 analogs) are below.
      'jsdoc/require-jsdoc': ['error', {
        publicOnly: true,
        require: {
          ClassDeclaration: true,
          FunctionDeclaration: true,
          MethodDefinition: false,
          ArrowFunctionExpression: false,
          FunctionExpression: false,
        },
        contexts: [
          'ExportNamedDeclaration > FunctionDeclaration',
          'ExportNamedDeclaration > ClassDeclaration',
          'ExportNamedDeclaration > VariableDeclaration',
          'ExportDefaultDeclaration > FunctionDeclaration',
          'ExportDefaultDeclaration > ClassDeclaration',
        ],
      }],
      // Style: first line ends with punctuation (mirrors ruff D400).
      'jsdoc/require-description-complete-sentence': 'warn',
      // Style: no whitespace-only first line (mirrors ruff D205 — must have
      // content immediately, with structured body following).
      'jsdoc/no-blank-blocks': 'error',
      // Cross-repo tenet 1 ("Simplicity over complexity") — >10 branches per
      // function means it's doing too many things; split it (extract helpers,
      // dispatch tables, collapse nested conditionals). Mirrors qiyas ruff
      // C901 max-complexity=10 (qiyas#348) and bikar eslint complexity gate
      // (bikar#348). Baseline measurement on src/ts/ at gate-landing showed
      // zero pre-existing violations — no grace list needed.
      complexity: ['error', { max: 10 }],
    },
  },
  {
    ignores: ['node_modules/', 'site/', 'src/js/', '*.js'],
  },
);
