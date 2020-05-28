var HtmlWebpackPlugin = require('html-webpack-plugin');
const path = require('path');

// Web pack is useful ... since I can add more type script files and not have to modify the HTML ...
// https://webpack.js.org/guides/getting-started/
// https://webpack.js.org/concepts/
// https://webpack.js.org/guides/typescript/

module.exports = {
  entry: './src/ts/index.ts',  // Start at this type script file ... and recursively go through the imports
  module: {
    rules: [
      {
        test: /\.tsx?$/,
        use: 'ts-loader',
        exclude: /node_modules/,
      },
    ],
  },
  resolve: {
    extensions: [ '.tsx', '.ts'],
  },
  // https://webpack.js.org/configuration/output/
  output: {
    path: path.resolve(__dirname, 'site'),
    filename: 'bundle.js',
    library: 'sacredPatterns', // this is needed so other js can use it!
    libraryTarget: 'umd',
        // https://github.com/umdjs/umd
  },
  plugins: [
    // Inject the bundle into this html file ...
    new HtmlWebpackPlugin({
        filename: 'index.html',
        template: './templates/index.tpl',
        hash: true,
        inject: false,
        minify: false,
    }),
  ],
  // Dont pack these into the bundle ... https://webpack.js.org/configuration/externals/
  externals: {
    _: 'lodash',
    d3: 'd3'
  },
};
