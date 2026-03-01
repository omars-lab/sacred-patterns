const tseslint = require('typescript-eslint');

module.exports = tseslint.config(
  {
    files: ['src/ts/**/*.ts'],
    extends: [
      ...tseslint.configs.recommended,
    ],
    rules: {
      'no-prototype-builtins': 'off',
      '@typescript-eslint/no-explicit-any': 'off',
    },
  },
  {
    ignores: ['node_modules/', 'site/', 'src/js/', '*.js'],
  },
);
