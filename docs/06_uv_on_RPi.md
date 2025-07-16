## uv installation on RPi   

#### 1. Installation process
- for years `pip` + `venv` was my simple, but effective way to work with Python web applications (especially in Django),  
- this time `uv` will be the main tool for Python ecosystem :snake:,  
- I've used many tips from [Saas Pegasus](https://www.saaspegasus.com/guides/uv-deep-dive/) guide on `uv`, 
- first, the `uv` must be installed:  
```bash
artur@pawn-cluster:~ $ curl -LsSf https://astral.sh/uv/install.sh | sh
downloading uv 0.7.21 aarch64-unknown-linux-gnu
no checksums to verify
installing to /home/artur/.local/bin
  uv
  uvx
everything's installed!

To add $HOME/.local/bin to your PATH, either restart your shell or run:

    source $HOME/.local/bin/env (sh, bash, zsh)
    source $HOME/.local/bin/env.fish (fish)
artur@pawn-cluster:~ $ source $HOME/.local/bin/env
artur@pawn-cluster:~ $ uv --version
uv 0.7.21

```