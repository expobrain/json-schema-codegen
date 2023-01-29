// @flow

/**
 * Courtesy of https://github.com/yarnpkg/yarn/blob/master/scripts/build-webpack.js
 */

const path = require("path");

const webpack = require("webpack");
const ProgressBarPlugin = require("progress-bar-webpack-plugin");
const CaseSensitivePathsPlugin = require("case-sensitive-paths-webpack-plugin");

const basedir = path.join(__dirname, "..");

// Use the real node __dirname and __filename in order to get Yarn's source
// files on the user's system. See constants.js
const nodeOptions = {
  __filename: false,
  __dirname: false,
};

module.exports = {
  target: "node",
  node: nodeOptions,
  mode: "production",
  entry: { ast_to_js: path.join(basedir, "scripts", "ast_to_js.js") },
  module: {
    rules: [
      {
        test: /\.js$/,
        exclude: /node_modules/,
        loader: "babel-loader",
      },
    ],
  },
  plugins: [
    new webpack.LoaderOptionsPlugin({
      options: {
        minimize: true,
      },
    }),
    new ProgressBarPlugin(),
    new CaseSensitivePathsPlugin(),
    new webpack.BannerPlugin({
      banner: "#!/usr/bin/env node",
      raw: true,
    }),
  ],
  output: {
    filename: `[name]`,
    path: path.join(basedir, "bin"),
    libraryTarget: "commonjs2",
  },
};
