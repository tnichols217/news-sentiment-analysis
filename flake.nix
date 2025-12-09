{
  description = "Data Analysis Homework 2";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    treefmt-nix.url = "github:numtide/treefmt-nix";
  };

  outputs =
    {
      self,
      nixpkgs,
      flake-utils,
      treefmt-nix,
    }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = import nixpkgs { inherit system; };

        python = pkgs.python3.withPackages (
          ps: with ps; [
            black
            matplotlib
            pandas
            numpy
            scipy
            pandas-stubs
            beautifulsoup4
            python-dotenv
            (ps.buildPythonPackage rec {
              pname = "matplotlib_stubs";
              version = "0.3.11";
              pyproject = true;
              src = pkgs.fetchPypi {
                inherit pname version;
                sha256 = "sha256-9rpvn6WYi3jDcyhPJueFA04zYNZrLKQcZanWJyBvfIs=";
              };

              build-system = with ps; [
                hatchling
                setuptools-scm
              ];

              dependencies = with ps; [
                matplotlib
                numpy
                pandas
              ];
            })
            (ps.buildPythonPackage rec {
              pname = "mediacloud";
              version = "4.5.0";

              pyproject = true;  # because you use flit_core build-backend

              src = pkgs.fetchPypi {
                inherit pname version;
                sha256 = "sha256-XMhIjj4eaEd1qjCpfKU5LGlI3BFToShRNrhnpJIfoas=";
              };

              build-system = [
                ps.flit-core
              ];

              propagatedBuildInputs = [
                ps.requests
              ];

              # Optional extras
              passthru.optional-dependencies = {
                dev = with ps; [
                  pre-commit
                  flake8
                  mypy
                  isort
                  types-urllib3
                  types-requests
                  python-dotenv
                ];
                test = with ps; [
                  pytest
                ];
              };

              # Enable tests if you want Nix to run pytest
              doCheck = true;
              nativeCheckInputs = with ps; [
                pytest
              ];

              meta = with lib; {
                description = "Media Cloud API Client Library";
                homepage = "https://mediacloud.org";
                license = licenses.asl20;
                maintainers = [];
              };
            })
          ]
        );

        treefmtconfig = treefmt-nix.lib.evalModule pkgs {
          projectRootFile = "flake.nix";
          programs = {
            nixfmt.enable = true;
            yamlfmt.enable = true;
          };
        };
      in
      {
        formatter = treefmtconfig.config.build.wrapper;

        devShells = {
          default = pkgs.mkShell {
            packages = with pkgs; [
              ruff
              nil
              nixd
              nixfmt
              basedpyright
            ] ++ [
              python
            ];
          };
        };

        packages = rec {
          default = plots;
          qol = pkgs.callPackage ./nix/qol_src.nix {};
          plots = pkgs.callPackage ./nix/build.nix { inherit qol; };
        };
      }
    );
}
