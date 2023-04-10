## Releasing `ipydatagrid`

### Tagging and creating a publishing environment

1. Create a new release branch: `git checkout -n release_1.0.x` (**replace .x with the actual version**).
2. Bump the version in `package.json` and `ipydatagrid/._version.py`.
3. Save, sign and commit your changes: `git commit -s -m "Release 1.0.x"`.
4. Open a PR with your release branch: `git push -u origin release_1.0.x`.
5. Once your PR has been merged (!), pull the new main branch `git checkout main && git pull upstream main`.
6. Add a new release tag: `git tag -a 1.0.x -m "Release 1.0.x"`.
7. Push the new tag to GitHub: `git push upstream --tags`.
8. Create a new conda environment: `conda create -n release_grid -c conda-forge python=3.8 python-build`.
9. Activate the environment: `conda activate release_grid`.

### Releasing on pypi

8. Make sure the `dist` folder under the `ipydatagrid` root folder is empty - delete previous release tarballs if they're present.
9. Build the Python release by running `python -m build` in the root directory.
10. Check the `dist` folder for the output from the build process. You should see the following files:
    - ipydatagrid-1.0.x-py3-none-any.whl
    - ipydatagrid-1.0.x.tar.gz
    - index.js
    - index.js.map
    - index.js.LICENSE.txt
11. Delete all \*.js, \*.map and \*.txt files: `rm *.js *.map *.txt`. Only the wheel and tarball files should remain.
12. Inspect the contents of the tarball to see everything is in check: `tar -tvf ipydatagrid-1.0.x.tar.gz`.
13. Install `twine` by running `pip install twine`.
14. Once `twine` is installed, upload the Python release to pypi: `twine upload dist/*`. You will need to have upload credentials for `ipydatagrid` on pypi for this step to work. If the step was successful, you should see an output similar to the one below:

```bash
Uploading ipydatagrid-1.0.x-py3-none-any.whl
100%|████████████████████████████████████████████████████████████████████████████████████████████| 3.38M/3.38M [00:04<00:00, 720kB/s]
Uploading ipydatagrid-1.0.x.tar.gz
100%|███████████████████████████████████████████████████████████████████████████████████████████| 22.4M/22.4M [00:07<00:00, 3.22MB/s]

View at:
https://pypi.org/project/ipydatagrid/1.0.x/
```

### Releasing on npm

15. In the root folder of the `ipydatagrid`, run `npm publish --dry-run`. This will perform a dry run release so you can check everything looks right before an actual release. It should generate an output similar to the one below:

```bash
webpack 5.34.0 compiled with 3 warnings in 93596 ms
npm notice
npm notice 📦  ipydatagrid@1.0.5
npm notice === Tarball Contents ===
npm notice 4.5kB   style/feathergrid.css
npm notice 56B     style/jupyter-widget.css
npm notice 4.5kB   lib/core/barrenderer.js
npm notice 11.1kB  lib/cellrenderer.js
npm notice 165.1kB lib/core/datagrid.js
npm notice 19.5kB  lib/datagrid.js
npm notice 1.3kB   lib/extension.js
npm notice 30.4kB  lib/feathergrid.js
npm notice 45.1kB  lib/core/filterMenu.js
npm notice 13.7kB  lib/core/graphicscontext.js
npm notice 5.2kB   lib/core/gridContextMenu.js
npm notice 13.6kB  lib/core/headerRenderer.js
npm notice 1.1MB   dist/index.js
npm notice 930B    lib/index.js
npm notice 1.4kB   lib/keyhandler.js
npm notice 3.1kB   lib/plugin.js
npm notice 114B    lib/core/transform.js
npm notice 10.8kB  lib/core/transformExecutors.js
npm notice 7.1kB   lib/core/transformStateManager.js
npm notice 6.2kB   lib/utils.js
npm notice 4.6kB   lib/core/valueRenderer.js
npm notice 3.8kB   lib/vegaexpr.js
npm notice 584B    lib/version.js
npm notice 7.8kB   lib/core/view.js
npm notice 16.7kB  lib/core/viewbasedjsonmodel.js
npm notice 4.0kB   package.json
npm notice 3.1kB   lib/core/barrenderer.js.map
npm notice 7.7kB   lib/cellrenderer.js.map
npm notice 128.2kB lib/core/datagrid.js.map
npm notice 15.8kB  lib/datagrid.js.map
npm notice 368B    lib/extension.js.map
npm notice 22.8kB  lib/feathergrid.js.map
npm notice 31.4kB  lib/core/filterMenu.js.map
npm notice 13.1kB  lib/core/graphicscontext.js.map
npm notice 2.8kB   lib/core/gridContextMenu.js.map
npm notice 10.6kB  lib/core/headerRenderer.js.map
npm notice 4.3MB   dist/index.js.map
npm notice 189B    lib/index.js.map
npm notice 689B    lib/keyhandler.js.map
npm notice 1.6kB   lib/plugin.js.map
npm notice 117B    lib/core/transform.js.map
npm notice 8.4kB   lib/core/transformExecutors.js.map
npm notice 4.9kB   lib/core/transformStateManager.js.map
npm notice 4.1kB   lib/utils.js.map
npm notice 3.7kB   lib/core/valueRenderer.js.map
npm notice 2.7kB   lib/vegaexpr.js.map
npm notice 287B    lib/version.js.map
npm notice 4.1kB   lib/core/view.js.map
npm notice 9.9kB   lib/core/viewbasedjsonmodel.js.map
npm notice 4.6kB   README.md
npm notice 416B    style/icons/arrow-down-short-dark.svg
npm notice 416B    style/icons/arrow-down-short.svg
npm notice 400B    style/icons/arrow-up-short-dark.svg
npm notice 400B    style/icons/arrow-up-short.svg
npm notice 349B    style/icons/filter-dark.svg
npm notice 349B    style/icons/filter.svg
npm notice 3.8kB   lib/core/barrenderer.d.ts
npm notice 4.5kB   lib/cellrenderer.d.ts
npm notice 38.0kB  lib/core/datagrid.d.ts
npm notice 2.6kB   lib/datagrid.d.ts
npm notice 25B     lib/extension.d.ts
npm notice 3.9kB   lib/feathergrid.d.ts
npm notice 10.0kB  lib/core/filterMenu.d.ts
npm notice 5.5kB   lib/core/graphicscontext.d.ts
npm notice 3.3kB   lib/core/gridContextMenu.d.ts
npm notice 2.5kB   lib/core/headerRenderer.d.ts
npm notice 103B    lib/index.d.ts
npm notice 584B    lib/keyhandler.d.ts
npm notice 231B    lib/plugin.d.ts
npm notice 1.6kB   lib/core/transform.d.ts
npm notice 3.2kB   lib/core/transformExecutors.d.ts
npm notice 2.7kB   lib/core/transformStateManager.d.ts
npm notice 1.4kB   lib/utils.d.ts
npm notice 1.4kB   lib/core/valueRenderer.d.ts
npm notice 1.4kB   lib/vegaexpr.d.ts
npm notice 262B    lib/version.d.ts
npm notice 4.7kB   lib/core/view.d.ts
npm notice 11.8kB  lib/core/viewbasedjsonmodel.d.ts
npm notice 1.5kB   LICENSE.txt
npm notice === Tarball Details ===
npm notice name:          ipydatagrid
npm notice version:       1.0.5
npm notice package size:  1.3 MB
npm notice unpacked size: 6.2 MB
npm notice shasum:        f8743bf45c0667b2f99631b73f5df465534549fc
npm notice integrity:     sha512-4E1xna+4Sy33k[...]eQx2mpnwvYKOw==
npm notice total files:   79
npm notice
+ ipydatagrid@1.0.5
```

One specific item to watch for is the inclusion of `dist/index.js` in the output generated by the console, as that's the file being used by CDNs, which `voila` relies on as a fallback.

16. If everything looks right, you can now publish to NPM. Login to NPM: `npm login` and enter your credentials.
17. Run `npm publish` in the root directory of `ipydatagrid`. You will need to have upload credentials for `ipydatagrid` on NPM for this step to work. If the publishing step was successful, you will see an output on your console which is similar to the one from step (15).

### Cleaning up the release environment

18. Deactivate the release environment: `conda deactivate`.
19. Delete the release environment: `conda env remove -n release_grid`.

Congratulations! You successfully published `ipydatagrid`!
