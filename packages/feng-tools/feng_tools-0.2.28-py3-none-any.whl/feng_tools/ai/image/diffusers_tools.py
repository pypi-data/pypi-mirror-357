"""
pip install --upgrade diffusers[torch]
pip install transformers

# 安装cuda版本
# 检查电脑是否支持cuda
nvidia-smi
# cuda版本
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128
# 如果没有 NVIDIA GPU，使用 CPU 版本：
pip3 install torch torchvision torchaudio
"""
import os
import traceback
import typing

import torch
from PIL.Image import Image
from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler


class DiffusersTools:
    def __init__(self, model_file:str, device:typing.Literal['cuda','cpu']=None,
                 safety_checker=None, feature_extractor=None):
        self.model_file = model_file
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.safety_checker=safety_checker
        self.feature_extractor=feature_extractor
        self.pipeline = None

    def load_model(self):
        """加载模型"""
        print(f"正在加载模型到 {self.device}...")
        torch_dtype = torch.float16 if self.device == "cuda" else torch.float32  # CPU 上使用 float32 更稳定
        # 加载模型
        self.pipeline = StableDiffusionPipeline.from_single_file(
            self.model_file,
            use_safetensors=self.model_file.endswith('.safetensors'),
            use_onnx=self.model_file.endswith('.onnx') or self.model_file.endswith('.pd'),
            torch_dtype=torch_dtype,
            safety_checker=self.safety_checker,
            feature_extractor=self.feature_extractor,
        )
        # 动态编译加速（PyTorch 2.0+）
        torch.compile(self.pipeline.unet)
        # 使用更快的调度器
        self.pipeline.scheduler = DPMSolverMultistepScheduler.from_config(self.pipeline.scheduler.config)
        # 3. 应用优化
        if self.device == "cuda":
            # 启用 xformers（需单独安装）
            try:
                self.pipeline.enable_xformers_memory_efficient_attention()
            except Exception as e:
                print("xformers not available, skipping")
        else:
            # 自动管理内存
            self.pipeline.enable_model_cpu_offload()
        # 将模型移动到指定设备
        self.pipeline = self.pipeline.to(self.device)
        print("模型加载完成")
        return self.pipeline


    def generate_image(self, prompt, negative_prompt=None, steps:int=20,
                       cfg_scale:float=7.5,
                       batch_size:int=1, seed=None) -> list[Image]:
        """
        生成图像
        Args:
            prompt: 提示词
            negative_prompt: 负面提示词
            steps: 推理步数
            cfg_scale: 引导系数
            batch_size: 每个提示词生成的图像数量
            seed: 随机种子

        Returns:
            生成的图像列表
        """
        if self.pipeline is None:
            self.load_model()

        # 设置随机种子
        if seed is not None:
            generator = torch.Generator(device=self.device).manual_seed(seed)
        else:
            generator = None

        # 生成图像
        with torch.autocast("cuda") if self.device == "cuda" else torch.no_grad():
            result = self.pipeline(
                prompt=prompt,
                negative_prompt=negative_prompt,
                num_inference_steps=steps,
                guidance_scale=cfg_scale,
                num_images_per_prompt=batch_size,
                generator=generator
            )
        return result.images

    @classmethod
    def save_image(cls, image:Image, save_file:str):
        """
        保存图像
        Args:
            image: PIL 图像对象
            save_file: 保持的文件
        Returns:
            保存的文件路径
        """
        os.makedirs(os.path.dirname(save_file), exist_ok=True)
        image.save(save_file)
        print(f"图像已保存到: {save_file}")
        return save_file

    @classmethod

    def show_image(cls, image):
        """显示图像"""
        try:
            image.show()
        except Exception as e:
            print(f"无法显示图像: {e}")
            traceback.print_exc()

if __name__ == '__main__':
    model_path = r'D:\models\ai_models\stable-diffusion-v1-5\v1-5-pruned-emaonly.safetensors'
    sd_tool = DiffusersTools(model_file=model_path)
    prompt = "a beautiful landscape with mountains and a lake"
    images = sd_tool.generate_image(prompt, batch_size=10)
    for i,tmp_img in enumerate(images):
        sd_tool.save_image(tmp_img, f'images/{i}.png')