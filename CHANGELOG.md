# Changelog

## [1.3.0](https://github.com/fryoll/zendure-local-ha/compare/v1.2.0...v1.3.0) (2026-04-30)


### Features

* Add Zendure Local agent documentation and CLAUDE context; update README and manifest links ([f7a362d](https://github.com/fryoll/zendure-local-ha/commit/f7a362dd01ede15bc21b113dcc2bb42da080c154))
* extract detect_percent_scale into shared utils module ([02a7fa3](https://github.com/fryoll/zendure-local-ha/commit/02a7fa300558d952c8ee6a368f23cff7002f30ca))


### Bug Fixes

* cancel coordinator timer on unload and in config flow tests ([f7d7b3f](https://github.com/fryoll/zendure-local-ha/commit/f7d7b3f5cf0241eb3535dd8d91f4ec21ec3df69d))
* improve detect_percent_scale robustness and test clarity ([235391c](https://github.com/fryoll/zendure-local-ha/commit/235391c40568652e1fb00d182177e9c006c6957e))


### Code Refactoring

* replace duplicated _detect_percent_scale with shared utils.detect_percent_scale ([cc88f22](https://github.com/fryoll/zendure-local-ha/commit/cc88f22e4565ea776099ccee3aa843c54b4e6aa9))


### Documentation

* add CI, licence, and HACS badges to README ([f7c238b](https://github.com/fryoll/zendure-local-ha/commit/f7c238b5ffb5a65e5888c77014b9ab4327fbca7d))
* add CONTRIBUTING guide ([130d94a](https://github.com/fryoll/zendure-local-ha/commit/130d94a3ed32589317d50923c5fff9ffacbd8f4c))
* add public repo cleanup design spec ([a1a91b9](https://github.com/fryoll/zendure-local-ha/commit/a1a91b9dc9f0e2af3e7145fffe988725fbbd6b78))
* add public repo cleanup implementation plan ([608128f](https://github.com/fryoll/zendure-local-ha/commit/608128fc9d771cc7224d2e7b443065ab6d00e487))
* align coverage command in CONTRIBUTING with CI threshold ([279b1d7](https://github.com/fryoll/zendure-local-ha/commit/279b1d7406b1543d36738cb890afd924fefc20bf))


### Miscellaneous

* add .worktrees to .gitignore ([bb912dd](https://github.com/fryoll/zendure-local-ha/commit/bb912dd8baefdeb41f9c702e0cd8b350f445e7f0))
* add MIT licence ([564ee38](https://github.com/fryoll/zendure-local-ha/commit/564ee38b96ba781a0e6fff662a6482ebb50cb19d))
* **ci:** add CI workflow to run tests on push and PR ([70c31f4](https://github.com/fryoll/zendure-local-ha/commit/70c31f46205194f57f9ed7942539e9fd2ad569af))
* **ci:** gate publish on tests passing ([354d8d6](https://github.com/fryoll/zendure-local-ha/commit/354d8d605db6a9bfbc145c66820943faa5ab60e0))
* prepare repo for public release ([553f89f](https://github.com/fryoll/zendure-local-ha/commit/553f89f725152136b18d48a75762e3d66eba0a4d))

## [1.2.0](https://github.com/fryoll/zendure-local-ha/compare/v1.1.0...v1.2.0) (2026-04-30)


### Features

* Add CI and release workflows, initial project structure, and tests ([5cd0618](https://github.com/fryoll/zendure-local-ha/commit/5cd061801aaf64508581172f8f4b361449d48b64))
* Add commitizen configuration, pre-commit hooks, and development guidelines ([37f66f7](https://github.com/fryoll/zendure-local-ha/commit/37f66f7d235f8393d07b4ab5c2ddd7402e996511))
* Add input limit functionality and update related documentation and tests ([71c0e29](https://github.com/fryoll/zendure-local-ha/commit/71c0e298e726a8dd28b8c50240361f50947293a2))
* Enhance property write functionality with serial number and delay for acknowledgment ([48de0c4](https://github.com/fryoll/zendure-local-ha/commit/48de0c435cb9269d88543092abd86d844e687c7c))
* Enhance release-please configuration with changelog sections and bootstrap SHA ([d4728fe](https://github.com/fryoll/zendure-local-ha/commit/d4728fec999e22346e1c5b43b330ed2117f99f4a))
* Exclude __pycache__ and Python bytecode files from HACS release zip and add .gitignore ([fa38fb2](https://github.com/fryoll/zendure-local-ha/commit/fa38fb2e35e47fe881577826fbe1b88b7779ebaf))
* Integrate CI testing into release workflow with Python setup and test execution ([1fb8d10](https://github.com/fryoll/zendure-local-ha/commit/1fb8d10c5d349b6bcbc17dc9c4dd8f1cbfe9b1c8))


### Bug Fixes

* Change git input validation setting from "error" to true in settings.json ([556d1c0](https://github.com/fryoll/zendure-local-ha/commit/556d1c0cc27b310b6ee066f00a4687d898bc156f))
* Correct value keys for power and energy sensors in sensor.py and update related test assertions ([8bb95ff](https://github.com/fryoll/zendure-local-ha/commit/8bb95ffdac5360711adc3f1bc359468080882a88))
* Update release-please-action to version 5 in release workflow ([8d48a02](https://github.com/fryoll/zendure-local-ha/commit/8d48a0227e11c4ba37e080c26bb75c196043ecb3))


### Code Refactoring

* Remove test job from release workflow to streamline process ([aeeda7a](https://github.com/fryoll/zendure-local-ha/commit/aeeda7a58cd1d3fc283400f2d09874d64c1dc280))


### Miscellaneous

* Add a blank line for improved readability in release workflow ([8cf61f3](https://github.com/fryoll/zendure-local-ha/commit/8cf61f3e621cb647c1a8df67cfa634a6d613b629))
* **main:** release 1.1.0 ([c4f99bd](https://github.com/fryoll/zendure-local-ha/commit/c4f99bd91def6117fd5a6a060ac0a94872572d1b))
* **main:** release 1.1.0 ([4640ce1](https://github.com/fryoll/zendure-local-ha/commit/4640ce1b85201d887d60ed2b83e4a269d5c36054))
* Remove cached Python bytecode files from __pycache__ directories ([ff2498c](https://github.com/fryoll/zendure-local-ha/commit/ff2498c485082d19c65b4f0754c11976156b1162))

## [1.1.0](https://github.com/fryoll/zendure-local-ha/compare/v1.0.0...v1.1.0) (2026-04-30)


### Features

* Add CI and release workflows, initial project structure, and tests ([5cd0618](https://github.com/fryoll/zendure-local-ha/commit/5cd061801aaf64508581172f8f4b361449d48b64))
* Add commitizen configuration, pre-commit hooks, and development guidelines ([37f66f7](https://github.com/fryoll/zendure-local-ha/commit/37f66f7d235f8393d07b4ab5c2ddd7402e996511))
* Add input limit functionality and update related documentation and tests ([71c0e29](https://github.com/fryoll/zendure-local-ha/commit/71c0e298e726a8dd28b8c50240361f50947293a2))
* Enhance property write functionality with serial number and delay for acknowledgment ([48de0c4](https://github.com/fryoll/zendure-local-ha/commit/48de0c435cb9269d88543092abd86d844e687c7c))
* Enhance release-please configuration with changelog sections and bootstrap SHA ([d4728fe](https://github.com/fryoll/zendure-local-ha/commit/d4728fec999e22346e1c5b43b330ed2117f99f4a))
* Exclude __pycache__ and Python bytecode files from HACS release zip and add .gitignore ([fa38fb2](https://github.com/fryoll/zendure-local-ha/commit/fa38fb2e35e47fe881577826fbe1b88b7779ebaf))
* Integrate CI testing into release workflow with Python setup and test execution ([1fb8d10](https://github.com/fryoll/zendure-local-ha/commit/1fb8d10c5d349b6bcbc17dc9c4dd8f1cbfe9b1c8))


### Bug Fixes

* Correct value keys for power and energy sensors in sensor.py and update related test assertions ([8bb95ff](https://github.com/fryoll/zendure-local-ha/commit/8bb95ffdac5360711adc3f1bc359468080882a88))
* Update release-please-action to version 5 in release workflow ([8d48a02](https://github.com/fryoll/zendure-local-ha/commit/8d48a0227e11c4ba37e080c26bb75c196043ecb3))


### Code Refactoring

* Remove test job from release workflow to streamline process ([aeeda7a](https://github.com/fryoll/zendure-local-ha/commit/aeeda7a58cd1d3fc283400f2d09874d64c1dc280))


### Miscellaneous

* Add a blank line for improved readability in release workflow ([8cf61f3](https://github.com/fryoll/zendure-local-ha/commit/8cf61f3e621cb647c1a8df67cfa634a6d613b629))
* Remove cached Python bytecode files from __pycache__ directories ([ff2498c](https://github.com/fryoll/zendure-local-ha/commit/ff2498c485082d19c65b4f0754c11976156b1162))
