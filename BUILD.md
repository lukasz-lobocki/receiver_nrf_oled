# receiver_nrf_oled

## Typical build workflow

```bash
git add --update
```

```bash
git commit -m "fix: change"
```

```bash
poetry run semantic-release version
```

```bash
git push
```

## Cookiecutter initiation

```bash
cookiecutter \
  ssh://git@github.com/lukasz-lobocki/py-pkgs-cookiecutter.git \
  package_name="receiver_nrf_oled"
```

### was run with following variables

- package_name: **`receiver_nrf_oled`**;
package_short_description: `Receiving end of temperature, pressure, humidity.`

- package_version: `0.5.2`; python_version: `3.10`

- author_name: `Lukasz Lobocki`;
open_source_license: `CC0 v1.0 Universal`

- __package_slug: `receiver_nrf_oled`; include_github_actions: `no`

### on

`2023-07-28 15:09:05 +0200`
