{
  description = "Development shell with Playwright and Python";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    playwright.url = "github:pietdevries94/playwright-web-flake";
  };

  outputs = { self, nixpkgs, flake-utils, playwright }: 
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
          overlays = [
            (final: prev: {
              # inherit (playwright.packages.${system}) playwright-test playwright-driver;
            })
          ];
        };
      in {
        devShells.default = pkgs.mkShell {
          packages = [
            (pkgs.python3.withPackages (ps: [
              ps.tomli
              ps.playwright
            ]))
            pkgs.certbot
            pkgs.playwright-test
          ];

          shellHook = ''
            export PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1
            export PLAYWRIGHT_BROWSERS_PATH="${pkgs.playwright-driver.browsers}"
            echo "Welcome to the Playwright and Python development shell!"
          '';
        };
      });
}
