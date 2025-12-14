const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
  transpileDependencies: true,
  configureWebpack: {
    output: {
      filename: 'js/[name].js',
      chunkFilename: 'js/[name].js'
    }
  },
  css: {
    extract: {
      filename: 'css/[name].css',
      chunkFilename: 'css/[name].css'
    }
  }
})
