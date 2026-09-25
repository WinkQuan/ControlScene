# ControlScene: Controllable Text-to-3D Scene Generation via Structured Layout Priors


## Datasets
<b>LayoutVerse-20K</b> : coming soon . 


## Installation && Running
Python version 3.8.10 is required.
1. Clone this repository.

2. Download the packages we used for runing.
'''bash
cd PanFusion
conda env create -f environment_strict.yaml
conda activate panfusion
cd ../PanoSpaceDreamer
pip install peft diffusers scipy numpy imageio[ffmpeg] opencv-python Pillow open3d torch==2.0.1  torchvision==0.15.2 gradio omegaconf
# ZoeDepth
pip install timm==0.6.7
# Gaussian splatting
pip install plyfile==0.8.1

cd submodules/depth-diff-gaussian-rasterization-min
# sudo apt-get install libglm-dev # may be required for the compilation.
python setup.py install
cd ../simple-knn
python setup.py install
cd ../..
'''

after that,you need to pip install the follow packages:
diffusers==0.26.0
accelerate
xformers
triton
transformers
realesrgan==0.3.0
py360convert


3. Download the checkpoint
Please download the checkpoints of PanFusion from the following link and move them to the directory logs/4142dlo4/checkpoints:
https://monashuni-my.sharepoint.com/:u:/g/personal/cheng_zhang_monash_edu/EeTrujeSOgdHh7vWsjXuMPAB8JtTaXS1uR8sp0y1kwQ4NQ?e=cI5jec

4. Run the code
You can adjust the test configuration by modifying the parameters in the config.json file. In this file, modify the "text" field to point to the file path that contains a single test prompt.
Next, run control.py. It should be noted that you need to replace the following information according to the actual situation:
--Replace the API address.
--Update the port number and IP address in the settings.py file required for communication. If you are running it on the local machine, please modify the configuration of the Client class in control.py.
If you plan to conduct remote communication, you need to deploy server_generate.py on the server side.

The server uses Tencent Cloud for translation. Create a local `.env` file using
`.env.example` as a template, then fill in `TENCENTCLOUD_SECRET_ID` and
`TENCENTCLOUD_SECRET_KEY`. Load these variables before starting the server from
the repository root (Bash):

```bash
set -a
. ./.env
set +a
python server_generate.py
```

You can also supply these environment variables through your deployment system.
The server reads the environment; it does not load `.env` automatically. Local
`.env` files are ignored by Git. Never put real credentials in `.env.example` or
source code.

If you do not need the refinement of the LLM, you can directly run main.py using the following command:
'''bash
WANDB_MODE=offline WANDB_RUN_ID=4142dlo4 python main.py predict --data=Matterport3D --model=PanFusion --ckpt_path=last
'''

5. Run in batches
If you want to perform batch testing on multiple prompts, list all the test prompts and save them to the data/prompt.txt file. Then, modify the content of the files in the data/Matterport3D/mp3d_skybox/e9zR4mvMWw7/blip3_stitched directory to test.txt.
After completing these steps, you can run the following command to execute the batch test:
'''
python run.py
'''

The running results of all tests will be saved in the directory logs/4142dlo4/predict. You can view and analyze the output files in this directory.