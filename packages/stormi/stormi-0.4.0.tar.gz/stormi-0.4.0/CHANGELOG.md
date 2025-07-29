# Changelog

## [stormi-v0.4.0](https://github.com/pinellolab/stormi/compare/stormi-v0.3.0...stormi-v0.4.0) (2025-06-23)

### Features

* **__init__.py:** Added the new ManualEuler model. ([36c4f32](https://github.com/pinellolab/stormi/commit/36c4f324d76e604f666ae9d1e6d4523757cdae50))
* **AmortizedNormal:** Added amortization for path weights and jit warmup function that ensures amortized parameters match prior before training. ([519a034](https://github.com/pinellolab/stormi/commit/519a03435492f1a8ae75e7e3614152faafe6a67d))
* **AmortizedNormal:** Better handling of random seed, made path weights scale a learnable parameter and made warmup JIT compatible. ([4efa0c1](https://github.com/pinellolab/stormi/commit/4efa0c149a0b14459b9670517f325f302600e9d2))
* **AmortizedNormal:** Made path weights scale learnable instead of fixed. ([8da4788](https://github.com/pinellolab/stormi/commit/8da4788731d7dc3f78fbe447c1aed3cb88f37e40))
* **AmortizedNormal:** Make path weight scale learnable. ([e6eba15](https://github.com/pinellolab/stormi/commit/e6eba157b1bb83e126c617ab78c361aec32dcc74))
* **model:** New jit compatible SDE model, with 2 layer mlp, option to include more prior info about paths and time, numerically stable logistic normal prior for path weights and one shared initial condition for all paths. ([88bb38b](https://github.com/pinellolab/stormi/commit/88bb38bbfcd3ceaa903550513fe1fb698fd02572))
* **models:** Model with a manual implementation of Euler integration in jax that is faster than our current diffrax version. ([f3ef7d0](https://github.com/pinellolab/stormi/commit/f3ef7d02e57085f0043d0ace76ab7e21b614a141))
* **plotting:** Plotting function showing gene expression trajectories for multiple stochastic paths side by side. ([9eb0804](https://github.com/pinellolab/stormi/commit/9eb0804b881d165c798f847cef66613542a33624))
* **preprocessing:** Simple gene filtering function when just using RNA data (not ATAC). ([eea3974](https://github.com/pinellolab/stormi/commit/eea397426747a35b5826462c4e6a79fa8e6036f5))
* **RNA_2layers_MultiplePaths_SDE:** Added option to return alpha with and without diffusions at each step. ([0756b35](https://github.com/pinellolab/stormi/commit/0756b353f1f424a7bf84914f8ad21903436e4a0c))
* **RNA1_layer.py:** Changed mlp weights to regular numpyro params, which saves memory ([8fe0a82](https://github.com/pinellolab/stormi/commit/8fe0a82272adf0c4cda8e432be2771a8a3e183d5))
* **test_workflow_SDE:** Lowered batch size to test minibatch training. ([740e929](https://github.com/pinellolab/stormi/commit/740e929512e1c77082aa7ba18d4c579d9e5c925e))
* **tests:** tests for new workflow with SDE model and jit training ([d5413ea](https://github.com/pinellolab/stormi/commit/d5413ea60f582f24141d433b2dc0b11ac15391fc))
* **train:** New JIT compatible svi training function. ([c888825](https://github.com/pinellolab/stormi/commit/c888825a7932cf7181b436504677a21b8d1b5c63))

### Bug Fixes

* **AmortizedNormal:** Ensure compatibility with models that do not have path weights parameters. ([7594f24](https://github.com/pinellolab/stormi/commit/7594f24b16be4033012a19fff5121a2a9fc922a4))
* **AmortizedNormal:** Fix treatement of random seeds for initialization. ([ff52df9](https://github.com/pinellolab/stormi/commit/ff52df9e564558bf587dee4bf562fdd6ab7c6807))
* **AmortizedNormal:** Made JIT compatible warmup training. ([b7cc1c0](https://github.com/pinellolab/stormi/commit/b7cc1c0e1002c735f25bbce92a0fab2e0725cb06))
* **preprocessing:** additional Motifs from Scenic+ Database ([66584ff](https://github.com/pinellolab/stormi/commit/66584ffdff1c11f360c883e7963499aad94fa1af))
* **RNA_1layer:** Fixes to time prior that ensures proper application of T_scaling parameter and compatibility for cases with no prior time knowledge. ([131d27c](https://github.com/pinellolab/stormi/commit/131d27cede76e57a1bb9814fccd3b9c62ef7b0ca))
* **RNA_1layer:** Precompute one-hot encoded batch identity for jit training compatibility. ([947b97e](https://github.com/pinellolab/stormi/commit/947b97e79559c58fd333bf88bdf871081fd1ed2a))
* **RNA_2layers_MultiplePaths_SDE.py:** Fix treatement of random seeds. ([1991b06](https://github.com/pinellolab/stormi/commit/1991b067048b23b601c39fbe53b2f0ad50b22a76))
* **RNA_2layers_MultiplePaths_SDE:** Sample epsilon in plate ([9caf8b1](https://github.com/pinellolab/stormi/commit/9caf8b11680a91734066e477fc9d49190107930d))
* **train:** Fixed the issue that training with full batch size and AutoNormal guide was failing, because cells were randomly reshuffled each epoch. ([736f3c0](https://github.com/pinellolab/stormi/commit/736f3c039468486017dad2a5f3c068a6c00ec8d2))
