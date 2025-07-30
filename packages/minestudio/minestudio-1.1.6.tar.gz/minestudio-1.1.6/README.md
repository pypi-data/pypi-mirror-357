<!--
 * @Date: 2024-11-30 13:20:04
 * @LastEditors: caishaofei-mus1 1744260356@qq.com
 * @LastEditTime: 2025-05-28 13:06:53
 * @FilePath: /MineStudio/README.md
-->

<div align="center">
<img src="./docs/source/_static/banner.png" width="60%" alt="MineStudio" />
</div>

<hr>

<div align="center">
	<a href="https://craftjarvis.github.io/"><img alt="Homepage" src="https://img.shields.io/badge/%20CraftJarvis-HomePage-ffc107?color=blue&logoColor=white" style="display: inline-block; vertical-align: middle;"/></a>
	<a href="https://huggingface.co/CraftJarvis""><img alt="Hugging Face" src="https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-CraftJarvis-ffc107?color=3b65ab&logoColor=white" style="display: inline-block; vertical-align: middle;"/></a>
	<a href="https://github.com/CraftJarvis/MineStudio/blob/master/LICENSE"><img src="https://img.shields.io/badge/Code License-MIT-blue"/></a>
</div>
<div align="center">	
	<a href="https://arxiv.org/abs/2412.18293"><img src="https://img.shields.io/badge/arXiv-2412.18293-b31b1b.svg"></a>
	<a href="https://craftjarvis.github.io/MineStudio/"><img src="https://img.shields.io/badge/Doc-Sphinx-yellow"/></a>
    	<a href="https://pypi.org/project/minestudio/"><img src="https://img.shields.io/pypi/v/minestudio.svg"/></a>
	<a href="https://huggingface.co/CraftJarvis"><img src="https://img.shields.io/badge/Dataset-Released-orange"/></a>
	<a href="https://github.com/CraftJarvis/MineStudio/tree/master/minestudio/tutorials"><img alt="Static Badge" src="https://img.shields.io/badge/Tutorials-easy-brightgreen"></a>
	<a href="https://github.com/CraftJarvis/MineStudio"><img src="https://visitor-badge.laobi.icu/badge?page_id=CraftJarvis.MineStudio"/></a>
	<a href="https://github.com/CraftJarvis/MineStudio"><img src="https://img.shields.io/github/stars/CraftJarvis/MineStudio"/></a>
</div>

## Overview

<div align="center">
<img src="./docs/source/_static/workflow.png" width="" alt="Workflow" />
</div>

MineStudio contains a series of tools and APIs that can help you quickly develop Minecraft AI agents:
- [Simulator](https://craftjarvis.github.io/MineStudio/simulator/index.html): Easily customizable Minecraft simulator based on [MineRL](https://github.com/minerllabs/minerl).
- [Data](https://craftjarvis.github.io/MineStudio/data/index.html): A trajectory data structure for efficiently storing and retrieving arbitray trajectory segment.
- [Models](https://craftjarvis.github.io/MineStudio/models/index.html): A template for Minecraft policy model and a gallery of baseline models.
- [Offline Training](https://craftjarvis.github.io/MineStudio/offline/index.html): A straightforward pipeline for pre-training Minecraft agents with offline data.
- [Online Training](https://craftjarvis.github.io/MineStudio/online/index.html): Efficient RL implementation supporting memory-based policies and simulator crash recovery.
- [Inference](https://craftjarvis.github.io/MineStudio/inference/index.html): Pallarelized and distributed inference framework based on [Ray](https://docs.ray.io/en/latest/index.html).
- [Benchmark](https://craftjarvis.github.io/MineStudio/benchmark/index.html): Automating and batch-testing of diverse Minecraft tasks.

**This repository is under development.** We welcome any contributions and suggestions.

## News

- 2025/05/28 - We have released a big update of MineStudio (v1.1.4) with the following changes:
  - Refactored the [data](https://craftjarvis.github.io/MineStudio/data/index.html) component to support more flexible data loading and processing, all the trajectory modals are now decoupled. Users are able to [customize](https://craftjarvis.github.io/MineStudio/data/callbacks.html) their own data processing methods. 
  - Added detailed code comments and docstrings to all the modules, making it easier to understand and use the code.
  - Improved the documentation with more [examples](https://github.com/CraftJarvis/MineStudio/tree/master/tests), [tutorials](https://github.com/CraftJarvis/MineStudio/tree/master/minestudio/tutorials), and a new [API](https://craftjarvis.github.io/MineStudio/api/index.html) reference section.

## Installation

For a more detailed installation guide, please refer to the [documentation](https://craftjarvis.github.io/MineStudio/overview/installation.html).

MineStudio requires Python 3.10 or later. We recommend using conda to maintain an environment on Linux systems. JDK 8 is also required for running the Minecraft simulator.

```bash
conda create -n minestudio python=3.10 -y
conda activate minestudio
conda install --channel=conda-forge openjdk=8 -y
```

MineStudio is available on PyPI. You can install it via pip.
```bash
pip install MineStudio
```
To install MineStudio from source, you can run the following command:
```bash
pip install git+https://github.com/CraftJarvis/MineStudio.git
```

[**Important**] Minecraft simulator requires rendering tools. For users with nvidia graphics cards, we recommend installing **VirtualGL**. For other users, we recommend using **Xvfb**, which supports CPU rendering but is slightly slower. Refer to the [documentation](https://craftjarvis.github.io/MineStudio/overview/installation.html#install-the-rendering-tool) for installation commands.

After the installation, you can run the following command to check if the installation is successful:
```bash
python -m minestudio.simulator.entry # using Xvfb
MINESTUDIO_GPU_RENDER=1 python -m minestudio.simulator.entry # using VirtualGL
```

### Docker

We provide a Docker image for users who want to run MineStudio in a container. The Dockerfile is available in the `assets` directory. You can build and run the image by running the following command:
```bash
cd assets
docker build --platform=linux/amd64 -t minestudio .
docker run -it minestudio
```

## Datasets on 🤗 Hugging Face

We converted the [Contractor Data](https://github.com/openai/Video-Pre-Training?tab=readme-ov-file#contractor-demonstrations) the OpenAI VPT project provided to our trajectory structure and released them to the Hugging Face. (The old dataset is only available in v1.0.6 and earlier versions. From v1.1.0, we have changed the dataset structure to support more flexible data loading and processing.)

- [CraftJarvis/minestudio-data-6xx](https://huggingface.co/datasets/CraftJarvis/minestudio-data-6xx-v110)
- [CraftJarvis/minestudio-data-7xx](https://huggingface.co/datasets/CraftJarvis/minestudio-data-7xx-v110)
- [CraftJarvis/minestudio-data-8xx](https://huggingface.co/datasets/CraftJarvis/minestudio-data-8xx-v110)
- [CraftJarvis/minestudio-data-9xx](https://huggingface.co/datasets/CraftJarvis/minestudio-data-9xx-v110)
- [CraftJarvis/minestudio-data-10xx](https://huggingface.co/datasets/CraftJarvis/minestudio-data-10xx-v110)

```python
from minestudio.data import RawDataset
from minestudio.data.minecraft.callbacks import ImageKernelCallback, ActionKernelCallback

dataset = RawDataset(
    dataset_dirs=['6xx', '7xx', '8xx', '9xx', '10xx'],  # Specify the dataset directories
    modal_kernel_callbacks=[
        ImageKernelCallback(frame_width=224, frame_height=224, enable_video_aug=False), 
        ActionKernelCallback(enable_prev_action=True, win_bias=1, read_bias=-1),
    ],
    win_len=128, 
    split_ratio=0.9,
    shuffle_episodes=True,
)
item = dataset[0]
print(item.keys())
```


## Models on 🤗 Hugging Face

We have pushed all the checkpoints to 🤗 Hugging Face, it is convenient to load the policy model. 

```python
from minestudio.simulator import MinecraftSim
from minestudio.simulator.callbacks import RecordCallback
from minestudio.models import VPTPolicy

policy = VPTPolicy.from_pretrained("CraftJarvis/MineStudio_VPT.rl_from_early_game_2x").to("cuda")
policy.eval()

env = MinecraftSim(
    obs_size=(128, 128), 
    callbacks=[RecordCallback(record_path="./output", fps=30, frame_type="pov")]
)
memory = None
obs, info = env.reset()
for i in range(1200):
    action, memory = policy.get_action(obs, memory, input_shape='*')
    obs, reward, terminated, truncated, info = env.step(action)
env.close()
```

Here is the checkpoint list:
- [CraftJarvis/MineStudio_VPT.foundation_model_1x](https://huggingface.co/CraftJarvis/MineStudio_VPT.foundation_model_1x), trained by [OpenAI](https://github.com/openai/Video-Pre-Training)
- [CraftJarvis/MineStudio_VPT.foundation_model_2x](https://huggingface.co/CraftJarvis/MineStudio_VPT.foundation_model_2x), trained by [OpenAI](https://github.com/openai/Video-Pre-Training)
- [CraftJarvis/MineStudio_VPT.foundation_model_3x](https://huggingface.co/CraftJarvis/MineStudio_VPT.foundation_model_3x), trained by [OpenAI](https://github.com/openai/Video-Pre-Training)
- [CraftJarvis/MineStudio_VPT.bc_early_game_2x](https://huggingface.co/CraftJarvis/MineStudio_VPT.bc_early_game_2x), trained by [OpenAI](https://github.com/openai/Video-Pre-Training)
- [CraftJarvis/MineStudio_VPT.rl_from_house_2x](https://huggingface.co/CraftJarvis/MineStudio_VPT.rl_from_house_2x), trained by [OpenAI](https://github.com/openai/Video-Pre-Training)
- [CraftJarvis/MineStudio_VPT.rl_from_early_game_2x](https://huggingface.co/CraftJarvis/MineStudio_VPT.rl_from_early_game_2x), trained by [OpenAI](https://github.com/openai/Video-Pre-Training)
- [CraftJarvis/MineStudio_VPT.bc_house_3x](https://huggingface.co/CraftJarvis/MineStudio_VPT.bc_house_3x), trained by [OpenAI](https://github.com/openai/Video-Pre-Training)
- [CraftJarvis/MineStudio_VPT.bc_early_game_3x](https://huggingface.co/CraftJarvis/MineStudio_VPT.bc_early_game_3x), trained by [OpenAI](https://github.com/openai/Video-Pre-Training)
- [CraftJarvis/MineStudio_VPT.rl_for_shoot_animals_2x](https://huggingface.co/CraftJarvis/MineStudio_VPT.rl_for_shoot_animals_2x), trained by [CraftJarvis](https://craftjarvis.github.io/)
- [CraftJarvis/MineStudio_VPT.rl_for_build_portal_2x](https://huggingface.co/CraftJarvis/MineStudio_VPT.rl_for_build_portal_2x), trained by [CraftJarvis](https://craftjarvis.github.io/)
- [CraftJarvis/MineStudio_GROOT.18w_EMA](https://huggingface.co/CraftJarvis/MineStudio_GROOT.18w_EMA), trained by [CraftJarvis](https://craftjarvis.github.io/)
- [CraftJarvis/MineStudio_STEVE-1.official](https://huggingface.co/CraftJarvis/MineStudio_STEVE-1.official), trained by [STEVE-1](https://github.com/Shalev-Lifshitz/STEVE-1)
- [CraftJarvis/MineStudio_ROCKET-1.12w_EMA](https://huggingface.co/CraftJarvis/MineStudio_ROCKET-1.12w_EMA), trained by [CraftJarvis](https://craftjarvis.github.io/)
- [CraftJarvis/MineStudio_ROCKET-2-1x-22w](https://huggingface.co/phython96/ROCKET-2-1x-22w), trained by [CraftJarvis](https://craftjarvis.github.io/)
- [CraftJarvis/MineStudio_ROCKET-2-1.5x-17w](https://huggingface.co/phython96/ROCKET-2-1.5x-17w), trained by [CraftJarvis](https://craftjarvis.github.io/)


## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=CraftJarvis/MineStudio&type=Date)](https://www.star-history.com/#CraftJarvis/MineStudio&Date)

## Acknowledgement

The simulation environment is built upon [MineRL](https://github.com/minerllabs/minerl) and [Project Malmo](https://github.com/microsoft/malmo).
We also refer to [Ray](https://docs.ray.io/en/latest/index.html), [PyTorch Lightning](https://pytorch-lightning.readthedocs.io/en/latest/) for distributed training and inference.
Thanks for their great work.

## Citation

```bibtex
@inproceedings{MineStudio,
  title={MineStudio: A Streamlined Package for Minecraft AI Agent Development},
  author={Shaofei Cai and Zhancun Mu and Kaichen He and Bowei Zhang and Xinyue Zheng and Anji Liu and Yitao Liang},
  year={2024},
  url={https://api.semanticscholar.org/CorpusID:274992448}
}
```
