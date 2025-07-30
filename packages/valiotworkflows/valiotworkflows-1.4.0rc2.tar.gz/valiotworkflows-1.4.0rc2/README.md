# valiotworkflows

Library to implement services and plugins for the Valiot Workflows framework.
For use with the `jobs` microservice and `WorkflowXXX` types.

## for MANTAINERS:

### Initial configuration

first of all, ensure you have configured poetry repositories correctly:
`poetry config repositories.valiot https://pypi.valiot.io/`

and their credentials:

For private valiot's pypi:

`poetry config http-basic.valiot <username> <password>`

(_ask adrian to send you the proper username and password for this step_)

And for public pypi:

`poetry config pypi-token.pypi <pypi-token>`

(_ask adrian or baruc to generate a token for you_)

then,

### regular publish steps (after initial configuration)

deploy using:

`poetry version <patch | minor | major>`

then publish to valiot's private pypi:

`poetry publish --build -r valiot # build and PUBLISH TO PRIVATE VALIOTs PYPI`

or:

`poetry publish -r valiot`

(if you already built the package)

After release, publish to github:

`cat gstorm/__version__.py`

`gh release create`

`gh release upload v<#.#.#> ./dist/gstorm-<#.#.#>-py3-none-any.whl`

and don't forget to keep the `CHANGELOG.md` updated!
