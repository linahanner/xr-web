/*
 *  index.js
 *  ----------
 *  Entry point for webpack.
 *  Other stuff (styles/js/fonts/components/...) gets included from here.
 */

// import normalize css
import 'normalize.css'

// Import project styles
import '../styles/main.scss'

// import umbrella js
import u from 'umbrellajs/umbrella.esm.js'


document.addEventListener("DOMContentLoaded", () => {
    u("button").on('click', () => {
        alert("Hello world!")
    })
})
