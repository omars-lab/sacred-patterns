const HtmlWebpackPlugin = require('html-webpack-plugin');
const { GitRevisionPlugin } = require('git-revision-webpack-plugin');
const path = require('path');

const gitRevisionPlugin = new GitRevisionPlugin();

module.exports = {
  mode: 'production',
  entry: './src/ts/index.ts',
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
    extensions: ['.tsx', '.ts', '.js'],
  },
  output: {
    path: path.resolve(__dirname, 'site'),
    filename: 'bundle.js',
    library: {
      name: 'sacredPatterns',
      type: 'umd',
    },
    globalObject: 'globalThis',
    clean: true,
  },
  plugins: [
    new HtmlWebpackPlugin({
      filename: 'index.html',
      template: './templates/index.tpl',
      hash: true,
      inject: 'head',
      scriptLoading: 'blocking',
      minify: false,
      templateParameters: {
        VERSION: gitRevisionPlugin.version(),
        COMMITHASH: gitRevisionPlugin.commithash(),
        BRANCH: gitRevisionPlugin.branch(),
      },
    }),
    gitRevisionPlugin,
  ],
  externals: {
    lodash: {
      commonjs: 'lodash',
      commonjs2: 'lodash',
      amd: 'lodash',
      root: '_',
    },
    d3: 'd3',
  },
  devServer: {
    static: {
      directory: path.join(__dirname, 'site'),
    },
    port: 3000,
  },
};
