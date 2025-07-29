# Changelog

## 0.1.0-alpha.2 (2025-04-24)

Full Changelog: [v0.1.0-alpha.1...v0.1.0-alpha.2](https://github.com/ShortGenius/shortgenius-sdk-python/compare/v0.1.0-alpha.1...v0.1.0-alpha.2)

### Bug Fixes

* **ci:** ensure pip is always available ([#18](https://github.com/ShortGenius/shortgenius-sdk-python/issues/18)) ([a351c01](https://github.com/ShortGenius/shortgenius-sdk-python/commit/a351c01c39fd92df422bf02c25ea3c1c5dd03694))
* **ci:** remove publishing patch ([#19](https://github.com/ShortGenius/shortgenius-sdk-python/issues/19)) ([bd9ccbf](https://github.com/ShortGenius/shortgenius-sdk-python/commit/bd9ccbf64ee8dc036e24c5212c0ec6566e8285a6))
* **perf:** optimize some hot paths ([cc75f61](https://github.com/ShortGenius/shortgenius-sdk-python/commit/cc75f618e9d8a09685d6c6d6888ce4629b8e087b))
* **perf:** skip traversing types for NotGiven values ([1944234](https://github.com/ShortGenius/shortgenius-sdk-python/commit/19442348bad148bfb51193989dd3f23ab837b738))
* **pydantic v1:** more robust ModelField.annotation check ([9474748](https://github.com/ShortGenius/shortgenius-sdk-python/commit/947474823069f5e280270711f4388000ba6d8d39))
* **types:** handle more discriminated union shapes ([#17](https://github.com/ShortGenius/shortgenius-sdk-python/issues/17)) ([af872e8](https://github.com/ShortGenius/shortgenius-sdk-python/commit/af872e8f259f3f7fe8a17df464c31054d517c801))


### Chores

* broadly detect json family of content-type headers ([375e3aa](https://github.com/ShortGenius/shortgenius-sdk-python/commit/375e3aad00c564c08ab0c9e19a43e703b562b4b8))
* **ci:** add timeout thresholds for CI jobs ([5ff7bff](https://github.com/ShortGenius/shortgenius-sdk-python/commit/5ff7bffddd6d14d1b9f808ca3cc95bb22e206c98))
* **ci:** only use depot for staging repos ([ae8834f](https://github.com/ShortGenius/shortgenius-sdk-python/commit/ae8834f257d6b45a0fd4e17697ef993b783cfda3))
* **client:** minor internal fixes ([0803108](https://github.com/ShortGenius/shortgenius-sdk-python/commit/0803108d7e1813316508ff4b599f04a2320903c0))
* fix typos ([#20](https://github.com/ShortGenius/shortgenius-sdk-python/issues/20)) ([84f6b34](https://github.com/ShortGenius/shortgenius-sdk-python/commit/84f6b348ec773f846e6bf87211043c9bb65f0dc6))
* **internal:** base client updates ([672b8f8](https://github.com/ShortGenius/shortgenius-sdk-python/commit/672b8f80e1c1172fec76a94a01660a3b6ddc3b7c))
* **internal:** bump pyright version ([7d4aff9](https://github.com/ShortGenius/shortgenius-sdk-python/commit/7d4aff9a9bf3ed3cf2644f16119140dd5687944d))
* **internal:** bump rye to 0.44.0 ([#16](https://github.com/ShortGenius/shortgenius-sdk-python/issues/16)) ([9a80c8b](https://github.com/ShortGenius/shortgenius-sdk-python/commit/9a80c8b744d86dc1708a248cf7506fdfe3741ec9))
* **internal:** codegen related update ([aa373fa](https://github.com/ShortGenius/shortgenius-sdk-python/commit/aa373faa69af1d7fab4e045cadbe3baf57c47ead))
* **internal:** codegen related update ([#15](https://github.com/ShortGenius/shortgenius-sdk-python/issues/15)) ([58cbde4](https://github.com/ShortGenius/shortgenius-sdk-python/commit/58cbde4b50cd13387aca44ddc965689bef631526))
* **internal:** expand CI branch coverage ([c74a744](https://github.com/ShortGenius/shortgenius-sdk-python/commit/c74a74451aa4679d4b5039d84989f214d47ebb92))
* **internal:** fix list file params ([c3dfa90](https://github.com/ShortGenius/shortgenius-sdk-python/commit/c3dfa907d373fc7a87b4838aa64290778b04914b))
* **internal:** import reformatting ([ff6aac8](https://github.com/ShortGenius/shortgenius-sdk-python/commit/ff6aac8e46df32286db532b3242efef92cc61cb1))
* **internal:** reduce CI branch coverage ([b292f3c](https://github.com/ShortGenius/shortgenius-sdk-python/commit/b292f3ca19e61e025d88b67e39156d82ca444ea5))
* **internal:** refactor retries to not use recursion ([901ed47](https://github.com/ShortGenius/shortgenius-sdk-python/commit/901ed479f748531fbc4bb78e68e9856400476850))
* **internal:** remove extra empty newlines ([#14](https://github.com/ShortGenius/shortgenius-sdk-python/issues/14)) ([17096b4](https://github.com/ShortGenius/shortgenius-sdk-python/commit/17096b4e08bab717e20eea3abb1218121dc8e707))
* **internal:** remove trailing character ([#21](https://github.com/ShortGenius/shortgenius-sdk-python/issues/21)) ([3dc644e](https://github.com/ShortGenius/shortgenius-sdk-python/commit/3dc644e93599c83668d1049b6e9567c424bf9754))
* **internal:** slight transform perf improvement ([#22](https://github.com/ShortGenius/shortgenius-sdk-python/issues/22)) ([bb6569d](https://github.com/ShortGenius/shortgenius-sdk-python/commit/bb6569da8a40dfed4a7956dacef9744d2ee403ae))
* **internal:** update models test ([bb459af](https://github.com/ShortGenius/shortgenius-sdk-python/commit/bb459af3a7a6110318ef19eff5e3289d150f4d55))
* **internal:** update pyright settings ([0616af3](https://github.com/ShortGenius/shortgenius-sdk-python/commit/0616af3a7cdd1181b3bda33fc3f891e5ad77f7f8))

## 0.1.0-alpha.1 (2025-03-06)

Full Changelog: [v0.0.1-alpha.1...v0.1.0-alpha.1](https://github.com/ShortGenius/shortgenius-sdk-python/compare/v0.0.1-alpha.1...v0.1.0-alpha.1)

### Features

* **api:** add code samples ([#5](https://github.com/ShortGenius/shortgenius-sdk-python/issues/5)) ([b4551bb](https://github.com/ShortGenius/shortgenius-sdk-python/commit/b4551bba2c0c564839e20318acb3377cfbc29bb4))
* **api:** api update ([#10](https://github.com/ShortGenius/shortgenius-sdk-python/issues/10)) ([e4b2898](https://github.com/ShortGenius/shortgenius-sdk-python/commit/e4b28987b783c1980613a47a8c1b5095cf4c3b9c))


### Chores

* **docs:** update client docstring ([#8](https://github.com/ShortGenius/shortgenius-sdk-python/issues/8)) ([f3ab1a3](https://github.com/ShortGenius/shortgenius-sdk-python/commit/f3ab1a3fdae25f96926c571747fd8bf73b273830))
* **internal:** remove unused http client options forwarding ([#9](https://github.com/ShortGenius/shortgenius-sdk-python/issues/9)) ([73777c9](https://github.com/ShortGenius/shortgenius-sdk-python/commit/73777c924ebd69f1a621eb8af872f2f5bcc865cb))


### Documentation

* update URLs from stainlessapi.com to stainless.com ([#7](https://github.com/ShortGenius/shortgenius-sdk-python/issues/7)) ([6c825ad](https://github.com/ShortGenius/shortgenius-sdk-python/commit/6c825addf5f75025c71325209f3637b1f95c7939))

## 0.0.1-alpha.1 (2025-02-25)

Full Changelog: [v0.0.1-alpha.0...v0.0.1-alpha.1](https://github.com/ShortGenius/shortgenius-sdk-python/compare/v0.0.1-alpha.0...v0.0.1-alpha.1)

### Chores

* go live ([#1](https://github.com/ShortGenius/shortgenius-sdk-python/issues/1)) ([d3c8bc1](https://github.com/ShortGenius/shortgenius-sdk-python/commit/d3c8bc19fe069344ce7bbbdfd8ecc6ef56ce19d7))
* update SDK settings ([#3](https://github.com/ShortGenius/shortgenius-sdk-python/issues/3)) ([fdd8c1f](https://github.com/ShortGenius/shortgenius-sdk-python/commit/fdd8c1f4e52329eefca1037e67df809fe4c169fe))
