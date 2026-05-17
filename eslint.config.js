const tseslint = require('typescript-eslint');
const jsdoc = require('eslint-plugin-jsdoc');

// Cross-repo tenet 9 ("Document intent — name the question the code answers")
// — TS mirror of qiyas's ruff D101/D103 + D205/D400/D401 gate (qiyas#341,
// #382, #383). New code must carry a JSDoc block on every exported class
// and function. All 9 pre-existing src/ts/ files carry untyped exports
// and are listed in the grace list below; each entry folds into
// sacred-patterns#386 (the parallel drain ticket to qiyas#385). The
// grace list shrinks monotonically as #386 is worked.
const JSDOC_GRACE_FILES = [
  'src/ts/circles.ts',
  'src/ts/index.ts',
  'src/ts/lines.ts',
  'src/ts/polygons.ts',
];

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
    // Grace list — pre-existing tenet-9 debt captured when the gate landed
    // (sacred-patterns#384, 2026-05-16). Each entry folds into #386 (drain
    // by hand-authoring docstrings per tenet 9). New code in any *other*
    // file blocks at lint time. Same monotonically-decreasing discipline
    // as qiyas#341 grace lists.
    files: JSDOC_GRACE_FILES,
    rules: {
      'jsdoc/require-jsdoc': 'off',
      'jsdoc/require-description-complete-sentence': 'off',
    },
  },
  {
    ignores: ['node_modules/', 'site/', 'src/js/', '*.js'],
  },
);
