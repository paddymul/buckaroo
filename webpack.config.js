const path = require('path');
const version = require('./package.json').version;
//import {TsconfigPathsPlugin} from 'tsconfig-paths-webpack-plugin';
const  TsconfigPathsPlugin = require('tsconfig-paths-webpack-plugin');

//import HtmlWebpackPlugin from 'html-webpack-plugin';
const HtmlWebpackPlugin = require('html-webpack-plugin');
const luminoThemeImages = /^.*@lumino\/default-theme.*.png$/;

const crypto = require('crypto');

// Workaround for loaders using "md4" by default, which is not supported in FIPS-compliant OpenSSL
const cryptoOrigCreateHash = crypto.createHash;
crypto.createHash = (algorithm) =>
  cryptoOrigCreateHash(algorithm == 'md4' ? 'sha256' : algorithm);

const  performance = {
    maxAssetSize: 100_000_000,
};

// Custom webpack rules

const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const devMode = process.env.NODE_ENV !== "production";

module.exports = {
  module: {
    rules: [

    ],
  },
  plugins: [].concat(devMode ? [] : [new MiniCssExtractPlugin()]),
};
const baseRules = [

    { test: /\.css$/, use: [ 'css-loader'],
      assert: { type: "css" },

      options: {
          exportType: "css-style-sheet",
      },
    },
                {
                    test: /\.scss$/,
                    use: [
                        // We're in dev and want HMR, SCSS is handled in JS
                        // In production, we want our css as files
                        "style-loader",
                        "css-loader",
                        {
                            loader: "postcss-loader",
                            options: {


                                postcssOptions: {
                                    plugins: [
                                        ["postcss-preset-env"],
                                    ],
                                },
                            },
                        },
                        "sass-loader"
                    ],
                },
  {
    test: luminoThemeImages,
    issuer: /\.css$/,
    use: {
      loader: 'url-loader',
    },
  },
  {
    test: /\.(jpg|png|gif|woff|woff2)$/,
    exclude: luminoThemeImages,
    use: ['file-loader'],
  },
    {
        test: /\.md$/,
        use: ['html-loader', 'markdown-loader']
    },
  {
    test: /\.svg(\?v=\d+\.\d+\.\d+)?$/,
    issuer: /\.css$/,
    use: {
      loader: 'svg-url-loader',
      options: { encoding: 'none', limit: 10000 },
    },
  },
];


const rules = [...baseRules,   { test: /\.tsx?$/, loader: 'ts-loader'
      {
        // If you enable `experiments.css` or `experiments.futureDefaults`, please uncomment line below
        // type: "javascript/auto",
        test: /\.(sa|sc|c)ss$/i,
        use: [
          devMode ? "style-loader" : MiniCssExtractPlugin.loader,
          "css-loader",
          "postcss-loader",
          "sass-loader",
        ],
      },

 }];
const demoRules = [...baseRules,
                {
                    test: /\.tsx?$/,
                    loader: 'ts-loader',
                    options: {
                        transpileOnly: true,
                        configFile: 'examples/tsconfig.json'
                    }
                }]


// Packages that shouldn't be bundled but loaded at runtime
const externals = ['@jupyter-widgets/base'];

const resolve = {
  // Add '.ts' and '.tsx' as resolvable extensions.
    extensions: ['.webpack.js', '.web.js', '.ts', '.js', '.tsx', 'css'],
    plugins: [new TsconfigPathsPlugin()],
  fallback: { crypto: false },
};

module.exports = [
  /**
   * Notebook extension
   *
   * This bundle only contains the part of the JavaScript that is run on load of
   * the notebook.
   */
  {
    entry: './js/extension.ts',
    output: {
      filename: 'index.js',
      path: path.resolve(__dirname, 'buckaroo', 'nbextension'),
      libraryTarget: 'amd',
    },
    module: {
      rules: rules,
    },
    devtool: 'source-map',
    externals,
    resolve,
      // plugins: [new HtmlWebpackPlugin({
      //           template: './examples/index.html'
      //       })]
      performance


  },

  /**
   * Embeddable buckaroo bundle
   *
   * This bundle is almost identical to the notebook extension bundle. The only
   * difference is in the configuration of the webpack public path for the
   * static assets.
   *
   * The target bundle is always `dist/index.js`, which is the path required by
   * the custom widget embedder.
   */
  {
    entry: './js/index.ts',
    output: {
      filename: 'index.js',
      path: path.resolve(__dirname, 'dist'),
      libraryTarget: 'amd',
      library: 'buckaroo',
      publicPath: 'https://unpkg.com/buckaroo@' + version + '/dist/',
    },
    devtool: 'source-map',
    module: {
      rules: rules,
    },
    externals,
    resolve,
        devServer: {
            port: 8030
        },
      performance

  },

  /**
   * Documentation widget bundle
   *
   * This bundle is used to embed widgets in the package documentation.
   */
  {
    entry: './js/index.ts',
    output: {
      filename: 'embed-bundle.js',
      path: path.resolve(__dirname, 'docs', 'source', '_static'),
      library: 'buckaroo',
      libraryTarget: 'amd',
    },
    module: {
      rules: rules,
    },
    devtool: 'source-map',
    externals,
    resolve,
      performance

  },
];
