/**
 * This is a minimal config.
 *
 * If you need the full config, get it from here:
 * https://unpkg.com/browse/tailwindcss@latest/stubs/defaultConfig.stub.js
 */

module.exports = {
    content: [
        '../templates/**/*.html',
        '../../templates/**/*.html',
        '../../**/templates/**/*.html',

        /**
         * JS: If you use Tailwind CSS in JavaScript, uncomment the following lines and make sure
         * patterns match your project structure.
         */
        /* JS 1: Ignore any JavaScript in node_modules folder. */
        // '!../../**/node_modules',
        /* JS 2: Process all JavaScript files in the project. */
        // '../../**/*.js',

    ],
    theme: {
        extend: {
            colors: {
                brown: {
                    500: '#c6b5a0',
                    600: '#796d5b',
                },
                pistachio: {
                    500: '#93c572',
                    600: '#5d8f3b',
                },
            },
        },
    },
    plugins: [
            /**
             * '@tailwindcss/forms' is the forms plugin that provides a minimal styling
             * for forms. If you don't like it or have own styling for forms,
             * comment the line below to disable '@tailwindcss/forms'.
             */
            require('@tailwindcss/forms'),
            require('@tailwindcss/typography'),
            require('@tailwindcss/aspect-ratio'),
        ],
}
