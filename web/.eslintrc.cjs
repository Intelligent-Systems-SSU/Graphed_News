/* eslint-disable @typescript-eslint/no-require-imports */

const path = require('path');

const { includeIgnoreFile } = require('@eslint/compat');
const importPlugin = require('eslint-plugin-import');
const jsxA11y = require('eslint-plugin-jsx-a11y');
const react = require('eslint-plugin-react');
const tseslint = require('typescript-eslint');

const gitignorePath = path.resolve(__dirname, '.gitignore');

/** @type {import('eslint').Linter.Config} */
module.exports = tseslint.config([
  includeIgnoreFile(gitignorePath),
  {
    plugins: {
      react,
      jsxA11y,
    },
    rules: {
      ...react.configs.recommended.rules,
      'react/react-in-jsx-scope': 'off',
    },
    settings: {
      react: {
        version: 'detect',
      },
      formComponents: ['Form'],
      linkComponents: [
        { name: 'Link', linkAttribute: 'to' },
        { name: 'NavLink', linkAttribute: 'to' },
      ],
      'import/resolver': {
        typescript: {},
      },
    },
  },
  tseslint.configs.strict,
  tseslint.configs.stylistic,
  importPlugin.flatConfigs.recommended,
  {
    rules: {
      'import/order': [
        'error',
        {
          groups: ['builtin', 'external', 'internal', ['parent', 'sibling'], 'index', 'object', 'type', 'unknown'],
          pathGroups: [
            {
              pattern: '@*/**',
              group: 'external',
            },
            {
              pattern: 'app/**',
              group: 'internal',
            },
            {
              pattern: 'Mock/**',
              group: 'internal',
            },
            {
              pattern: '*/**',
              group: 'internal',
            },
          ],
          pathGroupsExcludedImportTypes: ['builtin', 'object'],
          'newlines-between': 'always',
          alphabetize: {
            order: 'asc',
            caseInsensitive: true,
          },
        },
      ],
      'import/first': 'error',
    },
  },
]);
