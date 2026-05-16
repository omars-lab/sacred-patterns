const tseslint = require('typescript-eslint');

module.exports = tseslint.config(
  {
    files: ['src/ts/**/*.ts'],
    extends: [
      ...tseslint.configs.recommended,
    ],
    rules: {
      'no-prototype-builtins': 'off',
      // Cross-repo tenet 16 — Any silences the strict-typing gate; derive the
      // real type instead. Mirrors qiyas ANN401 and bikar no-explicit-any.
      '@typescript-eslint/no-explicit-any': 'error',
    },
  },
  {
    ignores: ['node_modules/', 'site/', 'src/js/', '*.js'],
  },
);
