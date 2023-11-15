const { src, dest, watch, series } = require('gulp');
const sass = require('gulp-sass')(require('sass'));
// const purgecss = require('gulp-purgecss');

function compileSass() {
    return src('app/static/style/css_library/**/*.scss')
        .pipe(sass())
        .pipe(dest('app/static/style/css'));
}

function applyPurgeCSS() {
    return src('app/static/style/css/**/*.css')  // Assuming you've compiled Sass files to the 'css' folder
        // .pipe(purgecss({ content: ['templates/**/*.html'] }))
        .pipe(dest('app/static/style/css'));
}

// Watch file function
function watchTask() {
    watch(['app/static/style/css_library/**/*.scss'], compileSass);
    // watch(['templates/**/*.html'], applyPurgeCSS);
}

exports.default = series(compileSass, watchTask);
//include this above when needed 'applyPurgeCSS,'