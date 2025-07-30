/**
 * Configuration for Playwright using default from @jupyterlab/galata
 */
/* eslint-disable */
const baseConfig = require("@jupyterlab/galata/lib/playwright-config");

module.exports = {
    ...baseConfig,
    webServer: {
        command: "yarn start",
        url: "http://localhost:8888/lab",
        timeout: 120 * 1000,
        reuseExistingServer: !process.env.CI,
    },
};
