{
  description = "A python devshell containing all the dependencies required to run this bot";

  inputs.nixpkgs.url = "nixpkgs/nixpkgs-unstable";

  outputs = { self, nixpkgs, ... }:
  let
    system = "x86_64-linux";
    pkgs = import nixpkgs {
      inherit system;
    };
  in {
    devShells.${system}.default = pkgs.mkShell {
      packages = with pkgs; [
        python312
        python312Packages.matplotlib
        python312Packages.discordpy
        python312Packages.tkinter
        python312Packages.sv-ttk
        python312Packages.requests
        python312Packages.pytz
      ];
      shellHook = ''
        echo "Python devShell"
      '';
    };
  };
}
