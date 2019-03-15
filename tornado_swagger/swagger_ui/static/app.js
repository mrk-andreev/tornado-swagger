(function () {
    window.onload = function () {
        window.ui = new SwaggerUIBundle({
            url: SWAGGER_CONFIG_URL,
            dom_id: "#swagger-ui-container",
            deepLinking: true,
            presets: [
                SwaggerUIBundle.presets.apis,
                SwaggerUIStandalonePreset
            ],
            plugins: [
                SwaggerUIBundle.plugins.DownloadUrl
            ],
            layout: "StandaloneLayout",
            validatorUrl: "https://validator.swagger.io/validator",
        });
    };
})();