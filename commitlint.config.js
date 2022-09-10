module.exports = {
    // See https://github.com/conventional-changelog/commitlint/blob/master/%40commitlint/config-conventional/index.js
    extends: ['@commitlint/config-conventional'],
    // Own rules
    rules: {
        'subject-case': [
            2,
            'never',
            ['start-case', 'pascal-case', 'upper-case'],
        ],
    },
}
