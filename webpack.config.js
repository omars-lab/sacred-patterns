var HtmlWebpackPlugin = require('html-webpack-plugin');
const path = require('path');
// https://webpack.js.org/guides/getting-started/
// https://webpack.js.org/concepts/
// https://webpack.js.org/guides/typescript/
module.exports = {
  entry: './src/ts/index.ts',                                // Start at this type script file ... and recursively go through the imports
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
    filename: 'bundle.js',
    path: path.resolve(__dirname, 'dist'),
  },
  plugins: [
    // Inject the bundle into this html file ...
    new HtmlWebpackPlugin({template: './templates/index.html'}),
    // new webpack.ProvidePlugin({
    //     d3: 'd3',
    //     _: 'lodash'
    // }),
  ],
  // https://webpack.js.org/configuration/externals/
  // Dont pack these into the bundle ...
  externals: {
    _: 'lodash',
    d3: 'd3'
  }
};
