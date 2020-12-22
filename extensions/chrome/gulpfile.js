var gulp = require('gulp');
var replace = require('gulp-replace');


gulp.task('default', function() {
  gulp.src('extension/js/*.js')
  .pipe(replace('http://localhost:5000', 'https://www.crestify.com'))
  .pipe(gulp.dest('build/js/'));

  gulp.src('extension/css/*.css')
  .pipe(gulp.dest('build/css/'));

  gulp.src('extension/*.js')
  .pipe(replace('http://localhost:5000', 'https://www.crestify.com'))
  .pipe(gulp.dest('build/'));

  gulp.src('extension/*.html')
  .pipe(gulp.dest('build/'));

  gulp.src('extension/*.json')
  .pipe(gulp.dest('build/'));

  gulp.src('extension/libs/*.js')
  .pipe(gulp.dest('build/libs/'));

  gulp.src('extension/libs/*.css')
  .pipe(gulp.dest('build/libs/'));

  gulp.src('extension/libs/bootstrap-3.3.4-dist/js/*.js')
  .pipe(gulp.dest('build/libs/bootstrap-3.3.4-dist/js/'));

   gulp.src('extension/libs/bootstrap-3.3.4-dist/css/*.css')
  .pipe(gulp.dest('build/libs/bootstrap-3.3.4-dist/css/'));

   gulp.src('extension/libs/bootstrap-3.3.4-dist/fonts/*.*')
  .pipe(gulp.dest('build/libs/bootstrap-3.3.4-dist/fonts/'));

   gulp.src('extension/*.png')
  .pipe(gulp.dest('build/'));

  gulp.src('extension/icons/*.png')
  .pipe(gulp.dest('build/icons/'));
});
