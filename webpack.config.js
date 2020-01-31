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
  output: {
    path: path.resolve(__dirname, 'site'),
    filename: 'bundle.js',
  },
  plugins: [
    // Inject the bundle into this html file ...
    new HtmlWebpackPlugin({template: './templates/index.html'}),
  ],
  // Dont pack these into the bundle ... https://webpack.js.org/configuration/externals/
  externals: {
    _: 'lodash',
    d3: 'd3'
  }
};
