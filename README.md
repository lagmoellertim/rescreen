<h1 align="center">
    <img alt="logo" src="https://github.com/lagmoellertim/rescreen/raw/main/assets/banner.png">
</h1>

*<p align="center">Display Manager with fractional scaling support for X11 </p>*

<p align="center">
    <a href="https://github.com/lagmoellertim/rescreen/blob/master/LICENSE" target="_blank"><img src="https://img.shields.io/badge/license-MIT-blue.svg?style=flat" alt="MIT License Badge"/></a>
    <a href="https://github.com/lagmoellertim/rescreen/actions" target="_blank"><img src="https://github.com/lagmoellertim/rescreen/workflows/Publish/badge.svg" alt="Github Action Badge"/></a>
    <a href="https://www.codacy.com/gh/lagmoellertim/rescreen/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=lagmoellertim/rescreen&amp;utm_campaign=Badge_Grade" target="_blank"><img src="https://app.codacy.com/project/badge/Grade/8a6ecf9dd5524962b2f04854a5e0c435" alt="Codacy Badge"/></a>
</p>

---

<p align="center">
  <img src="https://github.com/lagmoellertim/rescreen/raw/main/assets/gui.png" width="70%"/>
</p>

## Introduction
ReScreen is an **open-source** tool that tries to simplify the per-display fractional scaling problem many users have on
Linux inside an X11-Session. You can use the **graphical display configurator** to configure your display setup to your
liking. When you are satisfied with the setup, the configuration is saved and applied to your system. Everytime the
connected display configuration changes, ReScreen automatically tries to find a matching profile and if it found one, it
gets applied. You can also manually force this behaviour using the **command line interface**.

## Installation
### Debian/Ubuntu
1. Download the `.deb`-File from the [Release Page](https://github.com/lagmoellertim/rescreen/releases).

2. To install it on your system, use
    ```shell
    $ sudo apt-get install -f <path to the .deb-File>
    ```

A package repository for deb packages is in the making :construction:

### Arch
1. Download the `.pkg.tar.zst`-File from the [Release Page](https://github.com/lagmoellertim/rescreen/releases).
2. To install it on your System, use
    ```shell
    $ sudo pacman -U <path to the .pkg.tar.zst-File>
    ```

An easier method for installing this package on Arch is by using the AUR :arrow_down:

### AUR
1. With an AUR-Helper of your choice (I will use `yay` in this example), install the package using
    ```shell
    $ yay -S rescreen
    ```

### PIP
1. > This will not embed rescreen into your system, only the command line tool gets installed. The GUI is not available
    > as a shortcut in the menu and the screen change watcher does not automatically run in the background.
    >
    > You also need to install the required system dependencies on your own, including `xrandr`, `xev`, `loginctl`, 
    > `whoami` and `edid-decode`

    To install only the command line tools on your system, you can use
    ```shell
    $ pip install rescreen
    ```

## Command Line Usage
### Detect and save the current display configuration
```shell
$ rescreen save
```

### Detect the current display configuration, try to find a matching profile and apply it if found
```shell
$ rescreen load
```

### Start the Graphical Display Configurator
```shell
$ rescreen gui
```

### Start the display change watcher that automatically tries to apply the matching profile
>Note: This command needs to be run with superuser-permissions. The preferred way of using the watcher is to have it
> installed as a systemd-service 
> 
> (This is done in the bundled packages for the distributions)
```shell
$ rescreen watcher
```

## Contributing

If you are missing a feature or have new idea, go for it! That is what open-source is for! 😃

## Author

**Tim-Luca Lagmöller** ([@lagmoellertim](https://github.com/lagmoellertim))

## Donations / Sponsors

I'm part of the official GitHub Sponsors program where you can support me on a monthly basis.

<a href="https://github.com/sponsors/lagmoellertim" target="_blank"><img src="https://github.com/lagmoellertim/shared-repo-files/raw/main/github-sponsors-button.png" alt="GitHub Sponsors" height="35px" ></a>

You can also contribute by buying me a coffee (this is a one-time donation).

<a href="https://ko-fi.com/lagmoellertim" target="_blank"><img src="https://github.com/lagmoellertim/shared-repo-files/raw/main/kofi-sponsors-button.png" alt="Ko-Fi Sponsors" height="35px" ></a>

Thank you for your support!

## License

The Code is licensed under the

[MIT License](https://github.com/lagmoellertim/unsilence/blob/master/LICENSE)

Copyright © 2022-present, [Tim-Luca Lagmöller](https://github.com/lagmoellertim)

## Have fun :tada: